from logging import Logger
from time import time

import sys


def time_function(function):

    def new_function(*args, ofile=sys.stdout, logger:Logger=None, **kwargs):
        start = time()
        value = function(*args, **kwargs)
        end = time()
        msg = f"Function {function.__name__} executed in {'%.2f' % (end-start)} seconds"
        print(msg, file=ofile)
        if logger != None:
            logger.info(msg)
        return value
    
    return new_function