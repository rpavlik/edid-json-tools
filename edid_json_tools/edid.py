# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause


"""Provides EDID class with methods for parsing info."""

import array
from edid_json_tools.typing import ByteList
from typing import List, Optional

from . import (
    basic_display,
    chromaticity,
    descriptor,
    error,
    error_check,
    established_timings,
    extensions,
    standard_timings,
)
from .descriptor import Descriptor


class Edid(object):
    """Defines methods and properties for accesing an EDID object's content."""

    def __init__(self, e: ByteList):
        """Create an Edid object with a list of bytes.

        Args:
          e: The list of bytes that make up this EDID.
        """
        self._edid = e

    def GetData(
        self, start: Optional[int] = None, end: Optional[int] = None
    ) -> ByteList:
        """Fetch the raw data for the entire or part of the EDID.

        Args:
          start: The index of the first element to include.
          end: The index of the first element to exclude.

        Returns:
          A list of bytes.
        """
        return self._edid[start:end]

    @property
    def manufacturer_id(self) -> str:
        """Fetch the manufacturer ID.

        Returns:
          A three letter string that represents the manufacturer ID.
        """
        manu_id = (self._edid[0x08] << 8) + self._edid[0x09]

        c1 = self._ConvertToLetter((manu_id >> 10) & 0x1F)
        c2 = self._ConvertToLetter((manu_id >> 5) & 0x1F)
        c3 = self._ConvertToLetter(manu_id & 0x1F)

        return c1 + c2 + c3

    @property
    def product_code(self) -> int:
        """Fetch the ID Product code.

        This code is used to differentiate between different models from the same
        manufacturer (i.e., a model number). Bytes 10-11, little endian.

        Returns:
          An integer denoting the product code.
        """
        return (self._edid[0x0B] << 8) + self._edid[0x0A]

    @property
    def serial_number(self) -> Optional[int]:
        """Fetch the serial number.

        Used to differentiate between instances of the same display model.

        Returns:
          An integer denoting serial number or None.
        """
        sn = 0
        sn += self._edid[0x0F] << 24
        sn += self._edid[0x0E] << 16
        sn += self._edid[0x0D] << 8
        sn += self._edid[0x0C]

        return sn if sn else None

    @property
    def manufacturing_week(self) -> Optional[int]:
        """Fetch the week of manufacturing.

        Returns:
          None, if unspecified, or an integer indicating the week number.
        """
        if self._edid[0x10] in [0, 255]:
            return None
        else:
            return self._edid[0x10]

    @property
    def manufacturing_year(self) -> Optional[int]:
        """Fetch the year of manufacturing.

        Returns:
          None, if unspecified, or an integer indicating the year.
        """
        if self._edid[0x10] == 255:
            return None
        else:
            return self._edid[0x11] + 1990

    @property
    def model_year(self) -> Optional[int]:
        """Fetch the model year.

        Model year is only specified if week is set to 255.

        Returns:
          None, if unspecified, or an integer indicating the model year.
        """
        if self._edid[0x10] == 255:
            return self._edid[0x11] + 1990
        else:
            return None

    @property
    def extension_count(self) -> int:
        """Fetch the number of extensions in this EDID.

        Returns:
          An integer denoting the number of extensions.
        """
        return self._edid[0x7E]

    def _ConvertToLetter(self, b) -> str:
        """Convert a 5-digit binary number into a letter.

        Called when printing manufacturing info.

        Args:
          b: The binary number being converted into a character.

        Returns:
          A single character (upper-case letter).
        """
        return chr(b + 64)

    @property
    def edid_version(self) -> str:
        """Fetch the EDID version (1.3 or 1.4).

        Returns:
          A string indicating the EDID version.
        """
        return "%d.%d" % (self._edid[0x12], self._edid[0x13])

    @property
    def basic_display(self) -> basic_display.BasicDisplay:
        """Fetch the Basic Display information in this EDID.

        Returns:
          A basic_display.BasicDisplay object.
        """
        return basic_display.BasicDisplay(self._edid, self.edid_version)

    @property
    def chromaticity(self) -> chromaticity.Chromaticity:
        """Fetch the Chromaticity information in this EDID.

        Returns:
          A chromaticity.Chromaticity object.
        """
        return chromaticity.Chromaticity(self._edid)

    @property
    def established_timings(self) -> established_timings.EstablishedTimings:
        """Fetch the Established Timings information in this EDID.

        Returns:
          An established_timings.EstablishedTimings object.
        """
        return established_timings.EstablishedTimings(self._edid)

    @property
    def standard_timings(self) -> List[standard_timings.StandardTiming]:
        """Fetch the Standard Timing information in this EDID.

        Returns:
          A standard_timings.StandardTiming object.
        """
        base = 38
        sts = []
        for x in range(0, 8):
            st = standard_timings.GetStandardTiming(
                self._edid, (base + (x * 2)), self.edid_version
            )
            if st:
                sts.append(st)
        return sts

    def GetDescriptor(self, index: int) -> Descriptor:
        """Fetch a single Descriptor's information in this EDID.

        Args:
          index: The descriptor index (0-3) within the EDID.

        Returns:
          A single descriptor.Descriptor object.

        Raises:
          IndexError: If index is not in the range 0-3.
        """
        base = 54  # Descriptor blocks begin at byte 54 in base EDID
        return descriptor.GetDescriptor(
            self._edid, (base + (index * 18)), self.edid_version
        )

    @property
    def descriptors(self) -> List[Descriptor]:
        """Fetch all descriptors in a base EDID.

        Returns:
          A list of descriptor.Descriptor objects.
        """
        descs = []
        for x in range(0, 4):
            desc = self.GetDescriptor(x)
            if desc:
                descs.append(desc)
        return descs

    def GetExtension(self, index: int) -> extensions.Extension:
        """Fetch an Extension's information in this EDID.

        Args:
          index: The index of the extension (starting at 1).

        Returns:
          A single extensions.Extension object.
        """
        return extensions.GetExtension(self._edid, index, self.edid_version)

    def GetErrors(self) -> Optional[List[error.Error]]:
        """Check an EDID for errors by calling error_check module.

        Returns:
          A list of error.Error objects.
        """
        return error_check.GetErrors(self.GetData(), self.edid_version)

    def ConvertToBinary(self, filename: str):
        """Convert an EDID object into a binary blob.

        Args:
          filename: The string filename of the text file.
        """
        with open(filename, "wb") as myfile:
            blob = array.array("B", self._edid).tobytes()
            myfile.write(blob)
