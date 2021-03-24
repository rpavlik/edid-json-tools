# EDID JSON Tools

This is a collection of tools that helps you work with EDID files, by parsing
them as well as by converting between EDID binaries and JSON files.

As a tool to generate EDID binary from a text format (JSON), it is one of the
only EDID editing tools I've found that fits in a code-based workflow. As open
source software, it is open to be extended and adapted as needed.

## Dependencies

This tool uses Python 3.

## Included tools

### edid2json.py

This tool takes a filename of an EDID binary on the command line, and prints out
a representation of its contents in JSON format on standard out. This can be
manipulated to edit an EDID when used in combination with the next tool.

### json2edid.py

(Formerly `jsonparser`)

This tool takes a JSON filename and an output binary filename. The JSON file
should be in the format outputted by `edid2json.py`. It will generate a valid
EDID binary file from that JSON, save it to the specified filename, and output a
hexidecimal representation to standard out.

### edidparser.py

This is a multi-purpose tool that can load an EDID binary file and display a
variety of data about it. Sub-commands include:

- verify
- version
- hex
- dec
- xc (extension count)
- parse

## History

This began as a small fork of a single subdirectory from the "chameleon"
ChromiumOS repository. The history of that subdirectory of the repo has been
extracted and retained in this repository. Original code is at
<https://chromium.googlesource.com/chromiumos/platform/chameleon>

The license is a 3-clause BSD license, from the original "chameleon" source code
that gave rise to this project.
