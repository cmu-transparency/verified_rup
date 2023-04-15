__version__ = '1.0.0'

import os
import sys
import ctypes

basedir = os.path.abspath(os.path.dirname(__file__))
checker = ctypes.cdll.LoadLibrary(os.path.join(basedir, "checker.so"))

str_arr = (ctypes.c_char_p * (len(sys.argv)+1))()
str_arr[:] = [i.encode("utf-8") for i in sys.argv] + [ctypes.c_char_p(0)]
checker.do_startup(str_arr)

from verified_rup.wrappers import check_from_strings, check_from_files