# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause


"""Provides DataBlock class and related classes with methods for parsing info.

DataBlock objects are found in CEA extensions and appear in varying length.
The various types of DataBlocks all inherit the basic DataBlock object.
"""

from typing import Final, List, Optional, Union

from edid_json_tools.typing import BoolDict, ByteList, OverscanBehavior

from . import tools

DB_TYPE_AUDIO = "Audio Data Block"
DB_TYPE_VIDEO = "Video Data Block"
DB_TYPE_VENDOR_SPECIFIC = "Vendor-Specific Data Block"
DB_TYPE_SPEAKER_ALLOCATION = "Speaker Allocation Block"
DB_TYPE_VESA_DISPLAY_TRANSFER_CHAR = (
    "VESA Display Transfer Characteristic " "Data Block"
)
DB_TYPE_RESERVED = "Reserved block"
DB_TYPE_VIDEO_CAPABILITY = "Video Capability Data Block"
DB_TYPE_VENDOR_SPECIFIC_VIDEO = "Vendor-Specific Video Data Block"
DB_TYPE_VESA_DISPLAY_DEVICE = "VESA Display Device Data Block"
DB_TYPE_VESA_VIDEO_TIMING = "VESA Video Timing Block Extension"
DB_TYPE_HDMI_VIDEO = "Reserved for HDMI Video Data Block"
DB_TYPE_COLORIMETRY = "Colorimetry Data Block"
DB_TYPE_VIDEO_FORMAT_PREFERENCE = "Video Format Preference Data Block"
DB_TYPE_VENDOR_SPECIFIC_AUDIO = "Vendor-Specific Audio Data Block"
DB_TYPE_YCBCR420_VIDEO = "YCbCr 4:2:0 Video Data Block"
DB_TYPE_YCBCR420_CAPABILITY_MAP = "YCbCr 4:2:0 Capability Map Data Block"
DB_TYPE_MISC_AUDIO_FIELDS = "Reserved for CEA Miscellaneous Audio Fields"
DB_TYPE_HDMI_AUDIO = "Reserved for HDMI Audio Data Block"
DB_TYPE_INFO_FRAME = "InfoFrame Data Block"
DB_TYPE_UNKNOWN = "Unknown Data Block"


AUDIO_TYPE_LPCM = "Linear Pulse Code Modulation (LPCM)"
AUDIO_TYPE_AC3 = "AC-3"
AUDIO_TYPE_MPEG1 = "MPEG1 (Layers 1 and 2)"
AUDIO_TYPE_MPG3 = "MP3 (MPEG1 Layer 3)"
AUDIO_TYPE_MPEG2 = "MPEG2 (multichannel)"
AUDIO_TYPE_AAC_LC = "AAC"
AUDIO_TYPE_DTS = "DTS"
AUDIO_TYPE_ATRAC = "ATRAC"
AUDIO_TYPE_ONE_BIT = "One-bit audio (aka SACD)"
AUDIO_TYPE_E_AC3 = "E-AC-3"
AUDIO_TYPE_DTS_HD = "DTS-HD"
AUDIO_TYPE_MAT = "MAT MLP/Dolby TrueHD"
AUDIO_TYPE_DST = "DST Audio"
AUDIO_TYPE_WMA_PRO = "Microsoft WMA Pro"

# Extended audio types:
AUDIO_TYPE_MPEG4_HE_AAC = "MPEG-4 HE AAC"
AUDIO_TYPE_MPEG4_HE_AAC_V2 = "MPEG-4 HE AAC v2"
AUDIO_TYPE_MPEG4_AAC_LC = "MPEG-4 AAC LC"
AUDIO_TYPE_DRA = "DRA"
AUDIO_TYPE_MPEG4_HE_AAC_MPS = "MPEG-4 HE AAC + MPEG Surround"
AUDIO_TYPE_MPEG4_AAC_LC_MPS = "MPEG-4AAC LC + MPEG Surround"
AUDIO_TYPE_UNKNOWN = "Unknown"


SAMPLING_FREQ_32KHZ = "32kHz"
SAMPLING_FREQ_44_1KHZ = "44.1kHz"
SAMPLING_FREQ_48KHZ = "48kHz"
SAMPLING_FREQ_88_2KHZ = "88.2kHz"
SAMPLING_FREQ_96KHZ = "96kHz"
SAMPLING_FREQ_176_4KHZ = "176.4kHz"
SAMPLING_FREQ_192KHZ = "192kHz"

FREQS = (
    (0x40, SAMPLING_FREQ_192KHZ),
    (0x20, SAMPLING_FREQ_176_4KHZ),
    (0x10, SAMPLING_FREQ_96KHZ),
    (0x08, SAMPLING_FREQ_88_2KHZ),
    (0x04, SAMPLING_FREQ_48KHZ),
    (0x02, SAMPLING_FREQ_44_1KHZ),
    (0x01, SAMPLING_FREQ_32KHZ),
)

