#!/bin/bash

# fail early
set -e


### test import in virtualenvs

pushd /rpm-shim
tox
popd


### test import on local system

PYTHON=python3
PLATFORM_PYTHON=/usr/libexec/platform-python
if [ ! -x "${PYTHON}" -a -x "${PLATFORM_PYTHON}" ]; then
    # fallback to platform-python
    PYTHON="${PLATFORM_PYTHON}"
fi

${PYTHON} -m build --wheel /rpm-shim
# failure to install is most likely caused by existing RPM bindings, consider it a success
${PYTHON} -m pip install /rpm-shim/dist/*.whl || true
${PYTHON} /rpm-shim/tests/import.py
${PYTHON} -m pip check
