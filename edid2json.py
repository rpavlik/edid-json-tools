#!/usr/bin/env python3

# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

#############################################################
# Json output parser
# Takes in binary blob, creates EDID object, and outputs Json
# This parser is primarily based on the following:
# 1. "VESA Enhanced Extended Display Identification Data Standard", Release A,
#   Revision 2, Sept. 25, 2006.
# 2. "A DTV Profile for Uncompressed High Speed Digital Interfaces",
#   ANSI/CEA-861-F, Aug., 2013.
# 3. HDMI spec.
#############################################################

"""Parses EDID into python object and outputs Json form of EDID object."""



import json
import sys

import edid.data_block as data_block
import edid.descriptor as descriptor
import edid.edid as edid
import edid.extensions as extensions
from edid.tools import BytesFromFile


def _XYDict(x_value, y_value, first='x', second='y'):
  """Takes in x and y coordinates and returns in dictionary form.

  Args:
    x_value: The value of the x coordinate.
    y_value: The value of the y coordinate.
    first: The key for first field.
    second: The key for second field.

  Returns:
    A dict with a x key/value pair and a y key/value pair.
  """
  return {first: x_value, second: y_value}


def GetManufacturerInfo(e):
  """Organizes the manufacturer information of an EDID.

  Args:
    e: The edid.Edid object.

  Returns:
    A dictionary of manufacturer information.
  """
  return {
      'Manufacturer ID': e.manufacturer_id,
      'ID Product Code': e.product_code,
      'Serial number': e.serial_number,
      'Week of manufacture': e.manufacturing_week,
      'Year of manufacture': e.manufacturing_year,
      'Model year': e.model_year
  }


def GetBasicDisplay(e):
  """Organizes the basic display information of an EDID.

  Args:
    e: The edid.Edid object.

  Returns:
    A dictionary of basic display information.
  """
  bd = e.basic_display
  jdict = {'Video input type': 'Digital' if bd.video_input_type else 'Analog'}

  if bd.video_input_type:  # Digital

    jdict.update({
        'Color Bit Depth': bd.color_bit_depth,
        'Digital Video Interface Standard Support': bd.digital_supports
    })

  elif not bd.video_input_type:  # Analog

    jdict.update({
        'Video white and sync levels': bd.signal_level,
        'Blank-to-black setup expected': bd.blank_black,
        'Separate sync supported': bd.separate_sync,
        'Composite sync (on HSync) supported': bd.composite_sync,
        'Sync on green supported': bd.green_sync,
        'VSync serrated when composite/sync-on-green used': bd.vsync_pulse
    })

  # Shared basic display properties (both analog/digital)
  if not bd.horizontal_dim or not bd.vertical_dim:
    max_dim = None
  else:
    max_dim = _XYDict(bd.horizontal_dim, bd.vertical_dim)

  pix_str = ('Preferred timing includes native timing pixel format and refresh '
             'rate')

  jdict.update({
      'Maximum dimensions (cm)': max_dim,
      'Aspect ratio (portrait)': bd.aspect_ratio_portrait,
      'Aspect ratio (landscape)': bd.aspect_ratio_landscape,
      'Display gamma': bd.display_gamma,
      'DPM standby supported': bd.dpm_standby,
      'DPM suspend supported': bd.dpm_suspend,
      'DPM active-off supported': bd.active_off,
      'Display color type': bd.display_type,
      'sRGB Standard is default colour space': bd.srgb_as_default,
      pix_str: bd.native_preferred_timing_mode,
      'Continuous frequency supported': bd.cont_freq_support
  })

  return jdict


def GetChromaticity(e):
  """Organizes the chromaticity information of an EDID.

  Args:
    e: The edid.Edid object.

  Returns:
    A dictionary of chromaticity information.
  """
  chrom = e.chromaticity

  return {
      'Red': _XYDict(chrom.red_x, chrom.red_y),
      'Green': _XYDict(chrom.grn_x, chrom.grn_y),
      'Blue': _XYDict(chrom.blue_x, chrom.blue_y),
      'White': _XYDict(chrom.wht_x, chrom.wht_y)
  }


def GetEstablishedTiming(e):
  """Organizes the established timing information of an EDID.

  Args:
    e: The edid.Edid object.

  Returns:
    A list of established timing information.
  """
  return e.established_timings.supported_timings


def GetBaseStandardTiming(e):
  """Organizes the standard timing information of an EDID.

  Args:
    e: The edid.Edid object.

  Returns:
    A list of standard timing information.
  """
  return [BuildSt(s) for s in e.standard_timings]


