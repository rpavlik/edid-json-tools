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


import argparse
import re

from . import edid
from .edidparser_impl import (LAYOUT_MODE, NORMAL_MODE, RAW_DEC, RAW_HEX,
                                 RAW_OFF, TYPE_ALL, TYPE_BASE, TYPE_XALL,
                                 VERBOSE_MODE, CheckInvalidTypes, PrintBase,
                                 PrintDecEdid, PrintExtensions, PrintHexEdid,
                                 PrintSpace, Verify, Version, Xc,
                                 type_help_string)
from .tools import BytesFromFile

# The body of this script has been moved into the module itself.


def ParseEdid():
  """Parse an EDID and print its info according to commands and flags."""
  p = argparse.ArgumentParser(description='Select sections of EDID to parse.')

  sp = p.add_subparsers(title='subcommands', description='valid subcommands',
                        metavar='')
  sp_verify = sp.add_parser('verify', help='Error check the EDID')
  sp_verify.set_defaults(func=Verify)
  sp_version = sp.add_parser('version', help='Print EDID version')
  sp_version.set_defaults(func=Version)
  sp_hex = sp.add_parser('hex', help='Print full EDID in hex')
  sp_hex.set_defaults(func=PrintHexEdid)
  sp_dec = sp.add_parser('dec', help='Print full EDID in decimal')
  sp_dec.set_defaults(func=PrintDecEdid)
  sp_xc = sp.add_parser('xc', help='Print extension count')
  sp_xc.set_defaults(func=Xc)
  sp_parse = sp.add_parser('parse', help='Parse full or sections of EDID.'
                           ' Run \'./edidparser.py parse -h\' for more info '
                           'on additional arguments.')

  # The following are all arguments for the parse subcommand
  parse_mode = sp_parse.add_mutually_exclusive_group()
  parse_mode.add_argument('-v', '--verbose', action='store_true',
                          help='Show detailed information')
  parse_mode.add_argument('-n', '--normal', action='store_true',
                          help='Show standard information')
  parse_mode.add_argument('-l', '--layout', action='store_true',
                          help='Show basic layout information')

  parse_raw = sp_parse.add_mutually_exclusive_group()
  parse_raw.add_argument('--hex', action='store_true',
                         help='Print raw data for each section in hex')
  parse_raw.add_argument('--dec', action='store_true',
                         help='Print raw data for each section in decimal')

  sp_parse.add_argument('-t', '--types', type=str, help=type_help_string)

  # Positional arguments: 1) EDID name
  p.add_argument('edid_name', type=str,
                 help='Name of EDID binary blob for parsing')

  args = p.parse_args()

  # Fill the edid list with bytes from binary blob
  e = edid.Edid(BytesFromFile(args.edid_name))

  print('Parsing %s' % args.edid_name)

  if hasattr(args, 'func'):  # Not the 'parse' subcommand
    args.func(e)
    exit()

  # Set defaults here
  mode = NORMAL_MODE
  raw_mode = RAW_OFF

  if args.layout:  # Layout of EDID only
    # Here, set the mode to layout mode
    # Run each analysis method but get back basic info only
    mode = LAYOUT_MODE

  elif args.verbose:
    # Here, set the mode to verbose mode
    mode = VERBOSE_MODE

  # Otherwise, mode remains NORMAL_MODE

  if args.dec:
    raw_mode = RAW_DEC

  elif args.hex:
    raw_mode = RAW_HEX

  if not args.types or TYPE_ALL in args.types.split(','):
    base_types = [TYPE_BASE]
    ext_types = [TYPE_XALL]

  else:
    base_types = args.types.split(',')
    regex = re.compile('(x).*')
    ext_types = [m.group(0) for t in base_types for m in [regex.search(t)] if m]
    CheckInvalidTypes(base_types, ext_types)

  print('EDID version: %s' % e.edid_version)
  PrintSpace()

  PrintBase(e, mode, raw_mode, base_types)
  PrintExtensions(e, mode, raw_mode, ext_types)


####################
# CODE STARTS HERE #
####################
if __name__ == '__main__':
  ParseEdid()
