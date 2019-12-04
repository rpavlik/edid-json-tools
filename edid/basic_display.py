# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Provides the BasicDisplay class with methods for parsing basic display info.

Basic display info is stored in bytes 14h-18h of the base EDID.
"""


class BasicDisplay(object):
  """Class for parsing basic display block info from base EDID."""

  def __init__(self, e, version):
    """Create a BasicDisplay object.

    Args:
      e: The edid (in list form).
      version: A string indicating the EDID version (e.g., '1.4').
    """
    self._edid = e
    self._version = version

  @property
  def video_input_type(self):
    """Check 20th (0x14) byte of EDID for digital or analog input.

    Part of video input definition in base EDID.
    0 denotes Analog; 1 denotes Digital.

    Returns:
      0 (Analog) or 1 (Digital).
    """
    return (self._edid[0x14] >> 7) & 0x01

  ######################################
  # FOR DIGITAL VIDEO SIGNAL INTERFACE #
  ######################################

  @property
  def color_bit_depth(self):
    """Fetch color bit depth.

    For digital video signal interface only (not applicable for analog).

    Returns:
      A string indicating the number of bits per primary color.
    """
    cbd = (self._edid[0x14] & 0x70) >> 4

    bits = 0

    if cbd == 0x00:
      return None
    elif cbd == 0x01:
      bits = 6
    elif cbd == 0x02:
      bits = 8
    elif cbd == 0x03:
      bits = 10
    elif cbd == 0x04:
      bits = 12
    elif cbd == 0x05:
      bits = 14
    elif cbd == 0x06:
      bits = 16
    elif cbd == 0x07:
      return 'Reserved (Do Not Use)'

    return '%d Bits per Primary Color' % bits

  @property
  def digital_supports(self):
    """Check digital supports.

    For digital video signal interface only (not applicable for analog).

    Returns:
      A string indicating the support.
    """
    supp = self._edid[0x14] & 0x0F

    if supp == 0x00:
      return None
    elif supp == 0x01:
      return 'DVI'
    elif supp == 0x02:
      return 'HDMI-a'
    elif supp == 0x03:
      return 'HDMI-b'
    elif supp == 0x04:
      return 'MDDI'
    elif supp == 0x05:
      return 'DisplayPort'
    else:
      return 'Reserved: Should not be used'

  #####################################
  # FOR ANALOG VIDEO SIGNAL INTERFACE #
  #####################################

  @property
  def signal_level(self):
    """Check video white and sync levels.

    For analog video signal interface only (not applicable for digital).
    Relative to blank.

    Returns:
      A string indicating video white and sync levels.
    """
    vid_input = (self._edid[0x14] >> 5) & 0x03

    if vid_input == 0x00:
      return '+0.7/-0.3 V'
    elif vid_input == 0x01:
      return '+0.714/-0.286 V'
    elif vid_input == 0x02:
      return '+1.0/-0.4 V'
    elif vid_input == 0x03:
      return '+0.7/0 V'

  @property
  def blank_black(self):
    """Check blank-to-black set up (pedestal) expected.

    For analog video signal interface only (not applicable for digital).

    Returns:
      A boolean that indicates whether blank-to-black is expected.
    """
    return self._edid[0x14] & 0x10 != 0

  @property
  def separate_sync(self):
    """Check if separate sync is supported (bit 3).

    For analog video signal interface only (not applicable for digital).

    Returns:
      A boolean that indicates whether separate sync is supported.
    """
    return self._edid[0x14] & 0x08 != 0

  @property
  def composite_sync(self):
    """Check if composite sync (on HSync) is supported (bit 2).

    For analog video signal interface only (not applicable for digital).

    Returns:
      A boolean that indicates whether composite sync is supported.
    """
    return self._edid[0x14] & 0x04 != 0

  @property
  def green_sync(self):
    """Check if green sync is supported (bit 1).

    For analog video signal interface only (not applicable for digital).

    Returns:
      A boolean that indicates whether green sync is supported.
    """
    return self._edid[0x14] & 0x02 != 0

  @property
  def vsync_pulse(self):
    """Check if VSync pulse serration is supported.

    Specifically, when composite or sync-on-green (bit 0).
    For analog video signal interface only (not applicable for digital).

    Returns:
      A boolean that indicates whether VSync pulse serration is supported.
    """
    return self._edid[0x14] & 0x01 != 0

  ########################
  # BOTH INTERFACE TYPES #
  ########################

  @property
  def horizontal_dim(self):
    """Check maximum horizontal dimensions.

    Returns:
      An integer that represents the maximum horizontal dimensions, or None.
    """
    if self._edid[0x16]:
      return self._edid[0x15]
    else:
      return None

  @property
  def vertical_dim(self):
    """Check maximum vertical dimensions.

    Returns:
      An integer that represents the maximum vertical dimensions, or None.
    """
    if self._edid[0x15]:
      return self._edid[0x16]
    else:
      return None

  @property
  def aspect_ratio_portrait(self):
    """Check for aspect ratio (portrait) if defined.

    Returns:
      A float indicating aspect ratio (portrait), or None.
    """
    if not self._edid[0x15] and self._edid[0x16]:
      aspect_ratio = 100.0 / (self._edid[0x16] + 99.0)
      return '%.2f : 1' % aspect_ratio
    else:
      return None

  @property
  def aspect_ratio_landscape(self):
    """Check for aspect ratio (landscape) if defined.

    Returns:
      A float indicating aspect ratio (landscape), or None.
    """
    if not self._edid[0x16] and self._edid[0x15]:
      aspect_ratio = (self._edid[0x15] + 99.0) / 100.0
      return '%.2f : 1' % aspect_ratio
    else:
      return None

  @property
  def display_gamma(self):
    """Check display gamma (byte 23).

    Data value in EDID = (gamma * 100) - 100.
    Gamma is in range 1.00-3.54.

    Returns:
      A float representing the display gamma.
    """
    return (self._edid[0x17] + 100) / 100.0

  # SUPPORTED FEATURES SECTION

  @property
  def dpm_standby(self):
    """Check if DPM standby is supported.

    Returns:
      A boolean that indicates whether DPM standby is supported.
    """
    return self._edid[0x18] & 0x80 != 0

  @property
  def dpm_suspend(self):
    """Check if DPM suspend is supported.

    Returns:
      A boolean that indicates whether DPM suspend is supported.
    """
    return self._edid[0x18] & 0x40 != 0

  @property
  def active_off(self):
    """Check if DPM active-off is supported (bit 5).

    Returns:
      A boolean that indicates whether DPM active-off is supported.
    """
    return self._edid[0x18] & 0x20 != 0

  @property
  def display_type(self):
    """Check color display type (bits 4-3).

    Returns:
      A string that indicates display type.
    """
    code = (self._edid[0x18] >> 3) & 0x03
    color_type = ''

    if self.video_input_type:  # Digital
      if code == 0x00:
        color_type = 'RGB 4:4:4'
      elif code == 0x01:
        color_type = 'RGB 4:4:4 + YCrCb 4:4:4'
      elif code == 0x02:
        color_type = 'RGB 4:4:4 + YCrCb 4:2:2'
      elif code == 0x03:
        color_type = 'RGB 4:4:4 + YCrCb 4:4:4 + YCrCb 4:2:2'
    else:  # Analog
      if code == 0x00:
        color_type = 'Monochrome/Grayscale'
      elif code == 0x01:
        color_type = 'RGB color'
      elif code == 0x02:
        color_type = 'Non-RGB color'
      elif code == 0x03:
        color_type = 'Undefined'
    return color_type

  @property
  def srgb_as_default(self):
    """Check if standard sRGB color space is supported.

    Returns:
      A boolean that indicates whether standard sRGB color space is supported.
    """
    return self._edid[0x18] & 0x04 != 0

  @property
  def native_preferred_timing_mode(self):
    """Check preferred timing mode (bit 1).

    Specifically, if it includes native timing pixel format and refresh rate.

    Returns:
      A boolean that indicates whether preferred timing mode includes native
      timing pixel format and refresh rate.
    """
    return self._edid[0x18] & 0x02 != 0

  @property
  def cont_freq_support(self):
    """Check if continuous frequency is supported.

    Returns:
      A boolean that indicates whether continuous frequency is supported.
    """
    return self._edid[0x18] & 0x01 != 0
