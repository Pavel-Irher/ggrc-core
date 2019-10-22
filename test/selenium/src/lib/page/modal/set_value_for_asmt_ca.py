# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Modals for create objects."""

from lib import base


class SetValueForAsmtDropdown(base.Modal):
  """Modal for set value for assessment custom attribute."""

  def __init__(self, driver=None):
    super(SetValueForAsmtDropdown, self).__init__(driver)
    self.modal_elem = self._browser.div(class_name="no-border").div(
        class_name="simple-modal")
    self.modal_header_lbl = self.modal_elem.div(
        class_name="simple-modal__header-text")

  def click_close_button(self):
    """Click close button."""
    self.modal_elem.button(text="Close").click()

  def click_save_button(self):
    """Click save button."""
    self.modal_elem.button(text="Save").click()

  def set_dropdown_comment(self, comment):
    """Set comment via dropdown."""
    input_field = self.modal_elem.div(text="Comment").parent(
        tag_name="div").div(class_name="ql-editor")
    input_field.click()
    input_field.send_keys(comment)

  def set_dropdown_url(self, url):
    """Set evidence url via dropdown."""
    modal_url_root_element = self.modal_elem.div(text="Evidence url").parent(
        tag_name="div")
    modal_url_root_element.button(text="Add").click()
    modal_url_root_element.input().send_keys(url)
    modal_url_root_element.button(class_name="create-form__confirm").click()

  def fill_dropdown_lca(self, **kwargs):
    """Fill comment or url for Assessment dropdown."""
    if "url" in kwargs:
      self.set_dropdown_url(kwargs["url"])
    if "comment" in kwargs:
      self.set_dropdown_comment(kwargs["comment"])
      self.click_save_button()
    else:
      self.click_close_button()
