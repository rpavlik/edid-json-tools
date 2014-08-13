# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Provides Descriptor class and related classes with methods for parsing info.

18-byte descriptors are found both in the base EDID and in extensions.
The various types of Descriptor all inherit the basic Descriptor object.
"""
import collections

import coordinated_video_timings as cvt_module
import error
import standard_timings
import tools


TYPE_PRODUCT_SERIAL_NUMBER = 'Display Product Serial Number'
TYPE_ALPHANUM_DATA_STRING = 'Alphanumeric Data String (ASCII)'
TYPE_DISPLAY_RANGE_LIMITS = 'Display Range Limits Descriptor'
TYPE_DISPLAY_PRODUCT_NAME = 'Display Product Name'
TYPE_COLOR_POINT_DATA = 'Color Point Data'
TYPE_STANDARD_TIMING = 'Standard Timing Identifiers'
TYPE_DISPLAY_COLOR_MANAGEMENT = 'Display Color Management (DCM) Data'
TYPE_CVT_TIMING = 'CVT 3 Byte Timing Codes'
TYPE_ESTABLISHED_TIMINGS_III = 'Established Timings III'
TYPE_RESERVED = 'Error: Reserved/undefined; do not use'
TYPE_DUMMY = 'Dummy descriptor'
TYPE_MANUFACTURER_SPECIFIED = 'Manufacturer Specified Display Descriptor'
TYPE_DETAILED_TIMING = 'Detailed Timing Descriptor'
SUBTYPE_DISPLAY_RANGE_DEFAULT = 'Default GTF supported'
SUBTYPE_DISPLAY_RANGE_LIMIT_ONLY = 'Range Limits Only - no additional info'
SUBTYPE_DISPLAY_RANGE_2ND_GTF = 'Secondary GTF supported - requires default too'
SUBTYPE_DISPLAY_RANGE_CVT = 'CVT supported'
SUBTYPE_DISPLAY_RANGE_UNKNOWN = 'Unknown'


def GetDescriptor(edid, start, version):
  """Fetches a descriptor object.

  Args:
    edid: The list of bytes that make up the EDID.
    start: The index in the edid at which the descriptor starts.
    version: The string indicating the version of the EDID.

  Returns:
    A descriptor object.
  """
  block = edid[start:start + 18]

  class_map = {
      0xFF: ProductSerialNumberDescriptor,
      0xFE: AlphanumDataStringDescriptor,
      0xFD: GetDisplayRangeDescriptor,
      0xFC: DisplayProductNameDescriptor,
      0xFB: ColorPointDescriptor,
      0xF9: DisplayColorDescriptor,
      0xF8: CoordinatedVideoTimingsDescriptor,
      0xF7: EstablishedTimingsIIIDescriptor,
      0x10: DummyDescriptor
  }

  if block[0] == block[1] == block[2] == 0x00:
    tag = block[3]
    if tag in class_map:
      return class_map[tag](block)
    elif tag == 0xFA:
      return StandardTimingDescriptor(block, version)
    elif tag >= 0x00 and tag <= 0x0F:
      return ManuSpecifiedDescriptor(block)
    else:  # tag >= 0x11 and tag <= 0xF6
      return ReservedDescriptor(block)

  else:  # Detailed timing descriptor
    return DetailedTimingDescriptor(block)


def GetDisplayRangeDescriptor(block):
  """Fetches some type of Display Range Descriptor.

  Args:
    block: The list of bytes that make up this descriptor.

  Returns:
    A Display Range Descriptor object.
  """
  support_flag = block[10]
  if support_flag == 0x00:
    return DisplayRangeDescriptor(block, SUBTYPE_DISPLAY_RANGE_DEFAULT)
  elif support_flag == 0x01:
    return DisplayRangeDescriptor(block, SUBTYPE_DISPLAY_RANGE_LIMIT_ONLY)
  elif support_flag == 0x02:
    return DisplayRangeGTF(block)
  elif support_flag == 0x04:
    return DisplayRangeCVT(block)
  else:
    return DisplayRangeDescriptor(block, SUBTYPE_DISPLAY_RANGE_UNKNOWN)


class Descriptor(object):
  """Defines a single descriptor and its properties."""

  def __init__(self, block, my_type):
    """Creates a Descriptor object.

    Args:
      block: A list of 18-bytes that make up the descriptor.
      my_type: A string that indicates what type of Descriptor this is.
    """
    self._block = block
    self._type = my_type

  @property
  def type(self):
    """Fetches the type of the descriptor.

    Returns:
      A string that indicates the type of the descriptor.
    """
    return self._type

  def GetBlock(self):
    """Fetches the data block.

    Returns:
      A list of bytes that make up this descriptor.
    """
    return self._block

  def CheckErrors(self, index=None):
    """Checks the validity of this descriptor.

    Args:
      index: The integer index of the descriptor being checked.

    Returns:
      A list of error.Error objects. The list is None or empty if no errors.
    """
    pass


class StringDescriptor(Descriptor):
  """Analyzes a String Descriptor."""

  def __init__(self, block, my_type):
    """Creates a StringDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
      my_type: A string that indicates this descriptor is a String Descriptor.
    """
    Descriptor.__init__(self, block, my_type)
    self._type = my_type

  @property
  def string(self):
    """Fetches the alphanumeric string.

    Returns:
      A string of alphanumeric characters that this descriptor encoded.
    """
    alphanum_data = ''

    for x in xrange(5, 18):
      if self._block[x] == 0x0A:
        break
      else:
        alphanum_data += chr(self._block[x])

    return alphanum_data

  def CheckErrors(self, index=None):
    """Checks the StringDescriptor for errors.

    Args:
      index: The integer index of the descriptor.

    Returns:
      A list of error.Error objects, or None.
    """
    if self._block[4] != 0x00:
      loc = '%s %s' % (self._type, '#%d' % index if index else '')
      return [error.Error(loc, 'Byte 5', 0x00, self._block[4])]
    else:
      return None


class ProductSerialNumberDescriptor(StringDescriptor):
  """Analyzes a Product Serial Number Descriptor."""

  def __init__(self, block):
    """Creates a ProductSerialNumberDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    StringDescriptor.__init__(self, block, TYPE_PRODUCT_SERIAL_NUMBER)


