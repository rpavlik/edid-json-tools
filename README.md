# cros-chameleon EDID tools

This is a small fork of a single subdirectory from the "chameleon" ChromiumOS repository.
It contains tools (in Python) that can convert between EDID binaries and a JSON representation.

Original code is at <https://chromium.googlesource.com/chromiumos/platform/chameleon>

## Included tools

### edidparser.py

This is a multi-purpose tool that can load an EDID binary file and display a variety of data about it. Sub-commands include:

- verify
- version
- hex
- dec
- xc (extension count)
- parse

### edid2json.py

(Formerly `jsonedid`)

This tool takes a filename of an EDID binary on the command line, and prints out
a representation of its contents in JSON format on standard out.
This can be manipulated to edit an EDID when used in combination with the next tool.

### json2edid.py

(Formerly `jsonparser`)

This tool takes a JSON filename and an output binary filename.
The JSON file should be in the format outputted by `edid2json.py`.
It will generate a valid EDID binary file from that JSON,
save it to the specified filename, and output a hexidecimal representation
to standard out.

## Changes

- Bugfixes (typo fixes)
- Port to Python 3
- Rename files to more logical names
