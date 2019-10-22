# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Models for bulk update modals."""
import re

from lib import base
from lib.constants import objects
from lib.element import page_elements
from lib.page.modal import set_value_for_asmt_ca, search_modal_elements


class BaseBulkUpdateModal(base.Modal):
  """Common class for Bulk Complete and Bulk Verify modals."""
  # pylint: disable=too-few-public-methods

  def __init__(self):
    super(BaseBulkUpdateModal, self).__init__()
    self._root = self._browser.div(class_name="modal")
    self.filter_section = FilterSection(self._root)

  @property
  def is_displayed(self):
    """Returns whether modal is opened or not."""
    return self._root.exists


class BulkCompleteModal(BaseBulkUpdateModal):
  """Modal for choosing and downloading templates."""

  def __init__(self):
    super(BulkCompleteModal, self).__init__()
    self._root = self._browser.element(tag_name="assessments-bulk-complete")
    self.select_assessments_section = SelectAssessmentsToCompleteSection(
        self._root)
    self.custom_attributes_section = AsmtsCustomAttrsSection(self._root)

  @property
  def complete_button(self):
    """Returns 'Complete' button element."""
    return self._root.button(text="Complete")

  @property
  def cancel_button(self):
    """Returns 'Cancel' button element."""
    return self._root.button(text="Cancel")

  def click_complete_button(self):
    """Clicks on 'Complete' button."""
    self.complete_button.click()

  @property
  def is_complete_btn_active(self):
    """Returns whether 'Complete' button is active."""
    return self.complete_button.enabled


class FilterSection(object):
  """Represents collapsible filter section."""
  # pylint: disable=too-few-public-methods

  def __init__(self, parent_element):
    self._root = parent_element.element(
        tag_name="collapsible-panel", text=re.compile("FILTER"))

  @property
  def is_expanded(self):
    """Returns whether section is expanded or not."""
    return "is-expanded" in self._root.div(class_name="body-inner").classes


class SelectAssessmentsToCompleteSection(object):
  """Represents 'Select assessments' section for BulkCompleteModal."""

  def __init__(self, parent_element):
    self._root = parent_element.element(
        tag_name="collapsible-panel", text=re.compile("SELECT ASSESSMENTS"))

  @property
  def results_area(self):
    """Represents search result with filtered assessments. """
    return search_modal_elements.SearchResultsArea(self._root)

  def deselect_asmt_by_tittle(self, title):
    """Deselects assessment for bulk complete procedure by its title."""
    self.results_area.get_result_by(title=title).deselect()

  def click_select_all(self):
    """Clicks 'Select All' link to select all assessments."""
    self._root.button(text="All").click()

  def click_select_button(self):
    """Clicks on 'Select' button."""
    self._root.button(text="Select").click()


class AsmtsCustomAttrsSection(object):
  """Represents section for providing additional information about custom
    attributes for Bulk Complete."""
  # pylint: disable=too-few-public-methods

  def __init__(self, parent_element):
    super(AsmtsCustomAttrsSection, self).__init__()
    self._root = parent_element.element(
        tag_name="collapsible-panel", text=re.compile("PROVIDE INFORMATION"))

  def fill_lcas(self, custom_attributes, dropdown_cas_name=None, **kwargs):
    """Fills local custom attributes fields. Also fills comment or url for
    dropdown lca if needed."""
    ca_manager = page_elements.CustomAttributeManager(
        self._root, obj_type=objects.ASSESSMENTS, is_global=False,
        is_inline=True)
    for attr_title, attr_value in custom_attributes.iteritems():
      elem_class = ca_manager.find_ca_elem_by_title(attr_title)
      elem_class.set_value(attr_value)
      if attr_title == dropdown_cas_name:
        set_value_for_asmt_ca.SetValueForAsmtDropdown().fill_dropdown_lca(
            **kwargs)