class AlphanumDataStringDescriptor(StringDescriptor):
  """Analyzes an Alphanumerical Data String Descriptor."""

  def __init__(self, block):
    """Creates an AlphanumDataStringDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    StringDescriptor.__init__(self, block, TYPE_ALPHANUM_DATA_STRING)


class DisplayProductNameDescriptor(StringDescriptor):
  """Analyzes a Display Product Name Descriptor."""

  def __init__(self, block):
    """Creates a DisplayProductNameDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    StringDescriptor.__init__(self, block, TYPE_DISPLAY_PRODUCT_NAME)


class DisplayRangeDescriptor(Descriptor):
  """Analyzes a Display Range Descriptor."""

  def __init__(self, block, subtype):
    """Creates a DisplayRangeDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
      subtype: A string that indicates the specific type of
          DisplayRangeDescriptor.
    """
    Descriptor.__init__(self, block, TYPE_DISPLAY_RANGE_LIMITS)
    self._subtype = subtype

  @property
  def subtype(self):
    """Fetches the subtype.

    Returns:
      A string specifying the subtype of the DisplayRangeDescriptor.
    """
    return self._subtype

  @property
  def max_vertical_rate_offset(self):
    """Fetches the maximum vertical rate offset.

    Returns:
      An integer specifying the maximum vertical rate offset (in Hz).
    """
    if self._block[4] & 0x02:
      return 255
    else:
      return 0

  @property
  def min_vertical_rate_offset(self):
    """Fetches the minimum vertical rate offset.

    Returns:
      An integer specifying the minimum vertical rate offset (in Hz).
    """
    if self._block[4] & 0x03 == 0x03:
      return 255
    else:
      return 0

  @property
  def max_horizontal_rate_offset(self):
    """Fetches the maximum horizontal rate offset.

    Returns:
      An integer specifying the maximum horizontal rate offset (in kHz).
    """
    if (self._block[4] & 0x0C) >> 2:
      return 255
    else:
      return 0

  @property
  def min_horizontal_rate_offset(self):
    """Fetches the minimum horizontal rate offset.

    Returns:
      An integer specifying the minimum horizontal rate offset (in kHz).
    """
    if (self._block[4] >> 2) & 0x03 == 0x03:
      return 255
    else:
      return 0

  @property
  def min_vertical_rate(self):
    """Fetches the minimum vertical rate.

    Returns:
      An integer specifying the minimum vertical rate (in Hz).
    """
    return self._block[5] + self.min_vertical_rate_offset

  @property
  def max_vertical_rate(self):
    """Fetches the maximum vertical rate.

    Returns:
      An integer specifying the maximum vertical rate (in Hz).
    """
    return self._block[6] + self.max_vertical_rate_offset

  @property
  def min_horizontal_rate(self):
    """Fetches the minimum horizontal rate.

    Returns:
      An integer specifying the minimum horizontal rate (in kHz).
    """
    return self._block[7] + self.min_horizontal_rate_offset

  @property
  def max_horizontal_rate(self):
    """Fetches the maximum horizontal rate.

    Returns:
      An integer specifying the maximum horizontal rate (in kHz).
    """
    return self._block[8] + self.max_horizontal_rate_offset

  @property
  def pixel_clock(self):
    """Fetches the pixel clock.

    Returns:
      An integer specifying the pixel clock (MHz).
    """
    return self._block[9] * 10

  def CheckErrors(self, index=None):
    """Checks for errors.

    Errors may include maximum values being less than minimum values, or
    invalid support flag values.

    Args:
      index: The integer index of this descriptor (1-4).

    Returns:
      A list of error.Error objects.
    """
    errors = []

    max_vert = self.max_vertical_rate
    min_vert = self.min_vertical_rate

    max_hor = self.max_horizontal_rate
    min_hor = self.min_horizontal_rate

    loc = '%s %s' % (self._type, '#%d' % index if index else '')

    if max_vert < min_vert:
      errors.append(error.Error(loc, 'Maximum vertical rate less than minimum',
                                'Max vert: %d\tMin vert: %d' % (max_vert,
                                                                min_vert)))

    if max_hor < min_hor:
      errors.append(error.Error(loc, 'Maximum horizontal rate less than '
                                'minimum', '', 'Max hor: %d\tMin hor: %d' %
                                (max_hor, min_hor)))

    if not self.pixel_clock:
      errors.append(error.Error(loc, 'Pixel clock value invalid', 'Non-zero',
                                self.pixel_clock))

    val = [0x00, 0x01, 0x02, 0x04]

    val_str = '0x00 0x01 0x02 0x04'

    if self._block[10] not in val:
      my_err = error.Error(loc + '- byte 10', 'Invalid value for Video Timing '
                           'Support Flags', val_str, '0x%02X' % self._block[10])
      errors.append(my_err)

    return errors


