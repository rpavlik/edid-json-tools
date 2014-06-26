# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Provides the Error class with methods for describing and reporting errors."""


class Error(object):
  """Defines an Error object, with location, message, etc."""

  def __init__(self, location, msg, expected=None, found=None):
    """Creates an Error object.

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
    """Fetches the location of the error.

    Returns:
      A string describing the location of the error.
    """
    return self._location

  @property
  def message(self):
    """Fetches the message of the error.

    Returns:
      A string describing the message of the error.
    """
    return self._message

  @property
  def expected(self):
    """Fetches the expected value.

    Returns:
      A string describing the expected value.
    """
    return self._expected

  @property
  def found(self):
    """Fetches the value found instead of what was expected.

    Returns:
      A string describing the value found in the EDID.
    """
    return self._found


