# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Mixins for info page objects"""
# pylint: disable=too-few-public-methods

from lib import base
from lib.element import page_elements
from lib.page.modal import bulk_update
from lib.utils import selenium_utils


class WithPageElements(base.WithBrowser):
  """A mixin for page elements"""

  def _related_people_list(self, label, root_elem=None):
    """Return RelatedPeopleList page element with label `label`"""
    return page_elements.RelatedPeopleList(
        root_elem if root_elem else self._browser, label)

  def _related_urls(self, label, root_elem=None):
    """Return RelatedUrls page element with label `label`"""
    return page_elements.RelatedUrls(
        root_elem if root_elem else self._browser, label)

  def _assessment_evidence_urls(self):
    """Return AssessmentEvidenceUrls page element"""
    return page_elements.AssessmentEvidenceUrls(self._browser)

  def _comment_area(self):
    """Return CommentArea page element"""
    return page_elements.CommentArea(self._browser)

  def _simple_field(self, label, root_elem=None):
    """Returns SimpleField page element."""
    return page_elements.SimpleField(
        root_elem if root_elem else self._browser, label)

  def _info_pane_form_field(self, label):
    """Returns InfoPaneFormField page element."""
    return page_elements.InfoPaneFormField(self._browser, label)

  def _assessment_form_field(self, label):
    """Returns AssessmentFormField page element."""
    return page_elements.AssessmentFormField(self._browser, label)

  def _assertions_dropdown(self):
    """Returns AssertionsDropdown page element."""
    return page_elements.AssertionsDropdown(self._browser)


class WithAssignFolder(base.WithBrowser):
  """A mixin for `Assign Folder`"""

  def __init__(self, driver):
    super(WithAssignFolder, self).__init__(driver)
    self.assign_folder_button = self._browser.element(
        class_name="mapped-folder__add-button")


class WithObjectReview(base.WithBrowser):
  """A mixin for object reviews"""

  def __init__(self, driver=None):
    super(WithObjectReview, self).__init__(driver)

  @property
  def _review_root(self):
    return self._browser.element(class_name="object-review")

  @property
  def request_review_btn(self):
    return self._review_root.button(text="Request Review")

  @property
  def mark_reviewed_btn(self):
    return self._review_root.element(text="Mark Reviewed")

  @property
  def floating_message(self):
    return self._browser.element(text="Review is complete.")

  @property
  def undo_button(self):
    return self._browser.element(class_name="object-review__revert")

  @property
  def review_status(self):
    return self._review_root.element(class_name="state-value")

  @property
  def object_review_txt(self):
    """Return page element with review message."""
    return self._review_root.element(
        class_name="object-review__body-description")

  @property
  def reviewers(self):
    """Return page element with reviewers emails."""
    return self._related_people_list("Reviewers", self._review_root)

  def open_submit_for_review_popup(self):
    """Open submit for control popup by clicking on corresponding button."""
    self.request_review_btn.click()
    selenium_utils.wait_for_js_to_load(self._driver)

  def click_approve_review(self):
    """Click approve review button."""
    self.mark_reviewed_btn.click()

  def click_undo_button(self):
    """Click 'Undo' button on floating message."""
    self.undo_button.click()

  def get_object_review_txt(self):
    """Return review message on info pane."""
    return (self.object_review_txt.text if self.object_review_txt.exists
            else None)

  def get_reviewers_emails(self):
    """Return reviewers emails if reviewers assigned."""
    return (self.reviewers.get_people_emails()
            if self.reviewers.exists() else None)

  def get_review_dict(self):
    """Return Review as dict."""
    return {"status": self.get_review_state_txt(),
            "reviewers": self.get_reviewers_emails(),
            # Last 7 symbols are the UTC offset. Can not convert to UI
            # format date due to %z directive doesn't work in Python 2.7.
            "last_reviewed_by": self.get_object_review_txt()[:-7] if
            self.get_object_review_txt() else None}

  def has_review(self):
    """Check if review section exists."""
    return self._review_root.exists

  def get_review_status(self):
    """Get review status."""
    return self.review_status.text.title()


class WithDisabledProposals(base.WithBrowser):
  """A mixin for disabled objects pages with proposals elements."""

  @property
  def proposals_tab_or_link_name(self):
    """Returns a name of proposals tab/link for active/disabled objects."""
    return "Change Proposals"

  def click_change_proposals(self):
    """Click 'Change Proposals' link or tab."""
    self._browser.link(text=self.proposals_tab_or_link_name).click()

  @property
  def propose_changes_btn(self):
    """Returns 'Propose Changes' button element."""
    return self._browser.link(text="Propose Changes")

  @property
  def is_propose_changes_btn_exists(self):
    """Returns whether 'Propose Changes' button exists."""
    return self.propose_changes_btn.exists


class WithProposals(WithDisabledProposals):
  """A mixin for proposals elements."""

  def click_propose_changes(self):
    """Click on Propose Changes button."""
    self.propose_changes_btn.click()


class WithDisabledVersionHistory(base.WithBrowser):
  """A mixin for disabled objects pages with version history elements."""
  # pylint: disable=invalid-name

  @property
  def version_history_tab_or_link_name(self):
    """Returns a name of version history tab/link for active/disabled
    objects."""
    return "Version History"

  def click_version_history(self):
    """Click 'Version History' link or tab."""
    self._browser.element(text=self.version_history_tab_or_link_name).click()


class WithBulkUpdate(base.WithBrowser):
  """Contains bulk update elements."""

  @property
  def bulk_update_finalized_msg(self):
    """Returns floating message that appears after bulk update process is
    completed successfully."""
    return self._browser.element(text="Bulk update is finished successfully.")

  @property
  def bulk_update_submitted_msg(self):
    """Returns floating message that appears after bulk update process is
    started."""
    return self._browser.element(
        text="Your bulk update is submitted. Once it is done you will get a "
        "notification. You can continue working with the app.")


class WithBulkUpdateButtons(WithBulkUpdate):
  """Contains bulk update elements presented as buttons on page."""

  @property
  def bulk_complete_button(self):
    """Represents 'Bulk complete' button."""
    return self._browser.button(text="Bulk Complete")

  def is_bulk_complete_displayed(self):
    """Returns whether 'Bulk complete' button is displayed."""
    return self.bulk_complete_button.exists

  def open_bulk_complete_modal(self):
    """Clicks bulk complete button.
    Returns: Bulk Complete modal."""
    self.bulk_complete_button.click()
    return bulk_update.BulkCompleteModal()


class WithBulkUpdateOptions(WithBulkUpdate):
  """Contains bulk update elements presented as 3bbs menu options."""

  @property
  def bulk_complete_option(self):
    """Returns 'Bulk complete' option from 3bbs menu."""
    return self.three_bbs.option_by_text("Bulk Complete")

  def is_bulk_complete_displayed(self):
    """Returns whether 'Bulk complete' option is displayed in 3bbs menu."""
    return self.bulk_complete_option.exists

  def open_bulk_complete_modal(self):
    """Clicks on 'Bulk Complete' option in 3bbs dropdown.
    Returns: Bulk Complete modal."""
    self.bulk_complete_option.click()
    return bulk_update.BulkCompleteModal()
