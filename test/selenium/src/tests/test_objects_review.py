# -*- coding: utf-8 -*-
# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Control object review workflow tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=redefined-outer-name
import re

import pytest

from lib import base, constants, users
from lib.constants import roles
from lib.entities.entities_factory import PeopleFactory
from lib.service import webui_service, rest_service, rest_facade
from lib.utils import string_utils


class TestControlsWorkflow(base.Test):
  """Test class for control scenario tests"""
  info_service = rest_service.ObjectsInfoService
  usr_email = PeopleFactory.superuser.name
  rand_msg = string_utils.StringMethods.random_string()

  def _assert_control(self, actual_control, new_control_rest):
    """Assert control object on equals."""
    self.general_equal_assert(new_control_rest.repr_ui(), actual_control,
                              "created_at", "updated_at",
                              "custom_attribute_definitions",
                              "custom_attributes",
                              "object_review_txt")

  def test_control_approve_review_flow(self, new_control_rest, selenium):
    """Test accept review scenario"""
    control_ui_service = webui_service.ControlsService(selenium)
    control_ui_service.open_info_page_of_obj(new_control_rest)
    control_ui_service.submit_obj_for_review(
        new_control_rest, self.usr_email, self.rand_msg)
    control_ui_service.approve_review(new_control_rest)
    actual_control = control_ui_service.get_obj_from_info_page(
        new_control_rest)
    new_control_rest.update_attrs(os_state="Reviewed")
    full_regex = (
        unicode("Last reviewed by\n{}\non ".format(self.usr_email)) +
        constants.element.Common.APPROVED_DATE_REGEX)
    self._assert_control(actual_control, new_control_rest)
    assert re.compile(full_regex).match(actual_control.object_review_txt)

  @pytest.fixture
  def users_setup(self):
    """Set users for test_add_control_reviewer"""
    creator = rest_facade.create_user_with_role(roles.CREATOR)
    reviewer = rest_facade.create_user_with_role(roles.CREATOR)
    users.set_current_user(creator)
    return reviewer

  @pytest.mark.smoke_tests
  def test_add_control_reviewer(self, users_setup, selenium, new_control_rest):
    """Confirm reviewer is is displayed on Control Info panel"""
    reviewer = users_setup
    control_service = webui_service.ControlsService(selenium)
    widget = control_service.open_info_page_of_obj(new_control_rest)
    control_service.submit_obj_for_review(
        new_control_rest, reviewer.email, self.rand_msg)
    assert control_service.is_reviewer_displayed(widget, reviewer.email)
