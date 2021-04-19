# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause


"""Provides the StandardTiming class with methods for parsing info.

StandardTiming objects are found in bytes 26h-35h of the base EDID, as well as
in StandardTimingDescriptor objects.
"""

from typing import Final

from . import error
from .typing import ByteList, EdidVersion


def GetStandardTiming(edid, start_index, version):
  """Check if a potential standard timing block is valid.

  Args:
    edid: The EDID being parsed.
    start_index: The starting index of the standard timing block.
    version: The EDID version.

  Returns:
    A StandardTiming object, if valid; else, None.
  """
  if edid[start_index] == edid[start_index + 1] == 0x01:
    # All 0x01: unused
    return None
  return StandardTiming(edid, start_index, version)


# Used in base EDID as well as StandardTimingDescriptors
class StandardTiming(object):
  """Defines a single supported Standard Timing and its properties."""

  def __init__(self, edid: ByteList, start_index: int, version: EdidVersion):
    """Create a StandardTiming object.

    Args:
      edid: The list form of the EDID being analyzed.
      start_index: An integer indicating the start index of Standard Timing
          objects.
      version: The version of the EDID.
    """
    self._block: Final[ByteList] = edid[start_index:start_index + 2]
    self._version: Final[EdidVersion] = version

  def GetBlock(self) -> ByteList:
    """Fetch the data block of the StandardTiming object.

    Returns:
      A list of bytes that make up this StandardTiming object.
    """
    return self._block

  @property
  def x_resolution(self) -> int:
    """Fetch x resolution.

    Returns:
      An integer indicating x resolution.
    """
    return (self._block[0] + 31) * 8

  def CheckErrors(self, index=None) -> error.OptionalErrorList:
    """Check if the x resolution is faulty.

    Args:
      index: The integer index of this StandardTiming object.

    Returns:
      A list of error.Error objects.
    """
    st_index = '#%d' % index if index else ''

    if self._block[0] == 0:
      return [error.Error('Standard Timing object %s' % st_index,
                          'X resolution unset/invalid - possibly indicating '
                          '"unused" in a non-compliant way',
                          '256-2288 pixels',
                          'Value of 0 (converts to 248)')]
    else:
      return None

  @property
  def xy_pixel_ratio(self) -> str:
    """Fetch the xy pixel ratio.

    Returns:
      A string that indicates xy pixel ratio.
    """
    pixel_ratio = ''
    code = (self._block[1] >> 6) & 0x03
    if code == 0x0:
      pixel_ratio = '1:1' if self._version < '1.3' else '16:10'
    elif code == 0x1:
      pixel_ratio = '4:3'
    elif code == 0x2:
      pixel_ratio = '5:4'
    else:
      pixel_ratio = '16:9'

    return pixel_ratio

  @property
  def vertical_freq(self) -> int:
    """Fetch the vertical frequency.

    Actual frequency is 60 more than the value stored in the EDID.

    Returns:
      An integer indicating vertical frequency (in Hz).
    """
    return (self._block[1] & 0x3F) + 60