def BuildSt(st):
  """Organizes information in a single standard_timings.StandardTiming object.

  Args:
    st: A standard_timings.StandardTiming object.

  Returns:
    A dictionary of standard timings information.
  """
  return {
      'X resolution': st.x_resolution,
      'Ratio': st.xy_pixel_ratio,
      'Frequency': st.vertical_freq
  }


def GetDescriptorBlocks(e):
  """Organizes the descriptor blocks information of an EDID.

  Calls BuildBlockAnalysis on each block for detailed organization.

  Args:
    e: The edid.Edid object.

  Returns:
    A list of dictionaries of descriptor block information.
  """
  return [BuildBlockAnalysis(d) for d in e.descriptors]


def BuildBlockAnalysis(desc):
  """Organizes a single 18-byte descriptor's information.

  Called up to 4 times in a base EDID.
  Uses descriptor module to determine descriptor type.

  Args:
    desc: The descriptor being parsed.

  Returns:
    A dictionary of descriptor information.
  """
  mydict = {'Type': desc.type}

  if (desc.type == descriptor.TYPE_PRODUCT_SERIAL_NUMBER or
      desc.type == descriptor.TYPE_ALPHANUM_DATA_STRING or
      desc.type == descriptor.TYPE_DISPLAY_PRODUCT_NAME):

    mydict['Data string'] = desc.string

  elif desc.type == descriptor.TYPE_DISPLAY_RANGE_LIMITS:

    mydict['Subtype'] = desc.subtype

    vert_rate = _XYDict(desc.min_vertical_rate,
                        desc.max_vertical_rate, 'Minimum', 'Maximum')
    hor_rate = _XYDict(desc.min_horizontal_rate,
                       desc.max_horizontal_rate, 'Minimum', 'Maximum')

    mydict.update({
        'Vertical rate (Hz)': vert_rate,
        'Horizontal rate (kHz)': hor_rate,
        'Pixel clock (MHz)': desc.pixel_clock
    })

    if desc.subtype == descriptor.SUBTYPE_DISPLAY_RANGE_CVT:

      mydict.update({
          'Supported aspect ratios': desc.supported_aspect_ratios,
          'CVT blanking support': desc.cvt_blanking_support,
          'Display scaling support': desc.display_scaling_support,
          'CVT Version': desc.cvt_version,
          'Additional Pixel Clock (MHz)': desc.additional_pixel_clock,
          'Maximum active pixels': desc.max_active_pixels,
          'Preferred aspect ratio': desc.preferred_aspect_ratio,
          'Preferred vertical refresh (Hz)': desc.preferred_vert_refresh
      })

    elif desc.subtype == descriptor.SUBTYPE_DISPLAY_RANGE_2ND_GTF:

      mydict.update({
          'Start break frequency': desc.start_break_freq,
          'C': desc.c,
          'M': desc.m,
          'K': desc.k,
          'J': desc.j
      })

  elif desc.type == descriptor.TYPE_COLOR_POINT_DATA:
    cp_1 = desc.first_color_point
    cp_2 = desc.second_color_point

    mydict['Color Point'] = BuildCp(cp_1)
    mydict['Color Point'] = BuildCp(cp_2)

  elif desc.type == descriptor.TYPE_STANDARD_TIMING:

    mydict['Standard Timings'] = desc.standard_timings

  elif desc.type == descriptor.TYPE_DISPLAY_COLOR_MANAGEMENT:

    mydict['Display color management'] = {
        'Red a3:': desc.red_a3,
        'Red a2:': desc.red_a2,
        'Green a3:': desc.green_a3,
        'Green a2:': desc.green_a2,
        'Blue a3:': desc.blue_a3,
        'Blue a2:': desc.blue_a2
    }

  elif desc.type == descriptor.TYPE_CVT_TIMING:

    cvtlist = [BuildCvt(c) for c in desc.coordinated_video_timings]
    mydict['Coordinated Video Timings'] = cvtlist

  elif desc.type == descriptor.TYPE_ESTABLISHED_TIMINGS_III:

    mydict['Established Timings'] = desc.established_timings

  elif desc.type == descriptor.TYPE_MANUFACTURER_SPECIFIED:

    mydict['Blob'] = desc.GetBlob()

  elif desc.type == descriptor.TYPE_DETAILED_TIMING:

    return BuildDtd(desc)

  return mydict


def BuildCp(cp):
  """Organizes information about a single descriptor.ColorPoint object.

  Args:
    cp: A descriptor.ColorPoint object.

  Returns:
    A dictionary of color point information.
  """
  return {
      'Index number': cp.index_number,
      'White point coordinates': _XYDict(cp.white_x, cp.white_y),
      'Gamma': cp.gamma
  }