MPS_IMPLICIT = "MPS implicit"
MPS_EXPLICIT = "MPS explicit"

AUDIO_BITS = (
    (0x4, "24 bit"),
    (0x2, "20 bit"),
    (0x1, "16 bit"),
)


SVD_NATIVE = "Native"
SVD_NONNATIVE = "Non-native"
SVD_UNSPECIFIED = "Unspecified"


SPEAKER_FRONT_LEFT_RIGHT = "Front Left / Front Right"
SPEAKER_LFE = "LFE"
SPEAKER_FRONT_CENTER = "Front Center"
SPEAKER_REAR_LEFT_RIGHT = "Rear Left / Rear Right"
SPEAKER_REAR_CENTER = "Rear Center"
SPEAKER_FRONT_LEFT_CENTER_RIGHT_CENTER = "Front Left Center / " "Front Right Center"
SPEAKER_REAR_LEFT_CENTER_RIGHT_CENTER = "Rear Left Center / Rear Right Center"
SPEAKER_FRONT_LEFT_RIGHT_WIDE = "Front Left Wide / Front Right Wide"
SPEAKER_FRONT_LEFT_RIGHT_HIGH = "Front Left High / Front Right High"
SPEAKER_TOP_CENTER = "Top Center"
SPEAKER_FRONT_CENTER_HIGH = "Front Center High"

SPEAKERS = (
    (0x01, SPEAKER_FRONT_LEFT_RIGHT),
    (0x02, SPEAKER_LFE),
    (0x04, SPEAKER_FRONT_CENTER),
    (0x08, SPEAKER_REAR_LEFT_RIGHT),
    (0x10, SPEAKER_REAR_CENTER),
    (0x20, SPEAKER_FRONT_LEFT_CENTER_RIGHT_CENTER),
    (0x40, SPEAKER_REAR_LEFT_CENTER_RIGHT_CENTER),
    (0x80, SPEAKER_FRONT_LEFT_RIGHT_WIDE),
    (0x100, SPEAKER_FRONT_LEFT_RIGHT_HIGH),
    (0x200, SPEAKER_TOP_CENTER),
    (0x400, SPEAKER_FRONT_CENTER_HIGH),
)

COLORIMETRY_XVYCC601 = "Standard Definition Colorimetry based on IEC " "61966-2-4"
COLORIMETRY_XVYCC709 = "High Definition Colorimetry based on IEC 61966-2-4"
COLORIMETRY_SYCC601 = "Colorimetry based on IEC 61966-2-1/Amendment 1"
COLORIMETRY_ADOBE_YCC601 = "Colorimetry based on IEC 61966-2-5, Annex A"
COLORIMETRY_ADOBE_RGB = "Colorimetry based on IEC 61966-2-5"
COLORIMETRY_BT2020_CYCC = "Colorimetry based on ITU-R BT.2020 YcCbcCrc"
COLORIMETRY_BT2020_YCC = "Colorimetry based on ITU-R BT.2020 YCbCr"
COLORIMETRY_BT2020_RGB = "Colorimetry based on ITU-R BT.2020 RGB"


COLORS = (
    (0x01, COLORIMETRY_XVYCC601),
    (0x02, COLORIMETRY_XVYCC709),
    (0x04, COLORIMETRY_SYCC601),
    (0x08, COLORIMETRY_ADOBE_YCC601),
    (0x10, COLORIMETRY_ADOBE_RGB),
    (0x20, COLORIMETRY_BT2020_CYCC),
    (0x40, COLORIMETRY_BT2020_YCC),
    (0x80, COLORIMETRY_BT2020_RGB),
)

OU_UNDEFINED = "No Data"
OU_NOT_SUPPORTED = "Video Formats not supported"
OU_OVERSCAN = "Always Overscanned"
OU_UNDERSCAN = "Always Underscanned"
OU_BOTH = "Supports both over- and underscan"


VIDEO_PREFERENCE_VIC = "Video Preference VIC"
VIDEO_PREFERENCE_DTD = "Video Preference DTD"
VIDEO_PREFERENCE_RESERVED = "Video Preference Reserved"


INFO_FRAME_TYPE_VENDOR_SPECIFIC = "Vendor Specific"
INFO_FRAME_TYPE_AUX_VIDEO_INFO = "Auxiliary Video Information"
INFO_FRAME_TYPE_SOURCE_PRODUCT = "Source Product Description"
INFO_FRAME_TYPE_AUDIO = "Audio"
INFO_FRAME_TYPE_MPEG_SOURCE = "MPEG Source"
INFO_FRAME_TYPE_NTSC_VBI = "NTSC VBI"
INFO_FRAME_TYPE_PROCESSING = "Processing Descriptor Header"
INFO_FRAME_TYPE_UNKNOWN = "Unknown"


