# EDID JSON Tools

This is a collection of tools that helps you work with EDID files, by parsing
them as well as by converting between EDID binaries and JSON files.

As a tool to generate EDID binary from a text format (JSON), it is one of the
only EDID editing tools I've found that fits in a code-based workflow. As open
source software, it is open to be extended and adapted as needed.

## Dependencies

This tool uses Python 3.

The "nice" command line interfaces use Click (7.x): this is optional if you just
want the capabilities of this package in a Python module, rather than a
standalonen command.

## Included tools

If you install this package using pip, like:

```sh
python3 -m pip install --editable .[CLI]
```

you will get automatically-created executable wrappers for nicer command line
interfaces. The `[CLI]` part indicates you want the optional command-line
interface dependencies (Click), and not just the bare Python module for use in
other Python code.

### edid2json

This tool takes a filename of an EDID binary on the command line, and prints out
a representation of its contents in JSON format on standard out. This can be
manipulated to edit an EDID when used in combination with the next tool.

The `edid2json.py` script in the root directory of this repo is deprecated:
prefer installing with setuptools/pip which will give you access to the
Click-based CLI for `edid2json` which allows you to continue even if parse
errors occurred, etc. (The old script in the root of this repo does
not require Click.)

### json2edid

This tool takes a JSON filename and an output binary filename. The JSON file
should be in the format outputted by `edid2json`. It will generate a valid
EDID binary file from that JSON, save it to the specified filename, and output a
hexidecimal representation to standard out.

The `json2edid.py` script in the root directory of this repo is deprecated:
prefer installing with setuptools/pip which will give you access to the
Click-based CLI for `json2edid`. (The old script in the root of this repo does
not require Click.)

### edidparser.py

This is a multi-purpose tool that can load an EDID binary file and display a
variety of data about it. Sub-commands include:

- verify
- version
- hex
- dec
- xc (extension count)
- parse

If you install this package, you will get an `edidparser` launcher script
created, which just wraps what this (now very small) Python script in the root
directory of the repo does. It uses `argparse` instead of bare `sys.argv` usage,
so it has not yet been converted to use Click.

## History

This began as a small fork of a single subdirectory from the "chameleon"
ChromiumOS repository. The history of that subdirectory of the repo has been
extracted and retained in this repository. Original code is at
<https://chromium.googlesource.com/chromiumos/platform/chameleon> in the `tools`
subdirectory: the `chameleon_fork_point` tag in this project corresponds to the
code at the same point as the upstream commit
<https://chromium.googlesource.com/chromiumos/platform/chameleon/+/2a67bd8a0bbb4a7533670129d1b7beb4a8845438>.
Upstream has been mostly dormant since 2014 except for a late 2020 Python 3
migration that had already been done in this fork of the project. We remain
grateful for their awesome work putting together the foundation of this tool.

The license is a 3-clause BSD license, from the original "chameleon" source code
that gave rise to this project.
