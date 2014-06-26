# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Defines tools for printing and formatting EDID information."""


def ListFilter(alist, bits):
  """Translates bits from EDID into a list of strings.

  Args:
    alist: A list of tuples, with the first being a number and second a string.
    bits: The bits from EDID that code for which strings to return.

  Returns:
    A list of strings.
  """
  return [s for x, s in alist if bits & x]