def GetDataBlock(edid: ByteList, start: int) -> "DataBlock":
    """Create a DataBlock object based on the type specified in the tag.

    Args:
      edid: The list of bytes that make up the EDID.
      start: Index of the first byte of the data block.

    Returns:
      A DataBlock object.
    """
    tag = (edid[start] >> 5) & 0x07
    length = edid[start] & 0x1F

    block = edid[start : (start + length + 1)]

    if tag == 0x00:
        return DataBlock(block, DB_TYPE_RESERVED)
    if tag == 0x01:
        return AudioBlock(block)
    if tag == 0x02:
        return VideoBlock(block, DB_TYPE_VIDEO)
    if tag == 0x03:
        return VendorSpecificBlock(block, DB_TYPE_VENDOR_SPECIFIC)
    if tag == 0x04:
        return SpeakerBlock(block)
    if tag == 0x05:
        return DataBlock(block, DB_TYPE_VESA_DISPLAY_TRANSFER_CHAR)
    if tag == 0x06:
        return DataBlock(block, DB_TYPE_RESERVED)
    if tag == 0x07:
        ext_tag = edid[start + 1]
        if ext_tag == 0x00:
            return VideoCapabilityBlock(block)
        if ext_tag == 0x01:
            return VendorSpecificBlock(block, DB_TYPE_VENDOR_SPECIFIC_VIDEO)
        if ext_tag == 0x02:
            return DataBlock(block, DB_TYPE_VESA_DISPLAY_DEVICE)
        if ext_tag == 0x03:
            return DataBlock(block, DB_TYPE_VESA_VIDEO_TIMING)
        if ext_tag == 0x04:
            return DataBlock(block, DB_TYPE_HDMI_VIDEO)
        if ext_tag == 0x05:
            return ColorimetryDataBlock(block)
        if ext_tag >= 0x06 and ext_tag <= 0x0C:
            return DataBlock(block, DB_TYPE_RESERVED)
        if ext_tag == 0x0D:
            return VideoFormatPrefBlock(block)
        if ext_tag == 0x0E:
            return VideoBlock(block, DB_TYPE_YCBCR420_VIDEO)
        if ext_tag == 0x0F:
            return YCBCR420CapabilityMapBlock(block)
        if ext_tag == 0x10:
            return DataBlock(block, DB_TYPE_MISC_AUDIO_FIELDS)
        if ext_tag == 0x11:
            return VendorSpecificBlock(block, DB_TYPE_VENDOR_SPECIFIC_AUDIO)
        if ext_tag == 0x12:
            return DataBlock(block, DB_TYPE_HDMI_AUDIO)
        if ext_tag >= 0x13 and ext_tag <= 0x1F:
            return DataBlock(block, DB_TYPE_RESERVED)
        if ext_tag == 0x20:
            return InfoFrameDataBlock(block)
        if ext_tag >= 0x21 and ext_tag <= 0xFF:
            return DataBlock(block, DB_TYPE_RESERVED)

    return DataBlock(block, DB_TYPE_UNKNOWN)


class DataBlock(object):
    """Defines a basic Data Block object, with length, type, etc."""

    def __init__(self, block: ByteList, my_type: str):
        """Create a basic DataBlock object.

        Args:
          block: The list of bytes that make up the data block.
          my_type: The specific type of Data Block.
        """
        self._block: Final[ByteList] = block
        self._type: Final[str] = my_type

    def GetBlock(self) -> ByteList:
        """Fetch the list of bytes that make up the data block.

        Returns:
          A list of bytes that make up the data block.
        """
        return self._block

    @property
    def type(self) -> str:
        """Fetch the Data Block type.

        Returns:
          A string that denotes the Data Block type.
        """
        return self._type

    @property
    def length(self) -> int:
        """Fetch the length of this data block.

        Length is the number of bytes that follow the initial tag byte.

        Returns:
          An integer that indicates the length of the data block.
        """
        return self._block[0] & 0x1F

    @property
    def tag(self) -> int:
        """Fetch the tag of the data block.

        Returns:
          An integer that is the tag of the data block and indicates the type.
        """
        return (self._block[0] >> 5) & 0x07

    @property
    def ext_tag(self) -> Optional[int]:
        """Fetch the extended tag of the data block.

        The extended tag only exists if the original tag was equal to 7.

        Returns:
          An integer that is the extended tag of the data block, or None if the
          tag is not 7 (denoting no extension tag).
        """
        return self._block[1] if self.tag == 7 else None

    def GetBlob(self) -> ByteList:
        """Fetch the data blob of the data block.

        Returns:
          A list that holds the data in the rest of the block.
        """
        return self._block[1 : self.length + 1]


