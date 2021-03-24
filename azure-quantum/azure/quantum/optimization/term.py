##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

from typing import List, Union, Optional
import numpy as np
import numpy.typing as npt

__all__ = ['Term']

numpy_integer_types = [np.byte, np.ubyte, np.short, np.ushort, np.intc, np.uintc,
                       np.int_, np.uint, np.longlong, np.ulonglong, np.int8, np.uint8,
                       np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64]

numpy_float_types = [np.float16, np.float32, np.float64, np.float_, np.half, np.single, np.double]

def _convert_if_numpy_type(param : npt.DTypeLike):
    # Attempt first a conversion to a supported type if parameter is a numpy float/int.
    if (type(param) in numpy_integer_types + numpy_float_types):
        return param.item()
    else:
        return param

class Term:

    def __init__(self, indices: List[int] = None, w: Optional[Union[int, float, npt.DTypeLike]] = None, c: Optional[Union[int, float]] = None):
        if(type(w) == None and type(c) == None):
            raise RuntimeError("Cost should be provided for each term.")

        if(type(w) != None and type(c) != None):
            raise RuntimeError("Cost has been specified multiple times. Please do not specify 'w' if using 'c'.")

        if(w != None):
            # Legacy support if 'w' is used to specify term.
            self.w = _convert_if_numpy_type(w)
            if(type(w) != int and type(w) != float):
                raise RuntimeError("w must be a float or int value, or a numpy value that can be converted to those.")
            else:
                self.c = w
        elif(c != None):
            # Current intended specification of term.
            self.c = _convert_if_numpy_type(c)
            if(type(c) != int and type(c) != float):
                raise RuntimeError("c must be a float or int value, or a numpy value that can be converted to those.")
            else:
                self.c = c

        self.ids = indices

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