def BuildDtd(desc):
  """Organizes information about a single descriptor.DetailedTimingDescriptor.

  Used in the base EDID analysis as well as certain extensions (i.e., VTB).

  Args:
    desc: The descriptor.DetailedTimingDescriptor.

  Returns:
    A dictionary of detailed timing descriptor information.
  """
  return {
      'Type': desc.type,
      'Pixel clock (MHz)': desc.pixel_clock,
      'Addressable': _XYDict(desc.h_active_pixels, desc.v_active_lines),
      'Blanking': _XYDict(desc.h_blanking_pixels, desc.v_blanking_lines),
      'Front porch': _XYDict(desc.h_sync_offset, desc.v_sync_offset),
      'Sync pulse': _XYDict(desc.h_sync_pulse, desc.v_sync_pulse),
      'Image size (mm)': _XYDict(desc.h_display_size, desc.v_display_size),
      'Border': _XYDict(desc.h_border_pixels, desc.v_border_lines),
      'Interlace': desc.interlaced,
      'Stereo viewing': desc.stereo_mode,
      'Sync type': desc.sync_type
  }


def AnalyzeExtension(e, block_num):
  """Organizes an extension of an EDID.

  Args:
    e: The edid.Edid object.
    block_num: The index of the extension being analyzed.

  Returns:
    A dictionary of extension information.
  """
  ext = e.GetExtension(block_num)
  mydict = {'Type': ext.type}

  if ext.type == extensions.TYPE_CEA_861:

    # BASIC CEA INFO
    mydict.update({
        'Version': ext.version,
        'Underscan': ext.underscan_support,
        'Basic audio': ext.basic_audio_support,
        'YCbCr 4:4:4': ext.ycbcr444_support,
        'YCbCr 4:2:2': ext.ycbcr422_support,
        'Native DTD count': ext.native_dtd_count
    })

    # DATA BLOCKS

    dblist = []

    for db in ext.data_blocks:

      dbdict = {'Type': db.type}

      if (db.type == data_block.DB_TYPE_VIDEO or
          db.type == data_block.DB_TYPE_YCBCR420_VIDEO):

        svd_list = []
        for svd in db.short_video_descriptors:
          svd_list.append({'Nativity': svd.nativity, 'VIC': svd.vic})

        dbdict['Short video descriptors'] = svd_list

      elif db.type == data_block.DB_TYPE_AUDIO:

        adlist = []
        for ad in db.short_audio_descriptors:

          addict = {
              'Type': ad.type,
              'Max channel count': ad.max_channel_count,
              'Supported sampling': ad.supported_sampling_freqs,
          }

          if ad.type == data_block.AUDIO_TYPE_LPCM:
            addict['Bit depth'] = ad.bit_depth
          elif ad.type == data_block.AUDIO_TYPE_DRA:
            addict['DRA value'] = ad.value
          elif ad.format_code <= 8 and ad.format_code >= 2:
            addict['Max bit rate'] = ad.max_bit_rate
          elif ad.format_code <= 14 and ad.format_code <= 9:
            addict['Value'] = ad.value
          else:
            addict['Extension code'] = ad.ext_code
            addict['Frame length'] = ad.frame_length
            if ad.mps_support:
              addict['MPS support'] = ad.mps_support

          adlist.append(addict)

        dbdict['Short audio descriptors'] = adlist

      elif db.type == data_block.DB_TYPE_SPEAKER_ALLOCATION:

        dbdict['Speaker allocation'] = db.allocation

      elif (db.type == data_block.DB_TYPE_VENDOR_SPECIFIC or
            db.type == data_block.DB_TYPE_VENDOR_SPECIFIC_AUDIO or
            db.type == data_block.DB_TYPE_VENDOR_SPECIFIC_VIDEO):
        dbdict['IEEE OUI'] = db.ieee_oui
        dbdict['Data payload'] = db.payload

      elif db.type == data_block.DB_TYPE_COLORIMETRY:

        dbdict['Colorimetry'] = db.colorimetry
        dbdict['Metadata'] = db.metadata

      elif db.type == data_block.DB_TYPE_VIDEO_CAPABILITY:

        dbdict.update({
            'YCC Quantization range', db.selectable_quantization_range_ycc,
            'RGB Quantization range', db.selectable_quantization_range_rgb,
            'PT behavior', db.pt_behavior,
            'IT behavior', db.it_behavior,
            'CE behavior', db.ce_behavior
        })

      elif db.type == data_block.DB_TYPE_INFO_FRAME:

        if_proc = db.if_processing
        dbdict['InfoFrame Processing Descriptor'] = {'Data payload':
                                                     if_proc.payload}

        vsiflist = []
        for vsif in db.vsifs:

          vsifdict = {
              'Type': vsif.type,
              'Data payload': vsif.payload
          }

          if vsif.type == data_block.INFO_FRAME_TYPE_VENDOR_SPECIFIC:
            vsifdict['IEEE OUI'] = vsif.ieee_oui

          vsiflist.append(vsifdict)

        dbdict['Vendor-Specific Info Frames'] = vsiflist

      elif db.type == data_block.DB_TYPE_YCBCR420_CAPABILITY_MAP:

        dbdict['Supported descriptor indices'] = db.supported_descriptor_indices

      elif db.type == data_block.DB_TYPE_VIDEO_FORMAT_PREFERENCE:

        vps_list = []
        for vp in db.video_preferences:
          vp_json = {'Type': vp.type}
          if vp.type == 'Video Preference VIC':
            vp_json['VIC'] = vp.vic
          elif vp.type == 'Video Preference DTD':
            vp_json['DTD index'] = vp.dtd_index
          else:  # vp.type == 'Video Preference Reserved'
            vp_json['SVR'] = vp.svr

          vps_list.append(vp_json)

        dbdict['Video preferences'] = vps_list

      dblist.append(dbdict)

    mydict['Data blocks'] = dblist

    # DETAILED TIMING DESCRIPTORS

    mydict['Descriptors'] = [BuildDtd(dtd) for dtd in ext.dtds]

  elif ext.type == extensions.TYPE_VIDEO_TIMING_BLOCK:

    mydict.update({
        'Version': ext.version,
        'Detailed Timing Descriptors': [BuildDtd(d) for d in ext.dtbs],
        'Coordinated Video Timings': [BuildCvt(c) for c in ext.cvts],
        'Standard Timings': [BuildSt(s) for s in ext.sts]
    })

  elif ext.type == extensions.TYPE_EXTENSION_BLOCK_MAP:

    mydict['Tags'] = ext.all_tags

  return mydict