class AudioBlock(DataBlock):
    """Defines an Audio Data Block."""

    def __init__(self, block: ByteList):
        """Create an AudioBlock object.

        Args:
          block: The list of bytes that make up the audio block.
        """
        DataBlock.__init__(self, block, DB_TYPE_AUDIO)

    @property
    def short_audio_descriptors(self) -> List["ShortAudioDescriptor"]:
        """Fetch the short audio descriptors in the audio block.

        Returns:
          A list of ShortAudioDescriptor objects.
        """
        sads = []

        for x in range(1, len(self._block) - 2, 3):
            # Create a 3-byte chunk and send to ShortAudioDescriptor
            # TODO(chromium:395947): Double check number of SADs in audio block.
            sads.append(self._GetSad(self._block[x : (x + 3)]))

        return sads

    def _GetSad(self, block: ByteList) -> "ShortAudioDescriptor":
        """Fetch a single Short Audio Descriptor.

        Args:
          block: The 3-byte list that makes up a single short audio descriptor.

        Returns:
          A ShortAudioDescriptor object.
        """
        code = (block[0] >> 3) & 0x0F

        if code == 0x01:
            return AudioDescriptorLpcm(block, AUDIO_TYPE_LPCM)

        if code == 0x02:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_AC3)
        if code == 0x03:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_MPEG1)
        if code == 0x04:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_MPG3)
        if code == 0x05:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_MPEG2)
        if code == 0x06:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_AAC_LC)
        if code == 0x07:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_DTS)
        if code == 0x08:
            return AudioDescriptorBitRate(block, AUDIO_TYPE_ATRAC)

        if code == 0x09:
            return AudioDescriptorOther(block, AUDIO_TYPE_ONE_BIT)
        if code == 0x0A:
            return AudioDescriptorOther(block, AUDIO_TYPE_E_AC3)
        if code == 0x0B:
            return AudioDescriptorOther(block, AUDIO_TYPE_DTS_HD)
        if code == 0x0C:
            return AudioDescriptorOther(block, AUDIO_TYPE_MAT)
        if code == 0x0D:
            return AudioDescriptorOther(block, AUDIO_TYPE_DST)
        if code == 0x0E:
            return AudioDescriptorOther(block, AUDIO_TYPE_WMA_PRO)

        if code == 0x0F:
            ext_code = (block[2] >> 3) & 0x1F
            if ext_code == 0x04:
                return AudioDescriptorExtendedMpeg4(block, AUDIO_TYPE_MPEG4_HE_AAC)
            if ext_code == 0x05:
                return AudioDescriptorExtendedMpeg4(block, AUDIO_TYPE_MPEG4_HE_AAC_V2)
            if ext_code == 0x06:
                return AudioDescriptorExtendedMpeg4(block, AUDIO_TYPE_MPEG4_AAC_LC)
            if ext_code == 0x07:
                return AudioDescriptorExtendedDra(block, AUDIO_TYPE_DRA)
            if ext_code == 0x08:
                return AudioDescriptorExtendedMpeg4(block, AUDIO_TYPE_MPEG4_HE_AAC_MPS)
            if ext_code == 0x0A:
                return AudioDescriptorExtendedMpeg4(block, AUDIO_TYPE_MPEG4_AAC_LC_MPS)

        return ShortAudioDescriptor(block, AUDIO_TYPE_UNKNOWN)


class ShortAudioDescriptor(object):
    """Defines a Short Audio Descriptor within an Audio Data Block."""

    # Expects a 3 byte block
    def __init__(self, block: ByteList, my_type: str):
        """Create a basic ShortAudioDescriptor object.

        Args:
          block: The list of bytes that make up the Short Audio Descriptor.
          my_type: The type of Short Audio Descriptor.
        """
        self._block: Final[ByteList] = block
        self._type: Final[str] = my_type

    @property
    def format_code(self) -> int:
        """Fetch the format code of the short audio descriptor.

        Returns:
          An integer that denotes the format code of the short audio descriptor.
        """
        return (self._block[0] >> 3) & 0x1F

    @property
    def max_channel_count(self) -> int:
        """Fetch the maximum channel count.

        Returns:
          An integer that denotes the maximum channel count.
        """
        return (self._block[0] & 0x07) + 1

    @property
    def type(self) -> str:
        """Fetch the type of short audio descriptor.

        Returns:
          A string that indicates the type of short audio descriptor.
        """
        return self._type

    @property
    def supported_sampling_freqs(self) -> BoolDict:
        """Fetch a list of supported sampling frequencies.

        Note that extended SADs will never support 192 kHz or 176.4 kHz (see list
        of frequencies in __init__).
        However, those bits are set to 0 so will never translate as supported.

        Returns:
          A dict of string constants and bools that indicate sampling frequencies
          and whether each one is supported.
        """
        return tools.DictFilter(FREQS, self._block[1] & 0x7F)


