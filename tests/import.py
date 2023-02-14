# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import logging

# enable debug logging
logging.basicConfig(level=logging.DEBUG)


def test():
    import rpm

    # sanity check
    print("RPM conf dir:", rpm.expandMacro("%getconfdir"))


if __name__ == "__main__":
    test()