def BuildCvt(cvt):
  """Organizes information about a single CoordinatedVideoTiming object.

  Full object name: coordinated_video_timings.CoordinatedVideoTiming.

  Args:
    cvt: A single CoordinatedVideoTiming object.

  Returns:
    A dictionary of coordinated video timing information.
  """
  return {
      'Active vertical lines': cvt.active_vertical_lines,
      'Aspect ratio': cvt.aspect_ratio,
      'Preferred refresh rate': cvt.preferred_vertical_rate,
      'Supported refresh rates': cvt.supported_vertical_rates
  }


def BuildBase(e):
  """Organizes all information of the base EDID.

  Args:
    e: The edid.Edid object.

  Returns:
    A dictionary of EDID base block information.
  """
  return {
      'Manufacturer Info': GetManufacturerInfo(e),
      'Basic Display': GetBasicDisplay(e),
      'Chromaticity': GetChromaticity(e),
      'Established Timing': GetEstablishedTiming(e),
      'Standard Timing': GetBaseStandardTiming(e),
      'Descriptors': GetDescriptorBlocks(e)
  }


def BuildExtensions(e):
  """Organizes all information of one or more extensions.

  Args:
    e: The edid.Edid object.

  Returns:
    A list of extension information.
  """
  return [AnalyzeExtension(e, x + 1) for x in list(range(0,
                                                          e.extension_count))]


def ParseEdid(filename):
  """Creates an EDID object from binary blob and converts to dictionary form.

  Args:
    filename: The name of the file containing the binary blob.

  Returns:
    A dictionary of information about the EDID object.
  """
  # Fill the edid list with bytes from binary blob
  edid_obj = edid.Edid(BytesFromFile(filename))
  errors = edid_obj.GetErrors()
  if not errors:
    return {
        'Base': BuildBase(edid_obj),
        'Extensions': BuildExtensions(edid_obj),
        'Version': edid_obj.edid_version
    }
  else:
    print('Found %d errors\n' % len(errors))
    for error in errors:
      print('At %s: %s' % (error.location, error.message))
      if error.expected:
        print('\tExpected\t%s' % error.expected)
        print('\tFound\t\t\t%s' % error.found)


_USAGE = """
Usage: %s <inputfile>

The program takes an EDID file, organizes it into a JSON object and prints
it out in the stdout.
"""

####################
# CODE STARTS HERE #
####################
if __name__ == '__main__':
  if len(sys.argv) < 2:
    print(_USAGE % sys.argv[0])
  else:
    edid_json = ParseEdid(sys.argv[1])
    if edid_json:
      print(json.dumps(edid_json, sort_keys=True, indent=4))