class AudioDescriptorLpcm(ShortAudioDescriptor):
    """Defines a LPCM Short Audio Descriptor inside Audio Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create an AudioDescriptorLpcm object.

        Args:
          block: The list of bytes that make up the Short Audio Descriptor.
          my_type: A string that indicates this SAD is an LPCM SAD.
        """
        ShortAudioDescriptor.__init__(self, block, my_type)

    @property
    def bit_depth(self) -> BoolDict:
        """Fetch the supported bit depths.

        Returns:
          A dict of strings and bools that indicate bit depths and whether each one
          is supported.
        """
        return tools.DictFilter(AUDIO_BITS, self._block[2] & 0x07)


class AudioDescriptorBitRate(ShortAudioDescriptor):
    """Defines a BitRate Short Audio Descriptor inside Audio Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create a AudioDescriptorBitRate object.

        Args:
          block: The list of bytes that make up the Short Audio Descriptor.
          my_type: A string that indicates this SAD is a Bit Rate SAD.
        """
        ShortAudioDescriptor.__init__(self, block, my_type)

    @property
    def max_bit_rate(self) -> str:
        """Fetch the maximum bit rate.

        Returns:
          A string that indicates the maximum bit rate.
        """
        return "%d kHz" % (self._block[2] * 8)


class AudioDescriptorOther(ShortAudioDescriptor):
    """Defines nonspecialized Short Audio Descriptor inside Audio Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create a nonspecialized AudioDescriptorOther object.

        Args:
          block: The list of bytes that make up the Short Audio Descriptor.
          my_type: A string that indicates the type of this SAD.
        """
        ShortAudioDescriptor.__init__(self, block, my_type)

    @property
    def value(self) -> int:
        """Fetch the value of the Audio Descriptor, stored in the 3rd byte.

        Returns:
          An integer that indicates the value of the Audio Descriptor.
        """
        return self._block[2]


class AudioDescriptorExtendedMpeg4(ShortAudioDescriptor):
    """Defines Extended MPEG4 Short Audio Descriptor inside Audio Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create an AudioDescriptorExtendedMpeg4 object.

        Args:
          block: The list of bytes that make up the Extended MPEG 4 SAD.
          my_type: A string that indicates this SAd is an Extended MPEG 4 SAD.
        """
        ShortAudioDescriptor.__init__(self, block, my_type)

    @property
    def ext_code(self) -> int:
        """Fetch the extension code.

        Returns:
          The integer that indicates the extension code.
        """
        return (self._block[2] >> 3) & 0x1F

    @property
    def frame_length(self) -> str:
        """Fetch the frame length.

        Returns:
          A string that indicates frame length.
        """
        if self._block[2] & 0x4:
            return "1024"
        if self._block[2] & 0x2:
            return "960"
        else:
            return "Undefined"
        # TODO(chromium:395947): Check if exactly one bit is set.

    @property
    def mps_support(self) -> Optional[str]:
        """Fetch whether MPS is supported.

        Returns:
          A string that indicates whether MPS supported is explicitly stated,
          implicitly stated, or not specified at all.
        """
        if self.ext_code in (0x08, 0x0A):
            if self._block[2] & 0x1:
                return MPS_EXPLICIT
            else:
                return MPS_IMPLICIT
        else:  # for 4-6
            return None


class AudioDescriptorExtendedDra(ShortAudioDescriptor):
    """Defines Extended DRA Short Audio Descriptor inside Audio Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create an AudioDescriptorExtendedDra object.

        Args:
          block: The list of bytes that make up the SAD.
          my_type: A string that indicates this SAD is an Extended DRA.
        """
        ShortAudioDescriptor.__init__(self, block, my_type)

    @property
    def ext_code(self) -> int:  # Should always return 7
        """Fetch the extension code.

        Returns:
          An integer that indicates the extension code.
        """
        return (self._block[2] >> 3) & 0x1F

    @property
    def value(self) -> int:
        """Fetch the value of the DRA SAD.

        Returns:
          An integer that indicates the value of the DRA SAD.
        """
        return self._block[2] & 0x07


class VideoBlock(DataBlock):
    """Defines a Video Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create a VideoBlock object.

        Args:
          block: The list of bytes that make up the data block.
          my_type: A string that indicates the type of this VideoBlock.
        """
        DataBlock.__init__(self, block, my_type)
        self._offset = 1 if self.ext_tag else 0

    @property
    def short_video_descriptors(self) -> List["ShortVideoDescriptor"]:
        """Fetch the short video descriptors.

        Returns:
          A list of short video descriptors (strings).
        """
        svds = []

        for x in range(self._offset + 1, len(self._block)):
            svds.append(ShortVideoDescriptor(self._block[x]))

        return svds


