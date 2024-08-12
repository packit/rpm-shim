# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

"""
RPM shim module for use in virtualenvs
"""

import importlib
import json
import logging
import platform
import subprocess
import sys
from pathlib import Path
from typing import List

PROJECT_NAME = "rpm-shim"
MODULE_NAME = "rpm"

logger = logging.getLogger(PROJECT_NAME)


class ShimAlreadyInitializingError(Exception):
    pass


def get_system_sitepackages() -> List[str]:
    """
    Gets a list of sitepackages directories of system Python interpreter(s).

    Returns:
        List of paths.
    """

    def get_sitepackages(interpreter):
        command = [
            interpreter,
            "-c",
            "import json, site; print(json.dumps(site.getsitepackages()))",
        ]
        output = subprocess.check_output(command)
        return json.loads(output.decode())

    majorver, minorver, _ = platform.python_version_tuple()
    # try platform-python first (it could be the only interpreter present on the system)
    interpreters = [
        "/usr/libexec/platform-python",
        f"/usr/bin/python{majorver}",
        f"/usr/bin/python{majorver}.{minorver}",
    ]
    result = []
    for interpreter in interpreters:
        if not Path(interpreter).is_file():
            continue
        sitepackages = get_sitepackages(interpreter)
        formatted_list = "\n".join(sitepackages)
        logger.debug(f"Collected sitepackages for {interpreter}:\n{formatted_list}")
        result.extend(sitepackages)
    return result


def try_path(path: str) -> bool:
    """
    Tries to load system RPM module from the specified path.

    Returns:
        True if successful, False otherwise.
    """
    if not (Path(path) / MODULE_NAME).is_dir():
        return False
    sys.path.insert(0, path)
    try:
        importlib.reload(sys.modules[__name__])
        # sanity check
        confdir = sys.modules[__name__].expandMacro("%getconfdir")
        return Path(confdir).is_dir()
    finally:
        del sys.path[0]
    return False


def initialize() -> None:
    """
    Initializes the shim. Tries to load system RPM module and replace itself with it.
    """
    for path in get_system_sitepackages():
        logger.debug(f"Trying {path}")
        try:
            if try_path(path):
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