# NB: This class is untested - no sample EDIDs to check
class DisplayRangeGTF(DisplayRangeDescriptor):
  """Analyzes a Display Range GTF Descriptor (subtype of Display Range)."""

  def __init__(self, block):
    """Creates a DisplayRangeGTF object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    DisplayRangeDescriptor.__init__(self, block, SUBTYPE_DISPLAY_RANGE_2ND_GTF)

  @property
  def start_break_freq(self):
    """Fetches start break frequency.

    Returns:
      A string that indicates start break frequency.
    """
    return '%s kHz' % (self._block[12]*2)

  @property
  def c(self):
    """Fetches the value c for the Generalized Timing Formula (GTF).

    Returns:
      An integer that is the value of c.
    """
    return self._block[13] / 2

  @property
  def m(self):
    """Fetches the value m for the Generalized Timing Formula (GTF).

    Returns:
      An integer that is the value of m.
    """
    return (self._block[15] << 8) + self._block[14]

  @property
  def k(self):
    """Fetches the value k for the Generalized Timing Formula (GTF).

    Returns:
      An integer that is the value of k.
    """
    return self._block[16]

  @property
  def j(self):
    """Fetches the value j for the Generalized Timing Formula (GTF).

    Returns:
      An integer that is the value of j.
    """
    return self._block[17] / 2


class DisplayRangeCVT(DisplayRangeDescriptor):
  """Analyzes a Display Range CVT Descriptor (subtype of Display Range)."""

  _aspect_ratios = [
      [0x80, '4:3 AR'],
      [0x40, '16:9 AR'],
      [0x20, '16:10 AR'],
      [0x10, '5:4 AR'],
      [0x08, '15:9 AR']
  ]

  def __init__(self, block):
    """Creates a DisplayRangeDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    DisplayRangeDescriptor.__init__(self, block, SUBTYPE_DISPLAY_RANGE_CVT)

  @property
  def cvt_version(self):
    """Fetches CVT version - i.e., Version 1.1.

    Returns:
      A string that indicates the version.
    """
    version = (self._block[11] >> 4) & 0x0F
    revision = self._block[11] & 0x0F
    return '%d.%d' % (version, revision)

  @property
  def additional_pixel_clock(self):
    """Fetches additional pixel clock value.

    Returns:
      A float indicating additional pixel clock value (in MHz).
    """
    return (self._block[9] * 10) - (((self._block[12] >> 2) & 0x3F) * 0.25)

  @property
  def max_active_pixels(self):
    """Fetches maximum active pixels.

    Returns:
      A string describing the limit on horizontal active pixels.
    """
    if self._block[13] == 0x00:
      return 'No limit on horizontal active pixels'
    else:  # 8 x [Byte13 + (256 x (Byte 12, bits 1-0))]
      byte12_end = self._block[12] & 0x03
      return str(8 * (self._block[13] + (256 * byte12_end)))

  @property
  def supported_aspect_ratios(self):
    """Fetches supported aspect ratios.

    Returns:
      A dict of strings and bools specifying supported aspect ratios.
    """
    return tools.DictFilter(self._aspect_ratios, self._block[14])

  @property
  def preferred_aspect_ratio(self):
    """Fetches the preferred aspect ratio.

    Returns:
      A string indicating the preferred aspect ratio.
    """
    pref = (self._block[15] >> 5) & 0x07
    if pref >= len(self._aspect_ratios):
      return 'Undefined'
    return self._aspect_ratios[pref][1]

  @property
  def cvt_blanking_support(self):
    """Fetches the CVT blanking support.

    Returns:
      A collections.OrderedDict of string keys and boolean values indicating
      types of CVT blanking support.
    """
    b = collections.OrderedDict()

    b['Standard CVT Blanking'] = bool(self._block[15] & 0x08)
    b['Reduced CVT Blanking'] = bool(self._block[15] & 0x10)

    return b

  @property
  def display_scaling_support(self):
    """Fetches the types of display scaling support.

    Returns:
      A collections.OrderedDict of string keys and boolean values indicating the
      supported types of display scaling.
    """
    d = collections.OrderedDict()

    d['Horizontal Shrink'] = bool(self._block[16] & 0x80)
    d['Horizontal Stretch'] = bool(self._block[16] & 0x40)
    d['Vertical Shrink'] = bool(self._block[16] & 0x20)
    d['Vertical Stretch'] = bool(self._block[16] & 0x10)

    return d

  @property
  def preferred_vert_refresh(self):
    """Fetches preferred vertical refresh rate.

    Returns:
      An int indicating preferred vertical refresh rate in Hz.
    """
    return self._block[17]


