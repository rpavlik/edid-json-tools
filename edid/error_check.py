# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Check EDID for errors, which could indicate invalid or faulty EDID.

If errors are found, returns error.Error objects that store information about
each error's location, message, expected data, and what data is found.
"""

from . import descriptor
from . import error
from . import extensions
from . import standard_timings


def _LengthError(e):
  """Check if the length of the EDID is a multiple of 128.

  Args:
    e: The list form of the EDID to be checked.

  Returns:
    A list of error.Error objects, or None.
  """
  if not len(e) % 128:
    return None
  else:
    return [error.Error('Overall EDID', 'Invalid length', 'Length % 128 = 0',
                        'Length %% 128 = %d' % (len(e) % 128))]


def _HeaderError(e):
  """Check if header (bytes 0-7) is set up properly.

  Header should be 0x00 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0x00.

  Args:
    e: The list form of the EDID to be checked.

  Returns:
    A list of error.Error objects, or None.
  """
  magic_header = [
      0x00,
      0xFF,
      0xFF,
      0xFF,
      0xFF,
      0xFF,
      0xFF,
      0x00
  ]

  header = '%02X%02X ' * 4 % tuple(e[0:8])

  if e[0:8] == magic_header:
    return None
  else:
    return [error.Error('Bytes 0-7', 'Incorrect EDID header',
                        '00FF FFFF FFFF FF00', header)]

  return None


def _ChecksumError(e):
  """Check if checksum is valid.

  Checksum for each 128-byte block should be divisible by 256.

  Args:
    e: The list form of the EDID to be checked.

  Returns:
    None, if no error, or a list of error.Error objects.
  """
  cs_errors = []

  for x in range(0, len(e), 128):

    my_sum = sum(e[x:(x + 128)])
    if my_sum % 256:
      block_id = x / 128
      my_err = error.Error('Block %d' % block_id, 'Checksum error',
                           'Sum % 256 = 0', 'Sum %% 256 = %d' % (my_sum % 256))
      cs_errors.append(my_err)

  return cs_errors


def _DescriptorErrors(edid, version):
  """Check the descriptor blocks for errors.

  Args:
    edid: The list form of the EDID to be checked.
    version: The string indicating the version of the EDID.

  Returns:
    A list of error.Error objects.
  """
  base = 54  # Descriptor blocks start at byte 54 in base EDID

  errors = []

  for x in range(0, 4):

    desc = descriptor.GetDescriptor(edid, base + (x * 18), version)

    desc_errors = desc.CheckErrors(x + 1)

    if desc_errors:
      errors.extend(desc_errors)

  return errors


def _BaseStErrors(edid, version):
  """Check the standard timing section for errors.

  Args:
    edid: The list form of the EDID to be checked.
    version: A string indicating the EDID's version.

  Returns:
    A list of error.Error objects.
  """
  base = 38

  errors = []

  for x in range(0, 8):
    st = standard_timings.GetStandardTiming(edid, base + (x * 2), version)
    if st:
      err = st.CheckErrors(x + 1)
      if err:
        errors.extend(err)

  return errors


def _ExtensionErrors(edid, version):
  """Check all extensions for errors.

  Args:
    edid: The EDID being checked.
    version: A string indicating the EDID's version.

  Returns:
    A list of error.Error objects.
  """
  num_ext = edid[0x7E]

  errors = []

  if (num_ext + 1) != (len(edid) / 128):
    errors.append(error.Error('Extensions', 'Extension count does not match '
                              'EDID length', '%d extensions' % num_ext,
                              '%d extensions' % ((len(edid) / 128) - 1)))

  for x in range(1, num_ext + 1):
    ext = extensions.GetExtension(edid, x, version)

    err = ext.CheckErrors(x)
    if err:
      errors.extend(err)

  return errors


def _WeekError(edid):
  """Check if the manufacturer week is in the proper range of 1-54.

  Args:
    edid: The list form of the EDID being checked.

  Returns:
    An error.Error object, if there's an error.
  """
  if edid[0x10] > 54 and edid[0x10] != 255:
    return [error.Error('Manufacturer/Vendor section- byte 0x10', 'Invalid week'
                        ' value', 'Week in range 1-54', 'Week %d' % edid[0x10])]


def GetErrors(edid, version):
  """Check EDID for all potential errors.

  Args:
    edid: The list form of the EDID being checked.
    version: The string representing the version of the EDID.

  Returns:
    A list of error.Error objects.
  """
  errors = []

  # Check for various errors, and add them to error list

  error_check_functions = [
      _HeaderError(edid),
      _ChecksumError(edid),
      _LengthError(edid),
      _WeekError(edid),
      _DescriptorErrors(edid, version),
      _BaseStErrors(edid, version),
      _ExtensionErrors(edid, version)
  ]

  for err in error_check_functions:
    if err:
      errors.extend(err)

  return errors
