# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause
"""Click-based command line interfaces for the main conversion features."""

import json
import sys

import click

from .edid2json import ParseEdid
from .json2edid import JsonToBinary


@click.command()
@click.option('--ignore-errors/--no-ignore-errors',
  'ignore_errors',
  help='Whether errors in the conformance/validity of the input EDID will be'
  ' ignored or will prevent an output file from being generated.',
  show_default=True,
  default=False)
@click.argument('edid_file',
  type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
def edid2json(ignore_errors, edid_file):
  """Takes in binary EDID_FILE, parses it into a JSON object,
  and prints it to the stdout."""
  edid_json = ParseEdid(edid_file, ignore_errors)
  if edid_json:
    print(json.dumps(edid_json, sort_keys=True, indent=4))
  else:
    sys.stderr.write(
        "\n\nTo attempt to output JSON despite these errors, try again "
        "using the --ignore-errors flag\n")
    sys.exit(1)


@click.command()
@click.argument('json_file',
  type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('edid_file',
  type=click.Path(file_okay=True, dir_okay=False, writable=True))
def json2edid(json_file, edid_file):
  """Loads in JSON_FILE describing an EDID,
  and writes the corresponding binary EDID_FILE."""
  JsonToBinary(json_file, edid_file)
