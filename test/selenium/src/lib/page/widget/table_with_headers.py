# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Generic classes to represent table with headers."""
import inflection


def get_sub_row_by(rows, **conditions):
  """Returns a table row that matches conditions."""
  for table_row in rows():
    if table_row.matches_conditions(**conditions):
      return table_row
  return None


class TableWithHeaders(object):
  """Represents generic table with headers."""

  def __init__(self, container, header_elements, table_rows):
    self._root = container
    self._header_elements = header_elements
    self._table_rows = table_rows

  def table_header_names(self):
    """Returns names of table headers."""
    # JS `text_content` is used as displayed text is capitalized using CSS
    return [el.text_content for el in self._header_elements()]

  def get_table_row_by(self, **conditions):
    """Returns a table row that matches conditions."""
    return get_sub_row_by(rows=self._table_rows, **conditions)


class TableRow(object):
  """Represents generic row of the table."""

  def __init__(self, container, table_header_names, cell_locator):
    self._root = container
    self._headers = table_header_names
    self._cell_locator = cell_locator

  def obj_dict(self, row_obj, dict_keys):
    """Returns a dict where:
    * keys are `dict_keys`
    * if properties exist values are return values of `row_obj`'s properties,
    otherwise they are cell values retrieved by header names
    (headers are title-ized `dict_keys`)
    """
    result = {}
    for dict_key in dict_keys:
      if hasattr(row_obj, dict_key):
        value = getattr(row_obj, dict_key)  # should be a property
      else:
        header_name = inflection.titleize(dict_key)
        value = self.text_for_header(header_name)
      result[dict_key] = value
    return result

  def matches_conditions(self, row_obj, **expected_dict):
    """Returns whether tree item matches conditions.
    Conditions are evaluated similarly to how `obj_dict` is built.
    """
    for attr_name, expected_value in expected_dict.iteritems():
      if hasattr(row_obj, attr_name):
        actual_value = getattr(row_obj, attr_name)  # should be a property
      else:
        header_name = inflection.titleize(attr_name)
        actual_value = self.text_for_header(header_name)
      if actual_value != expected_value:
        return False
    return True

  def text_for_header(self, header_name):
    """Returns value of cell with header `header_name`."""
    idx = self._headers.index(header_name)
    return self.cells()[idx].text

  def cell_for_header(self, header_name):
    """Returns cell for header `header_name`."""
    idx = self._headers.index(header_name)
    return self.cells()[idx]

  def cells(self):
    """Returns the list with contents of all attr cells."""
    return self._root.elements(**self._cell_locator)
