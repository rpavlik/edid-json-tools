#!/usr/bin/env python3

# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause

# TODO(chromium:395947): Share strings and options with jsonedid
# TODO(chromium:395947): Add JSON validation


"""Create an EDID binary blob out of a Json representation of an EDID."""

# The body of this script has been moved into the module itself.


import sys

from edid_json_tools.json2edid import JsonToBinary

_USAGE = """
Usage: %s <inputfile> <outputfile>

The program takes a text file which contains an EDID in the JSON format and
produces the EDID in the binary form.
"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(_USAGE % sys.argv[0])
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        JsonToBinary(input_file, output_file)
