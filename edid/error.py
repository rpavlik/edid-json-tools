# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# SPDX-License-Identifier: BSD-3-Clause


"""Provides the Error class with methods for describing and reporting errors."""


class Error(object):
  """Defines an Error object, with location, message, etc."""

  def __init__(self, location, msg, expected=None, found=None):
    """Create an Error object.

    Args:
      location: A string describing the location of the Error.
      msg: A string describing why this is an Error.
      expected: A string describing the expected value.
      found: A string describing the value found instead.
    """
    self._location = location
    self._message = msg
    self._expected = expected
    self._found = found

  @property
  def location(self):
    """Fetch the location of the error.

    Returns:
      A string describing the location of the error.
    """
    return self._location

  @property
  def message(self):
    """Fetch the message of the error.

    Returns:
      A string describing the message of the error.
    """
    return self._message

  @property
  def expected(self):
    """Fetch the expected value.

    Returns:
      A string describing the expected value.
    """
    return self._expected

  @property
  def found(self):
    """Fetch the value found instead of what was expected.

    Returns:
      A string describing the value found in the EDID.
    """
    return self._found
