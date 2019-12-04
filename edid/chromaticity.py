# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Provides the Chromaticity class with methods for parsing chromaticity info.

Chromaticity info is stored in bytes 19h-22h of the base EDID.
Chromaticity object processes the 10-bit CIE xy coordinates: RGBW.
"""


class Chromaticity(object):
  """Class for parsing chromaticity section of base EDID."""

  def __init__(self, edid):
    """Create a Chromaticity object.

    Args:
      edid: The edid (in list form).
    """
    self._edid = edid

  @property
  def red_x(self):
    """Fetch 10-bit CIE Red X coordinate.

    Returns:
      An integer representing the Red X coordinate.
    """
    return (self._edid[0x1B] << 2) + ((self._edid[0x19] >> 6) & 0x03)

  @property
  def red_y(self):
    """Fetch 10-bit CIE Red Y coordinate.

    Returns:
      An integer representing the Red Y coordinate.
    """
    return (self._edid[0x1C] << 2) + ((self._edid[0x19] >> 4) & 0x03)

  @property
  def grn_x(self):
    """Fetch 10-bit CIE Green X coordinate.

    Returns:
      An integer representing the Green X coordinate.
    """
    return (self._edid[0x1D] << 2) + ((self._edid[0x19] >> 2) & 0x03)

  @property
  def grn_y(self):
    """Fetch 10-bit CIE Green Y coordinate.

    Returns:
      An integer representing the Green Y coordinate.
    """
    return (self._edid[0x1E] << 2) + (self._edid[0x19] & 0x03)

  @property
  def blue_x(self):
    """Fetch 10-bit CIE Blue X coordinate.

    Returns:
      An integer representing the Blue X coordinate.
    """
    return (self._edid[0x1F] << 2) + ((self._edid[0x1A] >> 6) & 0x03)

  @property
  def blue_y(self):
    """Fetch 10-bit CIE Blue Y coordinate.

    Returns:
      An integer representing the Blue Y coordinate.
    """
    return (self._edid[0x20] << 2) + ((self._edid[0x1A] >> 4) & 0x03)

  @property
  def wht_x(self):
    """Fetch 10-bit CIE White X coordinate.

    Returns:
      An integer representing the White X coordinate.
    """
    return (self._edid[0x21] << 2) + ((self._edid[0x1A] >> 2) & 0x03)

  @property
  def wht_y(self):
    """Fetch 10-bit CIE White Y coordinate.

    Returns:
      An integer representing the White Y coordinate.
    """
    return (self._edid[0x22] << 2) + (self._edid[0x1A] & 0x03)
