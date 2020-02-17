# Copyright (C) 2020 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Rows of tree widgets on workflow tabs."""
from lib.app_entity_factory import workflow_entity_factory
from lib.page.widget import tree_widget, table_with_headers
from lib.utils import date_utils, test_utils, ui_utils


class WorkflowCycleRow(tree_widget.TreeItem):
  """Represents workflow cycle row on workflow Active Cycles / History tab."""

  def __init__(self, row_el, table_header_names):
    super(WorkflowCycleRow, self).__init__(row_el, table_header_names)
    self._table_header_names = table_header_names

  @property
  def state(self):
    """Returns workflow cycle state."""
    return self.text_for_header("State")

  def expand(self):
    """Expands workflow cycle row to show cycle task group rows."""
    if not self.is_expanded:
      self.select()
      ui_utils.wait_for_spinner_to_disappear()

  @property
  def due_date(self):
    """Returns workflow cycle due date."""
    return date_utils.str_to_date(self.text_for_header("End Date"), "%m/%d/%Y")

  def cycle_task_group_rows(self):
    """Returns cycle task group rows."""
    all_sub_row_els = self._root.next_sibling(
        tag_name="lazy-render").elements(class_name="sub-item-content")
    task_group_row_els = [
        row_el for row_el in all_sub_row_els
        if not row_el.element(class_name="tree-item__overdue").exists]
    return [_CycleTaskGroupRow(row_el, self._table_header_names,
                               parent_row=self)
            for row_el in task_group_row_els]

  def get_cycle_task_group_row_by(self, **conditions):
    """Returns a cycle task group row by conditions."""
    return table_with_headers.get_sub_row_by(
        rows=self.cycle_task_group_rows, **conditions)

  def build_obj_with_tree(self):
    """Builds an object from a WorkflowCycle entity object.
    Will also build objects from subtrees if they are expanded.
    """
    dict_keys = ["title", "state", "due_date"]
    obj_dict = self.obj_dict_from_keys(dict_keys)
    cycle_task_groups = [cycle_task_group_row.build_obj_with_tasks()
                         for cycle_task_group_row
                         in self.cycle_task_group_rows()]
    return workflow_entity_factory.WorkflowCycleFactory().create_empty(
        title=obj_dict["title"],
        state=obj_dict["state"],
        due_date=obj_dict["due_date"],
        cycle_task_groups=cycle_task_groups
    )


class _BaseCycleSubRow(tree_widget.TreeItem):
  """Base row for cycle task group and cycle task classes."""

  def __init__(self, row_el, table_header_names, parent_row):
    super(_BaseCycleSubRow, self).__init__(row_el, table_header_names)
    self._parent_row = parent_row

  @property
  def title(self):
    """Returns task group title."""
    return self._root.element(class_name="title").text

  @property
  def state(self):
    """Returns task group state."""
    return self._root.element(tag_name="tree-item-status-for-workflow").text


class _CycleTaskGroupRow(_BaseCycleSubRow):
  """Represents cycle task group row on workflow Active Cycles / History tab.
  """

  def expand(self):
    """Expands cycle task group row to show cycle task rows."""
    if not self.is_expanded:
      self._root.element(class_name="columns").click()
      ui_utils.wait_for_spinner_to_disappear()

  def cycle_task_rows(self):
    """Returns cycle task rows."""
    task_group_row_els = self._root.next_sibling(
        class_name="sub-tier").elements(class_name="tree-item-element")
    return [_CycleTaskRow(
        row_el.wait_until(lambda e: e.present), self._table_header_names,
        parent_row=self)
        for row_el in task_group_row_els]

  def get_cycle_task_row_by(self, **conditions):
    """Returns a cycle task group row by conditions."""
    return table_with_headers.get_sub_row_by(
        rows=self.cycle_task_rows, **conditions)

  def build_obj_with_tasks(self):
    """Builds an object from a CycleTaskGroup entity object.
    Will also build child task objects if trees are expanded.
    """
    cycle_tasks = [cycle_task_row.build_obj()
                   for cycle_task_row in self.cycle_task_rows()]
    return workflow_entity_factory.CycleTaskGroupFactory().create_empty(
        title=self.title,
        state=self.state,
        cycle_tasks=cycle_tasks
    )


class _CycleTaskRow(_BaseCycleSubRow):
  """Represents cycle task row on workflow Active Cycles / History tab."""

  @property
  def due_date(self):
    """Returns task group due date."""
    return self._root.element(class_name="tree-item__overdue").text

  def build_obj(self):
    """Builds an object from a CycleTask entity object."""
    return workflow_entity_factory.CycleTaskFactory().create_empty(
        title=self.title,
        state=self.state,
        due_date=date_utils.str_to_date(self.due_date, "%m/%d/%Y"),
    )

  def select(self):
    """Clicks cycle task to open cycle task info panel."""
    self._root.element(class_name="columns").click()

  def start(self):
    """Starts this cycle task."""
    def workflow_state():
      """Returns workflow cycle state."""
      # pylint: disable=protected-access
      return self._parent_row._parent_row.state
    initial_workflow_state = workflow_state()
    self._root.hover()
    self._root.button(text="Start").click()
    test_utils.wait_for(lambda: workflow_state() != initial_workflow_state)


class SetupTaskGroupTreeItem(tree_widget.TreeItem):
  """Represents a row of task group."""

  def __init__(self, row_el, table_header_names):
    super(SetupTaskGroupTreeItem, self).__init__(
        row_el=row_el,
        table_header_names=table_header_names
    )

  def obj_dict(self):
    """Returns an obj dict."""
    dict_keys = ["title", "assignee", "details"]
    return self._table_row.obj_dict(self, dict_keys=dict_keys)

  @property
  def title(self):
    """Returns a title."""
    return self.text_for_header("Summary")
