# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Modal for assigning user roles."""

from lib import base, decorator
from lib.constants import locator
from lib.utils import selenium_utils


class UserRoleAssignmentsModal(base.Modal):
  """Modal for assigning user roles."""
  _locators = locator.ModalAssignUserRole

  def __init__(self, driver):
    super(UserRoleAssignmentsModal, self).__init__(driver)
    self.modal_elem = selenium_utils.get_when_visible(
        self._driver, self._locators.MODAL_CSS)
    self.role_radio_buttons = base.ElementsList(
        self.modal_elem, self._locators.ROLE_RADIO_BUTTONS)
    self.button_save_and_close = base.Button(
        self.modal_elem, self._locators.BUTTON_SAVE_AND_CLOSE)

  def assign_role(self, role):
    """Click on specified role radiobutton on modal"""
    self.role_radio_buttons.get_item(role).click()

  @decorator.handle_alert
  def save_and_close(self):
    """Set person role and close modal"""
    self.button_save_and_close.click()
