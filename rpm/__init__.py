# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

"""
RPM shim module for use in virtualenvs
"""

import importlib
import importlib.util
import json
import logging
import platform
import pprint
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict, List

PROJECT_NAME = "rpm-shim"
MODULE_NAME = "rpm"

logger = logging.getLogger(PROJECT_NAME)


class ShimAlreadyInitializingError(Exception):
    pass


def get_system_sitepackages_and_suffixes() -> List[Dict[str, List[str]]]:
    """
    Gets a list of sitepackages directories of system Python interpreter(s).

    Returns:
        List of paths.
    """

    def get_sitepackages_and_suffixes(interpreter):
        script = textwrap.dedent(
            """
            import json
            import site

            try:
                import importlib.machinery
            except ImportError:
                suffixes = []
            else:
                suffixes = importlib.machinery.EXTENSION_SUFFIXES
            print(
                json.dumps(
                    {
                        "sitepackages": site.getsitepackages(),
                        "suffixes": suffixes,
                    }
                )
            )
            """
        )
        output = subprocess.check_output([interpreter], input=script.encode())
        return json.loads(output.decode())

    majorver, minorver, _ = platform.python_version_tuple()
    # try platform-python first (it could be the only interpreter present on the system)
    interpreters = [
        "/usr/libexec/platform-python",
        f"/usr/bin/python{majorver}.{minorver}",
        f"/usr/bin/python{majorver}",
    ]
    result = []
    for interpreter in interpreters:
        if not Path(interpreter).is_file():
            continue
        sitepackages_and_suffixes = get_sitepackages_and_suffixes(interpreter)
        logger.debug(
            f"Collected sitepackages and extension suffixes for {interpreter}:\n"
            + pprint.pformat(sitepackages_and_suffixes)
        )
        result.append(sitepackages_and_suffixes)
    return result


def try_path(path: str, suffixes: List[str]) -> bool:
    """
    Tries to load system RPM module from the specified path.

    Returns:
        True if successful, False otherwise.
    """
    module_path = Path(path) / MODULE_NAME
    if not module_path.is_dir():
        return False
    sys.path.insert(0, path)
    try:
        reload_module(module_path, suffixes)
        # sanity check
        confdir = sys.modules[__name__].expandMacro("%getconfdir")
        return Path(confdir).is_dir()
    finally:
        del sys.path[0]
    return False


def reload_module(path: Path, suffixes: List[str]) -> None:
    """
    Reloads the `rpm` module. In case some of the required binary submodules fail to import,
    tries to import them directly by path using valid extension suffixes.

    Args:
        path: Absolute path to the `rpm` module.
        suffixes: List of extension suffixes valid for the Python interpreter associated
                  with the path.
    """
    attempted_modules = []
    while True:
        try:
            importlib.reload(sys.modules[__name__])
        except ModuleNotFoundError as e:
            if e.name is None:
                raise
            if e.name in attempted_modules:
                logger.debug(f"Already tried {e.name} in {path}, giving up")
                raise
            attempted_modules.append(e.name)
            logger.debug(
                f"Module {e.name} not found in {path}, "
                "looking for alternative filenames trying valid extension suffixes"
            )
            try_import_binary_extension(path, e.name, suffixes)
        else:
            logger.debug(f"Reloaded {__name__}")
            return


def try_import_binary_extension(path: Path, module: str, suffixes: List[str]) -> bool:
    """
    Tries to find and import a binary extension in the specified path based on name
    and valid extension suffixes.

    Args:
        path: Path to the module, e.g. /usr/lib64/python3.9/site-packages/rpm/
        module: Name of the module to import, e.g. `rpm._rpm`
        suffixes: List of extension suffixes to check for
                  (see `importlib.machinery.EXTENSION_SUFFIXES`).

    Returns:
        True if the module was loaded, False otherwise.
    """
    # get the submodule module name, e.g. just '_rpm' from 'rpm._rpm'
    submodule = module.rpartition(".")[-1]
    for suffix in suffixes:
        # a file named {submodule}{suffix} may exist in {path}, e.g.:
        #
        # /usr/lib64/python3.9/site-packages/rpm/_rpm.cpython-39-x86_64-linux-gnu.so
        #
        # if so we'll try loading it as rpm._rpm
        so = path / f"{submodule}{suffix}"
        if not so.is_file():
            logger.debug(f"{so} isn't a file, ignoring")
            continue
        if load_module_by_path(module, so):
            return True
    else:
        logger.debug(
            f"No combination of {submodule} and valid suffixes found in {path}, giving up"
        )
        return False


def load_module_by_path(module_name: str, path: Path) -> bool:
    """
    Imports a Python module by path.

    Args:
        module_name: Name of the module to import.
        path: Absolute path to the module to import.

    Returns:
        True if the import succeeded, otherwise False.
    """
    logger.debug(f"Trying to load {module_name} from {path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        logger.debug(f"No spec for {module_name} in {path}")
        return False
    if spec.loader is None:
        logger.debug(f"No loader in spec for {module_name}")
        return False
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    logger.debug(f"Loaded {module_name} from {path}")
    return True


def initialize() -> None:
    """
    Initializes the shim. Tries to load system RPM module and replace itself with it.
    """
    for entry in get_system_sitepackages_and_suffixes():
        for path in entry["sitepackages"]:
            logger.debug(f"Trying {path}")
            try:
                if try_path(path, entry["suffixes"]):
                    logger.debug("Import successfull")
                    return
            except ShimAlreadyInitializingError:
                continue
            except Exception as e:
                logger.debug(f"Exception: {type(e)}: {e}")
                continue
    else:
        raise ImportError(
            "Failed to import system RPM module. "
            "Make sure RPM Python bindings are installed on your system."
        )


# avoid repeated initialization of the shim module
try:
    _shim_module_initializing_
except NameError:
    _shim_module_initializing_: bool = True
    initialize()
else:
    raise ShimAlreadyInitializingError