class ShortVideoDescriptor(object):
    """Defines a Short Video Descriptor."""

    def __init__(self, byte: int):
        """Create a ShortVideoDescriptor object.

        Args:
          byte: The single byte that codes for the Short Video Descriptor.
        """
        self._byte = byte

    @property
    def nativity(self) -> str:
        """Fetch the nativity of the Short Video Descriptor.

        Nativity options include SVD_NATIVE, SVD_NONNATIVE, and SVD_UNSPECIFIED.

        Returns:
          A string indicating the nativity of the Short Video Descriptor.
        """
        if 1 <= self._byte <= 64:
            return SVD_NONNATIVE
        if 129 <= self._byte <= 192:
            return SVD_NATIVE
        else:
            return SVD_UNSPECIFIED

    @property
    def vic(self) -> int:
        """Fetch the Video Identification code for the Short Video Descriptor.

        Returns:
          An integer representing the Video Identification Code.
        """
        if 1 <= self._byte <= 64 or 129 <= self._byte <= 192:
            return self._byte & 0x7F
        return self._byte


class VendorSpecificBlock(DataBlock):
    """Defines a Vendor Specific Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create a VendorSpecificBlock object.

        Args:
          block: The list of bytes that make up the data block.
          my_type: A string that indicates that this Data Block is Vendor Specific.
        """
        DataBlock.__init__(self, block, my_type)
        self._offset: Final[int] = 1 if self.ext_tag else 0

    @property
    def ieee_oui(self) -> str:
        """Fetch the IEEE Organizationally Unique Identifier.

        Returns:
          A string that indicates the IEEE OUI.
        """
        return "%02x-%02x-%02x" % (
            self._block[3 + self._offset],
            self._block[2 + self._offset],
            self._block[1 + self._offset],
        )

    @property
    def payload(self) -> ByteList:
        """Fetch the rest of the data in the Vendor Specific Block.

        Returns:
          A list of bytes in the Vendor Specific Block.
        """
        return self._block[(4 + self._offset) : len(self._block)]


class SpeakerBlock(DataBlock):
    """Defines a Speaker Data Block."""

    def __init__(self, block: ByteList):
        """Create a SpeakerBlock object.

        Args:
          block: The list of bytes that make up the data block.
        """
        DataBlock.__init__(self, block, DB_TYPE_SPEAKER_ALLOCATION)

    @property
    def allocation(self) -> BoolDict:
        """Fetch the speaker allocation.

        Returns:
          A dict of strings and bools indicating the speaker allocation.
        """
        alloc_bits = ((self._block[2] & 0x07) << 8) + self._block[1]
        return tools.DictFilter(SPEAKERS, alloc_bits)


class VideoCapabilityBlock(DataBlock):
    """Defines a Video Capability Data Block."""

    def __init__(self, block: ByteList):
        """Create a VideoCapabilityBlock object.

        Args:
          block: The list of bytes that make up the data block.
        """
        DataBlock.__init__(self, block, DB_TYPE_VIDEO_CAPABILITY)

    @property
    def selectable_quantization_range_ycc(self) -> bool:
        """Fetch the selectability of YCbCr quantization range.

        Returns:
          A boolean indicating whether YCC quantization range is selectable via
          AVI YQ.
        """
        return bool(self._block[2] >> 7)

    @property
    def selectable_quantization_range_rgb(self) -> bool:
        """Fetch the selectability of RGB quantization range.

        Returns:
          A boolean indicating whether RGB quantization range is selectable via
          AVI Q.
        """
        return bool((self._block[2] >> 6) & 0x01)

    @property
    def pt_behavior(self) -> OverscanBehavior:
        """Fetch the PT behavior - preferred timing overscan/underscan.

        Returns:
          A string describing the PT behavior.
        """
        pt = (self._block[2] >> 4) & 0x03
        if pt == 0x00:
            return OU_UNDEFINED
        if pt == 0x01:
            return OU_OVERSCAN
        if pt == 0x02:
            return OU_UNDERSCAN
        assert pt == 0x03
        return OU_BOTH

    @property
    def it_behavior(self) -> OverscanBehavior:
        """Fetch the IT application specific display overscan/underscan behavior.

        IT application specific display may, for example, be computer display.

        Returns:
          A string describing the IT behavior.
        """
        it = (self._block[2] >> 2) & 0x03
        if it == 0x00:
            return OU_NOT_SUPPORTED
        if it == 0x01:
            return OU_OVERSCAN
        if it == 0x02:
            return OU_UNDERSCAN
        assert it == 0x03
        return OU_BOTH

    @property
    def ce_behavior(self) -> OverscanBehavior:
        """Fetch the CE application specific display overscan/underscan behavior.

        CE application specific display may, for example, be DTV.

        Returns:
          A string describing the CE behavior.
        """
        ce = self._block[2] & 0x03
        if ce == 0x00:
            return OU_NOT_SUPPORTED
        if ce == 0x01:
            return OU_OVERSCAN
        if ce == 0x02:
            return OU_UNDERSCAN
        assert ce == 0x03
        return OU_BOTH


