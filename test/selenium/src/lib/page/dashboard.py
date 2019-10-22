# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""List dashboard."""
# pylint: disable=too-many-instance-attributes

from selenium.common import exceptions

from lib import base, decorator, environment, url
from lib.constants import locator
from lib.element import tab_element, page_elements
from lib.page import widget_bar, lhn
from lib.page.modal import global_search
from lib.page.widget import object_modal, page_mixins
from lib.utils import selenium_utils


class UserList(base.Component):
  """User list dashboard."""
  locators = locator.PageHeader

  def __init__(self, driver):
    super(UserList, self).__init__(driver)
    self.button_logout = base.Button(
        self._driver, self.locators.BUTTON_LOGOUT)
    self.notifications = base.Label(
        self._driver, self.locators.NOTIFICATIONS)
    self.checkbox_daily_digest = base.Checkbox(
        self._driver, self.locators.CHECKBOX_DAILY_DIGEST)
    self.button_admin_dashboard = base.Button(
        self._driver, self.locators.BUTTON_ADMIN_DASHBOARD)
    self.button_help = base.Button(
        self._driver, self.locators.BUTTON_HELP)
    self.button_data_export = base.Button(
        self._driver, self.locators.BUTTON_DATA_EXPORT)
    self.email = base.Label(
        self._driver, self.locators.EMAIL)
    self.user_menu_items = (self.button_logout, self.button_data_export,
                            self.button_admin_dashboard, self.button_help,
                            self.notifications)

  @decorator.wait_for_redirect
  def select_logout(self):
    raise NotImplementedError

  def check_daily_email_digest(self):
    """Checks daily checkbox."""
    self.checkbox_daily_digest.check()

  def uncheck_daily_email_digest(self):
    """Unchecks daily checkbox."""
    self.checkbox_daily_digest.uncheck()

  def select_admin_dashboard(self):
    """
    Return: widget.AdminDashboard
    """
    self.button_admin_dashboard.click()
    return AdminDashboard(self._driver)


class GenericHeader(base.Component):
  """Header of page dashboard without navigation to admin panel."""
  # pylint: disable=too-many-instance-attributes
  locators = locator.PageHeader

  def __init__(self, driver):
    super(GenericHeader, self).__init__(driver)
    self.toggle_lhn_menu = None
    self.button_dashboard = None
    self.button_search = None
    self.button_my_tasks = None
    self.button_all_objects = None
    self.toggle_user_dropdown = None
    self.button_data_import = None
    self.button_data_export = None
    self._refresh_elements()

  def _refresh_elements(self):
    """Refresh dashboard elements."""
    self.button_dashboard = base.Button(
        self._driver, self.locators.BUTTON_DASHBOARD)
    self.button_search = base.Button(
        self._driver, self.locators.BUTTON_SEARCH)
    self.button_my_tasks = base.Button(
        self._driver, self.locators.BUTTON_MY_TASKS)
    self.button_all_objects = base.Button(
        self._driver, self.locators.BUTTON_ALL_OBJECTS)
    self.toggle_user_dropdown = base.Toggle(
        self._driver, self.locators.TOGGLE_USER_DROPDOWN)
    self.toggle_lhn_menu = base.Toggle(
        self._driver, self.locators.TOGGLE_LHN)
    self.button_data_import = base.Button(
        self._driver, self.locators.BUTTON_DATA_IMPORT)

  def open_lhn_menu(self):
    """Opens LHN on Dashboard.
    For some reason, after creating 2 objects via LHN (and clicking 2x on
    LHN button), third time toggle_lhn_menu signals it's not part of
    the DOM anymore. For this reason we're refreshing elements.
    Return: LHN Menu
    """
    try:
      self.toggle_lhn_menu.toggle()
      return lhn.Menu(self._driver)
    except exceptions.StaleElementReferenceException:
      self._refresh_elements()
      return self.open_lhn_menu()

  def close_lhn_menu(self):
    """Closes LHN on Dashboard.
    """
    try:
      self.toggle_lhn_menu.toggle(on_el=False)
      selenium_utils.get_when_invisible(self._driver, locator.LhnMenu.HOLDER)
    except exceptions.StaleElementReferenceException:
      self._refresh_elements()
      self.close_lhn_menu()

  def open_user_list(self):
    """
    Return: UserList
    """
    self.toggle_user_dropdown.click()
    return UserList(self._driver)

  def select_my_work(self):
    """
    Return: widget.Dashboard
    """
    self.button_dashboard.click()
    return Dashboard(self._driver)

  def select_all_objects(self):
    """Clicks "All Objects" button."""
    self._browser.element(id="allObjectView").click()
    return AllObjectsDashboard(self._driver)

  def open_global_search(self):
    """Clicks 'Global Search' button."""
    self.button_search.click()
    return global_search.GlobalSearch()