# NB: This class is untested
class ColorPointDescriptor(Descriptor):
  """Analyzes a Color Point Descriptor."""

  def __init__(self, block):
    """Creates a ColorPointDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_COLOR_POINT_DATA)

  @property
  def first_color_point(self):
    """Fetches the first color point in the descriptor.

    Returns:
      A ColorPoint object.
    """
    return ColorPoint(self._block, 5)

  @property
  def second_color_point(self):
    """Fetches the second color point in the descriptor.

    Returns:
      A ColorPoint object.
    """
    return ColorPoint(self._block, 10)

  def CheckErrors(self, index=None):
    """Checks the ColorPointDescriptor for errors.

    Args:
      index: The integer index of the descriptor.

    Returns:
      A list of error.Error objects.
    """
    errors = []

    if self._block[5] == 0x00:
      errors.append(error.Error('ColorPointDescriptor', 'First color point is '
                                'invalid', 'Non-0 value', 0x00))

    return errors


class ColorPoint(object):
  """Analyzes a single Color Point within a Color Point Descriptor."""

  def __init__(self, block, start):
    """Creates a ColorPoint object.

    Args:
      block: A list of bytes that make up this descriptor.
      start: The start index of the ColorPoint.
    """
    self._block = block[start : (start + 5)]

  @property
  def index_number(self):
    """Fetches the index number.

    Returns:
      An integer that indicates the index number of the Color Point.
    """
    return self._block[0]

  @property
  def white_x(self):
    """Fetches the White X coordinate in the Color Point.

    Returns:
      An integer that indicates the White X coordinate in the Color Point.
    """
    return ((self._block[2] << 2)
            + ((self._block[1] >> 2) & 0x03))

  @property
  def white_y(self):
    """Fetches the White Y coordinate in the Color Point.

    Returns:
      An integer that indicates the White Y coordinate in the Color Point.
    """
    return ((self._block[3] << 2)
            + (self._block[1] & 0x03))

  @property
  def gamma(self):
    """Fetches the gamma value (range 1.00-3.54).

    Returns:
      A float describing the gamma value, or None if unspecified.
    """
    if self._block[4] == 0xFF:
      return None
    else:
      return (self._block[4] + 100) / 100


class StandardTimingDescriptor(Descriptor):
  """Analyzes a Standard Timing Descriptor."""

  def __init__(self, block, version):
    """Creates a StandardTimingDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
      version: The string indicating the version of the EDID.
    """
    Descriptor.__init__(self, block, TYPE_STANDARD_TIMING)
    self._version = version

  @property
  def standard_timings(self):
    """Fetches the standard timings indicated in this descriptor.

    Returns:
      A list of StandardTiming objects.
    """
    sts = []

    for x in xrange(0, 7):
      st = standard_timings.GetStandardTiming(self._block, 5 + (x*2),
                                              self._version)
      if st:
        sts.append(st)

    return sts


class DisplayColorDescriptor(Descriptor):
  """Analyzes a Display Color Descriptor."""

  def __init__(self, block):
    """Creates a DisplayColorDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_DISPLAY_COLOR_MANAGEMENT)

  @property
  def red_a3(self):
    """Fetches the red a3 value for color management.

    Returns:
      An integer denoting the red a3 value for color management.
    """
    return (self._block[7] << 8) + self._block[6]

  @property
  def red_a2(self):
    """Fetches the red a2 value for color management.

    Returns:
      An integer denoting the red a2 value for color management.
    """
    return (self._block[9] << 8) + self._block[8]

  @property
  def green_a3(self):
    """Fetches the green a3 value for color management.

    Returns:
      An integer denoting the green a3 value for color management.
    """
    return (self._block[11] << 8) + self._block[10]

  @property
  def green_a2(self):
    """Fetches the green a2 value for color management.

    Returns:
      An integer denoting the green a2 value for color management.
    """
    return (self._block[13] << 8) + self._block[12]

  @property
  def blue_a3(self):
    """Fetches the blue a3 value for color management.

    Returns:
      An integer denoting the blue a3 value for color management.
    """
    return (self._block[15] << 8) + self._block[14]

  @property
  def blue_a2(self):
    """Fetches the blue a2 value for color management.

    Returns:
      An integer denoting the blue a2 value for color management.
    """
    return (self._block[17] << 8) + self._block[16]