class ColorimetryDataBlock(DataBlock):
    """Defines a Colorimetry Data Block."""

    def __init__(self, block: ByteList):
        """Create a ColorimetryDataBlock object.

        Args:
          block: The list of bytes that make up the data block.
        """
        DataBlock.__init__(self, block, DB_TYPE_COLORIMETRY)

    @property
    def colorimetry(self) -> BoolDict:
        """Fetch the colorimetry.

        Returns:
          A dict of strings and bools indicating the colorimetry.
        """
        return tools.DictFilter(COLORS, self._block[2])

    @property
    def metadata(self) -> int:
        """Fetch the additional metadata.

        Metadata is stored in the least significant 4 bits of the 4th byte.

        Returns:
          An integer indicating the additionally specified metadata.
        """
        return self._block[3] & 0x0F


class VideoFormatPrefBlock(DataBlock):
    """Defines a Video Format Preference Data Block."""

    def __init__(self, block: ByteList):
        """Create a VideoFormatPrefBlock object.

        Args:
          block: The list of bytes that make up the data block.
        """
        DataBlock.__init__(self, block, DB_TYPE_VIDEO_FORMAT_PREFERENCE)

    @property
    def video_preferences(self):
        """Fetch the video preferences.

        Calls on the video_block module to translate short video descriptor codes
        into supported video preferences.

        Returns:
          A list of VideoPreference objects indicating the video preferences.
        """
        prefs = []

        for x in range(2, len(self._block)):
            svr = self._block[x]
            if (svr in [0, 128, 254, 255]) or (svr >= 145 and svr <= 192):
                prefs.append(VideoPreferenceReserved(svr))
            elif svr >= 129 and svr <= 144:
                prefs.append(VideoPreferenceDtd(svr))
            else:
                prefs.append(VideoPreferenceVic(svr))

        return prefs


class VideoPreference(object):
    """Defines a Video Preference object."""

    def __init__(self, byte, atype):
        """Create a VideoPreference object.

        Args:
          byte: The single byte that codes for the Video Preference object.
          atype: The string that indicates the type of the Video Preference object.
        """
        self._byte = byte
        self._type = atype

    def GetSvr(self):
        """Fetch the Short Video Reference value.

        Returns:
          An integer indicating the Short Video Reference.
        """
        return self._byte

    @property
    def type(self):
        """Fetch the type of the Video Preference object.

        Returns:
          A string indicating the type of the Video Preference object.
        """
        return self._type


class VideoPreferenceVic(VideoPreference):
    """Defines a Video Preference VIC object."""

    def __init__(self, byte):
        """Create a Video Preference VIC object.

        Args:
          byte: The single byte that codes for the Video Preference object.
        """
        VideoPreference.__init__(self, byte, VIDEO_PREFERENCE_VIC)

    @property
    def vic(self):
        """Fetch the Video Identification Code value.

        Returns:
          An integer specifying the Video Identification Code value.
        """
        return self._byte


class VideoPreferenceDtd(VideoPreference):
    """Defines a Video Preference DTD object."""

    def __init__(self, byte):
        """Create a Video Preference DTD object.

        Args:
          byte: The single byte that codes for the Video Preference object.
        """
        VideoPreference.__init__(self, byte, VIDEO_PREFERENCE_DTD)

    @property
    def dtd_index(self):
        """Fetch the DTD index.

        Returns:
          An integer (1-16) specifying the DTD index.
        """
        return self._byte - 128


class VideoPreferenceReserved(VideoPreference):
    """Defines a Video Preference Reserved object."""

    def __init__(self, byte):
        """Create a Video Preference Reserved object.

        Args:
          byte: The single byte that codes for the Video Preference object.
        """
        VideoPreference.__init__(self, byte, VIDEO_PREFERENCE_RESERVED)

    @property
    def svr(self):
        """Fetch the Short Video Reference.

        Returns:
          An integer specifying the Short Video Reference.
        """
        return self._byte


class YCBCR420CapabilityMapBlock(DataBlock):
    """Defines a YCbCr 4:2:0 Capability Map Data Block."""

    def __init__(self, block: ByteList):
        """Create a YCBCR420CapabilityMapBlock object.

        Args:
          block: The list of bytes that make up the data block.
        """
        DataBlock.__init__(self, block, DB_TYPE_YCBCR420_CAPABILITY_MAP)

    @property
    def supported_descriptor_indices(self):
        """Fetch the indices of the SVDs that support YCbCr 4:2:0.

        Returns:
          A single string indicating that all SVDs support YCbCr, or a list of
          the indices of the SVDs that support it.
        """
        if len(self._block) == 2:
            return "All SVDs support YCbCr4:2:0"

        supported = []
        index = 0

        for x in range(2, len(self._block)):
            byte = self._block[x]
            for _ in range(0, 8):
                if byte & 0x01:
                    supported.append(index)
                byte >>= 1
                index += 1

        return supported


