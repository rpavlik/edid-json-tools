#!/usr/bin/env python3

# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause

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

# The body of this script has been moved into the module itself.

import json
import sys

from edid_json_tools.edid2json import ParseEdid

_USAGE = """
Usage: %s <inputfile>

The program takes an EDID file, organizes it into a JSON object and prints
it out in the stdout.
"""

####################
# CODE STARTS HERE #
####################
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(_USAGE % sys.argv[0])
    else:
        edid_json = ParseEdid(sys.argv[1])
        if edid_json:
            print(json.dumps(edid_json, sort_keys=True, indent=4))
