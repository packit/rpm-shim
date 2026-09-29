#!/bin/bash

# fail early
set -e


### test import in virtualenvs

pushd /rpm-shim
tox
popd


### test import on local system

PYTHON="$(command -v python3 || true)"
if [ -z "${PYTHON}" ]; then
    for candidate in /usr/bin/python3.*; do
        case "${candidate}" in
            *-config) continue ;;
        esac
        if [ -x "${candidate}" ] && "${candidate}" -c 'pass' 2>/dev/null; then
            PYTHON="${candidate}"
            break
        fi
    done
fi

PLATFORM_PYTHON=/usr/libexec/platform-python
if [ -z "${PYTHON}" ] && [ -x "${PLATFORM_PYTHON}" ]; then
    # fallback to platform-python
    PYTHON="${PLATFORM_PYTHON}"
fi

if [ -z "${PYTHON}" ]; then
    echo "No Python interpreter found" >&2
    exit 1
fi

${PYTHON} -m build --wheel /rpm-shim
# failure to install is most likely caused by existing RPM bindings, consider it a success
${PYTHON} -m pip install /rpm-shim/dist/*.whl || true
${PYTHON} /rpm-shim/tests/import.py
${PYTHON} -m pip check