class CoordinatedVideoTimingsDescriptor(Descriptor):
  """Analyzes a Coordinated Video Timings Descriptor."""

  def __init__(self, block):
    """Creates a CoordinatedVideoTimingsDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_CVT_TIMING)

  @property
  def coordinated_video_timings(self):
    """Fetches the coordinated video timings.

    Returns:
      A list of coordinated_video_timings.CoordinatedVideoTiming objects.
    """
    cvts = []

    for x in xrange(0, 4):
      cvt = cvt_module.GetCoordinatedVideoTiming(self._block, 6 + (x*3))
      if cvt:
        cvts.append(cvt)

    return cvts

  def CheckErrors(self, index=None):
    """Checks the CoordinatedVideoTimingsDescriptor for errors.

    Args:
      index: The integer index of the descriptor.

    Returns:
      A list of error.Error objects.
    """
    errors = []
    cvts = self.coordinated_video_timings

    for x in xrange(0, len(cvts)):
      err = cvts[x].CheckErrors(x + 1)
      if err:
        errors.append(err)

    return errors


class EstablishedTimingsIIIDescriptor(Descriptor):
  """Analyzes an Established Timings III Descriptor."""

  def __init__(self, block):
    """Creates an EstablishedTimingsIIIDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_ESTABLISHED_TIMINGS_III)
    self._timings = [
        [0x80000000000, '640 x 350 @ 85 Hz'],
        [0x40000000000, '640 x 400 @ 85 Hz'],
        [0x20000000000, '720 x 400 @ 85 Hz'],
        [0x10000000000, '640 x 480 @ 85 Hz'],
        [0x8000000000, '848 x 480 @ 60 Hz'],
        [0x4000000000, '800 x 600 @ 85 Hz'],
        [0x2000000000, '1024 x 768 @ 85 Hz'],
        [0x1000000000, '1152 x 864 @ 75 Hz'],
        [0x800000000, '1280 x 768 @ 60 Hz (RB)'],
        [0x400000000, '1280 x 768 @ 60 Hz'],
        [0x200000000, '1280 x 768 @ 75 Hz'],
        [0x100000000, '1280 x 768 @ 85 Hz'],
        [0x80000000, '1280 x 960 @ 60 Hz'],
        [0x40000000, '1280 x 960 @ 85 Hz'],
        [0x20000000, '1280 x 1024 @ 60 Hz'],
        [0x10000000, '1280 x 1024 @ 85 Hz'],
        [0x8000000, '1360 x 768 @ 60 Hz'],
        [0x4000000, '1440 x 900 @ 60 Hz (RB)'],
        [0x2000000, '1440 x 900 @ 60 Hz'],
        [0x1000000, '1440 x 900 @ 75 Hz'],
        [0x800000, '1440 x 900 @ 85 Hz'],
        [0x400000, '1400 x 1050 @ 60 Hz (RB)'],
        [0x200000, '1400 x 1050 @ 60 Hz'],
        [0x100000, '1400 x 1050 @ 75 Hz'],
        [0x80000, '1400 x 1050 @ 85 Hz'],
        [0x40000, '1680 x 1050 @ 60 Hz (RB)'],
        [0x20000, '1680 x 1050 @ 60 Hz'],
        [0x10000, '1680 x 1050 @ 75 Hz'],
        [0x8000, '1680 x 1050 @ 85 Hz'],
        [0x4000, '1600 x 1200 @ 60 Hz'],
        [0x2000, '1600 x 1200 @ 65 Hz'],
        [0x1000, '1600 x 1200 @ 70 Hz'],
        [0x800, '1600 x 1200 @ 75 Hz'],
        [0x400, '1600 x 1200 @ 85 Hz'],
        [0x200, '1792 x 1344 @ 60 Hz'],
        [0x100, '1792 x 1344 @ 75 Hz'],
        [0x80, '1856 x 1392 @ 60 Hz'],
        [0x40, '1856 x 1392 @ 75 Hz'],
        [0x20, '1920 x 1200 @ 60 Hz (RB)'],
        [0x10, '1920 x 1200 @ 60 Hz'],
        [0x8, '1920 x 1200 @ 75 Hz'],
        [0x4, '1920 x 1200 @ 85 Hz'],
        [0x2, '1920 x 1440 @ 60 Hz'],
        [0x1, '1920 x 1440 @ 75 Hz']
    ]

  @property
  def established_timings(self):
    """Fetches the supported established timings.

    Returns:
      A dict of strings and bools denoting the supported established timings.
    """
    # Bytes 6-10 plus first half of 11
    timing_byte = ((self._block[6] << 36) + (self._block[7] << 28) +
                   (self._block[8] << 20) + (self._block[9] << 12) +
                   (self._block[10] << 4) + (self._block[11] >> 4))
    return tools.DictFilter(self._timings, timing_byte)


