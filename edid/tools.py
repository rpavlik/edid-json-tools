# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Defines tools for printing and formatting EDID information."""


import collections


def DictFilter(alist, bits):
  """Translates bits from EDID into a list of strings.

  Args:
    alist: A list of tuples, with the first being a number and second a string.
    bits: The bits from EDID that indicate whether each string is supported by
        this EDID or not.

  Returns:
    A dict of strings and bools.
  """
  d = collections.OrderedDict()
  for x, s in alist:
    d[s] = bool(bits & x)
  return d


def ListTrueOnly(adict):
  """Returns a list of strings for which their values were True in the dict.

  Args:
    adict: The original dictionary, with string keys and boolean values.

  Returns:
    A list of strings for which the boolean values were True in the dictionary.
  """
  return [x for x in adict if adict[x]]
