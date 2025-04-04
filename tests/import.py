# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import logging

# enable debug logging
logging.basicConfig(level=logging.DEBUG)


def test():
    import rpm

    # sanity check
    print("RPM conf dir:", rpm.expandMacro("%getconfdir"))
    # the spec class should be present, but loading it fails if there is an ABI
    # mismatch between the current interpreter and the site packages from which
    # we loaded the module
    rpm.spec


if __name__ == "__main__":
    test()