class Header(GenericHeader):
  """Header of page dashboard with navigation to admin panel."""

  def __init__(self, driver):
    super(Header, self).__init__(driver)
    self._refresh_elements()


class Dashboard(widget_bar.Dashboard):
  """Main dashboard page."""
  # pylint: disable=abstract-method

  @property
  def header(self):
    """Returns header of dashboard page."""
    return Header(self._driver)

  @property
  def dashboard_url(self):
    """Returns dashboard page url."""
    return url.dashboard()

  def open_objs_tab_via_url(self, obj_type):
    """Opens objects dashboard tab via url according to specified object
    type."""
    selenium_utils.open_url(self.dashboard_url + "#!" + obj_type.lower())

  def start_workflow(self):
    """Clicks "Start new Workflow" button."""
    self._browser.element(class_name="get-started__list__item",
                          text="Start new Workflow").click()

  def start_task_group(self):
    """Clicks "Create" button."""
    self._browser.div(class_name="tree-action").link(text="Create").click()

  def click_create_obj_btn(self):
    """Clicks "Create object" button."""
    self._browser.element(class_name=(["get-started__list__item",
                                       "get-started__list__item--top-space",
                                       "hidden-widgets-list"]),
                          visible_text='Create object').click()

  def open_create_obj_modal(self, obj_type):
    """Click "Create object" button, select type and click."""
    self.click_create_obj_btn()
    CreateObjectDropdown().click_item_by_text(text=obj_type)
    return object_modal.get_modal_obj(obj_type=obj_type)

  @property
  def is_add_tab_present(self):
    """Checks presence of Add Tab"""
    return selenium_utils.is_element_exist(self._driver,
                                           locator.WidgetBar.BUTTON_ADD)

  def wait_to_be_init(self):
    """Waits for page object to be initialized."""
    # Element with class `nav-tabs` appears in DOM at start of panel rendering.
    # But a class "tab-container_hidden-tabs" that makes it "display: none"
    #   is removed only at end.
    self._browser.element(class_name="internav").\
        wait_until(lambda e: e.present)


class CreateObjectDropdown(base.Widget):
  """Create object dropdown."""

  def click_item_by_text(self, text):
    """Click item from list by text."""
    self._browser.element(class_name="inner-nav-item", text=text).click()

  def get_all_hidden_items(self):
    """Returns a list of hidden items from dropdown."""
    return self._browser.elements(css=" .external-link__content").to_list


class AdminDashboard(widget_bar.AdminDashboard, GenericHeader):
  """Admin Dashboard page model."""
  # pylint: disable=abstract-method

  def __init__(self, driver=None):
    super(AdminDashboard, self).__init__(driver)
    self.tabs = tab_element.Tabs(self._browser, tab_element.Tabs.TOP)


class AllObjectsDashboard(widget_bar.AllObjectsDashboard, GenericHeader):
  """All Objects Dashboard"""
  # pylint: disable=abstract-method


class MyAssessments(page_mixins.WithBulkUpdateButtons):
  """Model for 'My Assessments' page."""

  def __init__(self, driver=None):
    super(MyAssessments, self).__init__(driver)

  @property
  def my_assessments_url(self):
    """Returns 'My Assessments' page url."""
    return environment.app_url + url.Widget.MY_ASSESSMENTS

  @property
  def status_filter_dropdown(self):
    """Returns multi select dropdown for filtering Assessments by their
    status."""
    return page_elements.MultiselectDropdown(
        self._browser.element(tag_name="tree-status-filter"))
