# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Defines tools for reading, printing, and formatting EDID information."""


import collections


def DictFilter(alist, bits):
  """Translate bits from EDID into a list of strings.

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
  """Return a list of strings for which their values were True in the dict.

  Args:
    adict: The original dictionary, with string keys and boolean values.

  Returns:
    A list of strings for which the boolean values were True in the dictionary.
  """
  return [x for x in adict if adict[x]]


def BytesFromFile(filename):
  """Read the EDID from binary blob form into list form.

  Args:
    filename: The name of the binary blob.

  Returns:
    The list of bytes that make up the EDID.
  """
  with open(filename, 'rb') as f:
    chunk = f.read()
    return [int(x) for x in bytes(chunk)]


def PrintHexData(data):
  """Print an array of values in hexadecimal form.

  Args:
    data: The data to be printed.
  """
  hex_rows = len(data) // 16

  print('\t\t 0 1  2 3  4 5  6 7  8 9  A B  C D  E F')

  for x in range(0, hex_rows):

    start = 0x10 * x
    row = '%02X%02X ' * 8 % tuple(data[start:(start + 16)])
    print('0x%04X:\t\t%s' % (x, row))