class InfoFrameDataBlock(DataBlock):
    """Defines an InfoFrame Data Block."""

    def __init__(self, block: ByteList):
        """Create a basic InfoFrameDataBlock object.

        Args:
          block: The list of bytes that make up the data block.
        """
        DataBlock.__init__(self, block, DB_TYPE_INFO_FRAME)

    @property
    def if_processing(self):
        """Fetch the InfoFrame Processing Descriptor.

        Returns:
          An InfoFrame Processing Descriptor object.
        """
        return InfoFrameProcessingDescriptor(self._block[2:])

    @property
    def vsifs(self):
        """Fetch the Vendor-Specific InfoFrame.

        Returns:
          A list of InfoFrameDescriptor objects.
        """
        vsifs = []

        start = 2 + 2 + self.if_processing.payload_length

        while start < len(self._block):
            vsif = self._GetVsif(self._block[start:])
            if start + vsif.payload_length + 1 <= len(self._block):
                vsifs.append(vsif)
            start += vsif.payload_length + 1

        return vsifs

    def _GetVsif(
        self, new_block: ByteList
    ) -> Union["InfoFrameVendorSpecific", "InfoFrameDescriptor"]:
        """Fetch a single InfoFrameDescriptor object.

        Args:
          new_block: The list of bytes that make up a single InfoFrame Descriptor.

        Returns:
          A single InfoFrameDescriptor object.
        """
        code = new_block[0] & 0x1F
        if code == 0x01:
            return InfoFrameVendorSpecific(new_block)

        if code == 0x02:
            return InfoFrameDescriptor(new_block, INFO_FRAME_TYPE_AUX_VIDEO_INFO)
        if code == 0x03:
            return InfoFrameDescriptor(new_block, INFO_FRAME_TYPE_SOURCE_PRODUCT)
        if code == 0x04:
            return InfoFrameDescriptor(new_block, INFO_FRAME_TYPE_AUDIO)
        if code == 0x05:
            return InfoFrameDescriptor(new_block, INFO_FRAME_TYPE_MPEG_SOURCE)
        if code == 0x06:
            return InfoFrameDescriptor(new_block, INFO_FRAME_TYPE_NTSC_VBI)
        else:
            return InfoFrameDescriptor(new_block, INFO_FRAME_TYPE_UNKNOWN)


class InfoFrameDescriptor(object):
    """Defines an InfoFrameDescriptor inside InfoFrame Data Block."""

    def __init__(self, block: ByteList, my_type: str):
        """Create an InfoFrameDescriptor object.

        Args:
          block: The list of bytes that make up the InfoFrame Descriptor.
          my_type: The string that indicates the type of the InfoFrame Descriptor.
        """
        self._block: Final[ByteList] = block
        self._type: Final[str] = my_type

    @property
    def type_code(self):
        """Fetch the type code.

        Returns:
          An integer representing the type of InfoFrameDescriptor.
        """
        return self._block[0] & 0x1F

    @property
    def type(self):
        """Fetch the type.

        Returns:
          A string describing the type of InfoFrameDescriptor.
        """
        return self._type

    @property
    def payload_length(self):
        """Fetch the length of the data payload.

        Returns:
          An integer indicating the length of the data payload.
        """
        return (self._block[0] >> 5) & 0x07

    @property
    def payload(self):
        """Fetch the data payload.

        Returns:
          A list of bytes that make up the data payload; may be an empty list.
        """
        return self._block[1 : self.payload_length + 1]


class InfoFrameProcessingDescriptor(InfoFrameDescriptor):
    """Defines an InfoFrame Processing Descriptor Header."""

    def __init__(self, block: ByteList):
        """Create an InfoFrameProcessingDescriptor object.

        Args:
          block: The list of bytes that make up the InfoFrameProcessingDescriptor.
        """
        InfoFrameDescriptor.__init__(self, block, INFO_FRAME_TYPE_PROCESSING)

    @property
    def vsif_count(self):
        """Fetch the number of additional VSIFs that can be received at once.

        Returns:
          An integer that indicates the number of additional VSIFs that can be
          received simultaneously.
        """
        return self._block[1]


class InfoFrameVendorSpecific(InfoFrameDescriptor):
    """Defines InfoFrame Vendor Specific Desc inside InfoFrame Data Block."""

    def __init__(self, block: ByteList):
        """Create an InfoFrameVendorSpecific object.

        Args:
          block: The list of bytes that make up the InfoFrameDescriptor.
        """
        InfoFrameDescriptor.__init__(self, block, INFO_FRAME_TYPE_VENDOR_SPECIFIC)

    @property
    def ieee_oui(self):
        """Fetch the IEEE Organizationally Unique Identifier.

        Returns:
          A string that indicates the IEEE OUI.
        """
        return "%02x-%02x-%02x" % (self._block[3], self._block[2], self._block[1])
