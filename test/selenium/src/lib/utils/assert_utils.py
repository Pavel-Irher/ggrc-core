# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Assert utils."""
from lib.constants import messages
from lib.entities import entity
from lib.utils import help_utils


class SoftAssert(object):
  """Class for performing soft asserts."""

  def __init__(self):
    self.__errors = []

  def expect(self, expr, msg):
    """Tries to perform assert and if fails stores msg into errors list."""
    try:
      assert expr, msg
    except AssertionError:
      self.__errors.append(msg)

  def expect_equal(self, expected_objs, actual_objs, *exclude_attrs):
    """Tries to perform equal assert for deepcopy converted to list
    expected and actual objects according to '*exclude_attrs' tuple of
    excluding attributes' names (compare objects' collections w/
    attributes' values set to None). """
    expected_objs_wo_excluded_attrs, actual_objs_wo_excluded_attrs = (
        entity.Representation.extract_objs(
            help_utils.convert_to_list(expected_objs),
            help_utils.convert_to_list(actual_objs), *exclude_attrs))
    try:
      assert expected_objs_wo_excluded_attrs == actual_objs_wo_excluded_attrs
    except AssertionError:
      self.__errors.append(messages.AssertionMessages.format_err_msg_equal(
          expected_objs_wo_excluded_attrs, actual_objs_wo_excluded_attrs))

  def assert_expectations(self):
    """Performs assert that there were no soft_assert errors."""
    assert not self.__errors, ("There were some errors during soft_assert:\n"
                               "{}".format(self.__errors))
