# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Elements of search / mapper modal."""
# pylint: disable=too-few-public-methods

from lib import factory
from lib.constants import element, value_aliases
from lib.page.widget import table_with_headers


class SearchFilterArea(object):
  """Represents an upper filter area of search / mapper modal."""

  def __init__(self, container):
    self._root = container
    self._search_btn = self._root.button(text="Search")
    self.type_select_option = self._root.select(name="type-select")
    self.filter_row = self._root.element(
        class_name="filter-container__attribute")
    self.filter_name = self._root.element(
        class_name="autocomplete-dropdown__input-container")
    self.filter_operator = self._root.element(
        class_name="filter-attribute__operator")

  def search_obj(self, obj, filter_value=None,
                 search_attr=element.Common.TITLE,
                 filter_operator=value_aliases.EQUAL_OP):
    """Searches for object by title. Optionally search by any other
    specified attribute."""
    if not filter_value:
      filter_value = obj.title
    self._select_obj_type(obj)
    self._select_search_criteria(search_attr, filter_operator)
    self._set_filter_value(filter_value)
    self._click_search()
    self._wait_for_search_results()

  def _select_obj_type(self, obj):
    """Selects object type."""
    obj_type = obj.type if hasattr(obj, "type") else obj.obj_type()
    self.type_select_option.wait_until(
        lambda e: e.exists).option(value=obj_type).click()

  def _select_search_criteria(self, search_attr, filter_operator):
    """Selects search criteria for object."""
    self.filter_name.click()
    self.filter_name.parent().element(text=search_attr).click()
    self.filter_operator.option(value=filter_operator).click()

  def _set_filter_value(self, value):
    """Types value in to search criteria text box."""
    self.filter_row.text_field(name="right").set(value)

  def _click_search(self):
    """Clicks `Search` button."""
    self._search_btn.click()

  def _wait_for_search_results(self):
    """Waits for search results to be refreshed."""
    self._search_btn.wait_until_not(lambda btn: btn.disabled)


class SearchResultsArea(object):
  """Represents a bottom search results area of search / mapper modal."""

  def __init__(self, container):
    self._root = container
    self._table = table_with_headers.TableWithHeaders(
        container=self._root,
        header_elements=self.search_result_headers,
        table_rows=self.search_result_rows
    )
    self.get_result_by = self._table.get_table_row_by

  def search_result_headers(self):
    """Returns table header elements."""
    return self._root.element(
        tag_name="mapper-results-items-header").divs(class_name="title")

  def search_result_rows(self):
    """Returns search result rows."""
    return [_SearchResultRow(row_el, self._table.table_header_names())
            for row_el in self._root.elements(class_name="object-list__item")]


class _SearchResultRow(object):
  """Represents a search result item in object search / mapper."""

  def __init__(self, container, table_header_names):
    self._root = container
    self._table_row = table_with_headers.TableRow(
        container=container,
        table_header_names=table_header_names,
        cell_locator={"class_name": "attr"}
    )

  def matches_conditions(self, **conditions):
    """Returns whether a row matches conditions."""
    return self._table_row.matches_conditions(self, **conditions)

  def _set_selection_checkbox_state(self, is_selected):
    """Selects or deselects checkbox responsible for search result selection
    according to a passed  value."""
    self._root.element(tag_name="object-selection-item").checkbox().set(
        is_selected)

  def select(self):
    """Selects search result."""
    self._set_selection_checkbox_state(True)

  def deselect(self):
    """Deselects search result."""
    self._set_selection_checkbox_state(False)

  def expand(self):
    """Expands an item if it is not expanded already."""
    if not self.is_expanded:
      self._root.click()

  @property
  def is_expanded(self):
    return self._root.element(tag_name="mapper-results-item-details").exists

  def get_three_bbs(self, obj_type):
    """Expands an item if necessary in order to get 3bbs element.
    Returns 3bbs element."""
    self.expand()
    return factory.get_cls_3bbs_dropdown_info(object_name=obj_type)(self._root)
