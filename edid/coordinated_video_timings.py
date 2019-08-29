# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Provides the CoordinatedVideoTiming class with methods for parsing info.

CoordinatedVideoTiming info is stored in Video Timing Block extensions.
"""

from . import error
from . import tools


def GetCoordinatedVideoTiming(edid, start_index):
  """Returns a CoordinatedVideoTiming object if valid block exists.

  Args:
    edid: The list form of the EDID being parsed.
    start_index: The starting index of the CVT block, relative to base EDID.

  Returns:
    A CoordinatedVideoTiming object, if valid; or else None.
  """
  if not(edid[start_index] == edid[start_index + 1] == edid[start_index + 2]
         == 0x00):
    return CoordinatedVideoTiming(edid, start_index)
  else:
    return None


class CoordinatedVideoTiming(object):
  """Returns a CoordinatedVideoTiming object and its properties."""

  _ref_rates = [
      [0x10, '50Hz'],
      [0x08, '60Hz'],
      [0x04, '75Hz'],
      [0x02, '85Hz'],
      [0x01, '60Hz (reduced blanking)']
  ]

  def __init__(self, edid, start_index):
    """Creates a CoordinatedVideoTiming object.

    Args:
      edid: The edid (in list form).
      start_index: The starting index of the coordinated video timing block,
          relative to the base EDID.
    """
    self._block = edid[start_index:(start_index + 3)]

  def GetBlock(self):
    """Fetches the bytes that constitute the coordinated video timing block.

    Returns:
      The list of bytes of the coordinated video timing block.
    """
    return self._block

  @property
  def active_vertical_lines(self):
    """Fetches the number of active vertical lines.

    Returns:
      An integer indicating the number of active vertical lines.
    """
    val = ((self._block[1] & 0xF0) << 4) + self._block[0]
    return (val + 1) * 2

  @property
  def aspect_ratio(self):
    """Fetches the aspect ratio.

    Returns:
      A string indicating the aspect ratio.
    """
    ar = (self._block[1] >> 2) & 0x03
    asp_ratio = ''

    if ar == 0x00:
      asp_ratio = '4:3 AR'
    elif ar == 0x01:
      asp_ratio = '16:9 AR'
    elif ar == 0x02:
      asp_ratio = '16:10 AR'
    elif ar == 0x03:
      asp_ratio = '15:9 AR'

    return asp_ratio

  @property
  def preferred_vertical_rate(self):
    """Fetches the preferred refresh rate (byte 3).

    Returns:
      A string indicating the preferred refresh rate; the returned value should
      also be included in supported_vertical_rates.
    """
    pref_code = (self._block[2] >> 5) & 0x03  # Ranges 00-11 (0-3)
    supp_code = self._block[2] & 0x1F  # 5 bits long

    if pref_code == 0x01 and supp_code & 0x01:
      pref_code = 4
    return self._ref_rates[pref_code][1]

  @property
  def supported_vertical_rates(self):
    """Fetches the list of supported refresh rates.

    Returns:
      A dict of strings and booleans, each representing a refresh rate and
      whether it is supported.
    """
    supp_code = self._block[2] & 0x1F
    return tools.DictFilter(self._ref_rates, supp_code)

  def CheckErrors(self, index=None):
    """Checks for errors in the coordinated video timing block.

    Args:
      index: The index of the CoordinatedVideoTiming object within the EDID.

    Returns:
      An error.Error object specifying details, if there is one; else, None.
    """
    loc = 'Coordinated video timing block %s' % ('#%d' % index if index else '')
    errors = []

    # Check that preferred refresh rate is supported
    if self.preferred_vertical_rate not in self.supported_vertical_rates:
      errors.append(error.Error(loc, 'Preferred refresh rate not supported',
                                '%s supported' % self.preferred_vertical_rate,
                                'Supported: %s' %
                                self.supported_vertical_rates))

    # Check for reserved 0 bits
    if self._block[1] & 0x03:
      # Error: Bits 1-0 of byte 2 in CVT should be set to '00'
      errors.append(error.Error(loc, 'Bits 1-0 of byte 2 incorrectly set',
                                0x00, self._block[1] & 0x03))

    if self._block[2] & 0x80:
      # Error: Bit 7 of byte 3 in CVT should be set to '0'
      errors.append(error.Error(loc, 'Bit 7 of byte 3 incorrectly set', 0x00,
                                self._block[2] & 0x80))

    return errors
