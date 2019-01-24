# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Services for create and manipulate objects via admin UI."""

from lib import url
from lib.page import dashboard
from lib.page.modal.create_new_person import CreateNewPersonModal
from lib.page.modal.user_role_assignments_modal import UserRoleAssignmentsModal
from lib.utils import selenium_utils


class AdminWebUiService(object):
  """Base class for business layer's services objects for Admin."""

  # pylint: disable=too-few-public-methods
  def __init__(self, driver):
    self._driver = driver


class PeopleAdminWebUiService(AdminWebUiService):
  """Class for admin people business layer's services objects"""

  def __init__(self, driver):
    super(PeopleAdminWebUiService, self).__init__(driver)
    self.people_widget = self._open_admin_people_tab()

  def create_new_person(self, person):
    """Create new person on Admin People widget
      - Return: lib.entities.entity.PersonEntity"""
    self.people_widget.click_create_button()
    self._create_new_person_on_modal(person)
    # refresh page to make newly created person appear on Admin People Widget
    self._driver.refresh()
    return self.find_filtered_person(person)

  def _open_admin_people_tab(self):
    """Open People widget on Admin dashboard.
      - Return: lib.page.widget.admin_widget.People"""
    selenium_utils.open_url(url.Urls().admin_people_tab)
    return dashboard.AdminDashboard(self._driver).select_people()

  def _create_new_person_on_modal(self, person):
    """Fill required fields and click on save and close button
      on New Person modal"""
    create_person_modal = CreateNewPersonModal(self._driver)
    create_person_modal.enter_name(person.name)
    create_person_modal.enter_email(person.email)
    create_person_modal.name_tf.click()
    create_person_modal.save_and_close()

  def find_filtered_person(self, person):
    """Find person by email in the list on Admin People widget
      - Return: list of PersonEntities"""
    self.people_widget.filter_by_name_email_company(person.email)
    selenium_utils.wait_for_js_to_load(self._driver)
    return self.people_widget.get_people()[0]

  def get_person_role(self, person):
    """Return role of a person"""
    return self.find_filtered_person(person).system_wide_role

  def assign_person_role(self, person, role):
    """Assign specified role to a person"""
    assign_role_modal = self.open_user_role_assignments_modal(person)
    assign_role_modal.assign_role(role)
    assign_role_modal.save_and_close()

  def open_user_role_assignments_modal(self, person):
    """Open User Role Assignments modal for specified person
      - Return: lib.page.modal.UserRoleAssignmentsModal"""
    self.find_filtered_person(person)
    self.people_widget.expand_person_info()
    self.people_widget.open_details_dropdown()
    self.people_widget.click_edit_authorisations_link()
    return UserRoleAssignmentsModal(self._driver)

  @property
  def ppl_count(self):
    """Get ppl count from tab."""
    return self.people_widget.tab_people.count