# This descriptor is not supposed to be used yet
class ReservedDescriptor(Descriptor):
  """Defines a ReservedDescriptor (which should not yet appear in EDID)."""

  def __init__(self, block):
    """Creates a ReservedDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_RESERVED)


# This descriptor indicates that the descriptor space is unused
class DummyDescriptor(Descriptor):
  """Defines a Dummy (placeholder) Descriptor."""

  def __init__(self, block):
    """Creates a DummyDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_DUMMY)

  # First 5 bytes of Dummy Descriptor should be 0x00
  def CheckErrors(self, index=None):
    """Checks the DummyDescriptor for errors.

    Args:
      index: The integer index of this descriptor (1-4).

    Returns:
      A list of error.Error objects.
    """
    errors = []
    loc = '%s %s' % (self._type, '#%d' % index if index else '')

    if self._block[0:5] != [0x00, 0x00, 0x00, 0x10, 0x00]:
      found_header = '0x%02X ' * 5 % tuple(self._block[0:5])
      errors.append(error.Error(loc, 'Bytes 0-4', '0x00 0x00 0x00 0x10 0x00',
                                found_header))
    if self._block[5:18] != [0x00] * 13:
      found_body = '0x%02X ' * 13 % tuple(self._block[5:18])
      errors.append(error.Error(loc, 'Bytes 5-18', 'All 0x00',
                                found_body))

    return errors


