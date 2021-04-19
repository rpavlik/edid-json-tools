#!/usr/bin/env python3

# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause

####################################################
# EDID Parser
# Takes in binary blob EDID
# This parser is primarily based on the following:
# 1. "VESA Enhanced Extended Display Identification Data Standard", Release A,
#   Revision 2, Sept. 25, 2006.
# 2. "A DTV Profile for Uncompressed High Speed Digital Interfaces",
#   ANSI/CEA-861-F, Aug., 2013.
# 3. HDMI spec.
####################################################

"""Parses EDID and establishes command line options for EDID analysis."""

from edid_json_tools.edidparser_argparse import ParseEdid

# The body of this script has been moved into the module itself.

####################
# CODE STARTS HERE #
####################
if __name__ == '__main__':
  ParseEdid()
