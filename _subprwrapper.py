"""
This module is a wrapper for subprocess to support logging

"""

import logging
import subprocess

logger = logging.getLogger('tpcc.wrapper')
logger.setLevel(logging.DEBUG)


def run(command: list, *args, **kwargs):
    logger.info(" ".join(command))
    logger.debug("run({}, {}, {})".format(command, args, kwargs))
    return subprocess.run(command, *args, **kwargs)