class ManuSpecifiedDescriptor(Descriptor):
  """Defines a Manufacturer Specified Descriptor."""

  def __init__(self, block):
    """Creates a ManuSpecifiedDescriptor object.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_MANUFACTURER_SPECIFIED)

  def GetBlob(self):
    """Fetches the data blob (13-byte manufacturer specified data).

    Returns:
      A list of bytes that make up the data blob.
    """
    return self._block[5:18]


class DetailedTimingDescriptor(Descriptor):
  """Defines a Detailed Timing Descriptor, perhaps the most common type."""

  def __init__(self, block):
    """Creates a DetailedTiming Descriptorobject.

    Args:
      block: A list of 18-bytes that make up this descriptor.
    """
    Descriptor.__init__(self, block, TYPE_DETAILED_TIMING)

  @property
  def pixel_clock(self):
    """Fetches pixel clock measurements.

    Returns:
      A float denoting the pixel clock measurement (in MHz).
    """
    # Bytes 0-1 | Pixel clock in kHz units
    return ((self._block[1] << 8) + (self._block[0])) / 100.0

  @property
  def h_active_pixels(self):
    """Fetches the number of horizontal active pixels.

    Returns:
      An integer denoting the number of horizontal active pixels.
    """
    # Bytes 2&4 | Horizontal active pixels (0-4095)
    return ((self._block[4] & 0xF0) << 4) + self._block[2]

  @property
  def h_blanking_pixels(self):
    """Fetches the number of horizontal blanking pixels.

    Returns:
      An integer denoting the number of horizontal blanking pixels.
    """
    # Bytes 3&4 | Horizontal blanking pixels (0-4095)
    return ((self._block[4] & 0x0F) << 8) + self._block[3]

  @property
  def v_active_lines(self):
    """Fetches the number of vertical active lines.

    Returns:
      An integer denoting the number of vertical active lines
    """
    # Bytes 5&7 | Vertical active lines (0-4095)
    return ((self._block[7] & 0xF0) << 4) + self._block[5]

  @property
  def v_blanking_lines(self):
    """Fetches the number of vertical blanking lines.

    Returns:
      An integer denoting the number of vertical blanking lines.
    """
    # Bytes 6&7 | Vertical blanking lines (0-4095)
    return ((self._block[7] & 0x0F) << 8) + self._block[6]

  @property
  def h_sync_offset(self):
    """Fetches the number of horizontal sync offset pixels.

    Returns:
      An integer denoting the number of horizontal sync offset pixels.
    """
    # Bytes 8&11 | Horizontal sync offset pixels (0-1023)
    return ((self._block[11] & 0xC0) << 2) + self._block[8]

  @property
  def h_sync_pulse(self):
    """Fetches the horizontal sync pulse.

    Returns:
      An integer denoting the horizontal sync pulse.
    """
    # Bytes 9&11 | Horizontal sync pulse width pixels (0-1023)
    return ((self._block[11] & 0x30) << 4) + self._block[9]

  @property
  def v_sync_offset(self):
    """Fetches the number of vertical sync offset pixels.

    Returns:
      An integer denoting the number of vertical sync offset pixels.
    """
    # Bytes 10&11 | Vertical sync offset lines (0-63)
    return ((self._block[11] & 0x0C) << 2) + ((self._block[10] & 0xF0) >> 4)

  @property
  def v_sync_pulse(self):
    """Fetches the vertical sync pulse.

    Returns:
      An integer denoting the vertical sync pulse.
    """
    # Bytes 10&11 | Vertical sync pulse width lines (0-63)
    return ((self._block[11] & 0x03) << 4) + (self._block[10] & 0x0F)

  @property
  def h_display_size(self):
    """Fetches the horizontal display size.

    Returns:
      An integer denoting the horizontal display size.
    """
    # Bytes 12&14 | Horizontal display size (mm) (0-4095)
    return ((self._block[14] & 0xF0) << 4) + self._block[12]

  @property
  def v_display_size(self):
    """Fetches the vertical display size.

    Returns:
      An integer denoting the vertical display size.
    """
    # Bytes 13&14 | Vertical display size (mm) (0-4095)
    return ((self._block[14] & 0x0F) << 8) + self._block[13]

  @property
  def h_border_pixels(self):
    """Fetches the number of horizontal border pixels.

    Returns:
      An integer denoting the number of horizontal border pixels.
    """
    # Byte 15 | Horizontal border pixels (each side; total is 2x)
    return self._block[15]

  @property
  def v_border_lines(self):
    """Fetches the number of vertical border lines.

    Returns:
      An integer denoting the number of vertical border lines.
    """
    # Byte 16 | Vertical border lines (each side; total is 2x)
    return self._block[16]

  @property
  def interlaced(self):
    """Fetches the interlace setting.

    Returns:
      A boolean indicating whether the setting is interlaced or not.
    """
    # Byte 17 | Features bitmap
    # Bit 7 | Interlaced
    return self._block[17] & 0x80 != 0

  @property
  def stereo_mode(self):
    """Fetches the stereo mode.

    Returns:
      A string indicating the stereo mode.
    """
    # Bits 6-5 | Stereo mode
    stereo_bits = (self._block[17] & 0x60) >> 4 + (self._block[17] & 0x01)
    stereo_map = [
        'No stereo',
        'No stereo',
        'Field sequential stereo, right image when stereo sync signal = 1',
        '2-way interleaved stereo, right image on even lines',
        'Field sequential stereo, left image when stereo sync signal = 1',
        '2-way interleaved stereo, left image on even lines',
        '4-way interleaved stereo',
        'Side-by-side interleaved stereo'
    ]

    return stereo_map[stereo_bits]

  @property
  def sync_type(self):
    """Fetches the sync signal definition type.

    Returns:
      A dict of strings and bools indicating sync signal definition types.
    """
    s = collections.OrderedDict()
    s['Type'] = None

    # Bits 4-1 | Sync signal definitions:
    sync_bits = (self._block[17] >> 1) & 0x0F
    if not sync_bits & 0x08:  # Analog sync signal definitions

      if not sync_bits & 0x04:
        s['Type'] = 'Analog Composite Sync'
      else:
        s['Type'] = 'Bipolar Analog Composite Sync'

      s['Serrations'] = bool(sync_bits & 0x02)
      s['Sync on RGB'] = bool(sync_bits & 0x01)

    else:  # Digital sync signal definitions
      if not sync_bits & 0x04:
        s['Type'] = 'Digital Composite Sync'
        s['Serrations'] = bool(sync_bits & 0x02)
      else:
        s['Type'] = 'Digital Separate Sync'
        s['Vertical sync'] = 'Positive' if sync_bits & 0x02 else 'Negative'

      s['Horizontal sync (outside of V-sync)'] = ('Positive' if sync_bits & 0x01
                                                  else 'Negative')

    return s

