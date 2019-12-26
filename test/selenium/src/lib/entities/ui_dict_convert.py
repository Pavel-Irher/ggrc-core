# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Conversions from UI dicts to App entities."""
from lib.app_entity_factory import (
    person_entity_factory, workflow_entity_factory, entity_factory_common,
    threat_entity_factory)
from lib.utils import date_utils


def ui_to_app(obj_name, ui_dict):
  """Converts ui_dict to app_entity."""
  method_name = {
      "workflow": workflow_ui_to_app,
      "cycle_task": cycle_task_ui_to_app,
      "threat": threat_ui_to_app
  }[obj_name]
  return method_name(ui_dict)


def workflow_ui_to_app(ui_dict):
  """Converts Workflow ui_dict to app_entity."""
  return workflow_entity_factory.WorkflowFactory().create_empty(
      obj_id=int(ui_dict["obj_id"]),
      title=ui_dict["title"],
      state=ui_dict["state"],
      is_archived=ui_dict["is_archived"],
      admins=emails_to_app_people(ui_dict["admins"]),
      wf_members=emails_to_app_people(ui_dict["workflow_members"]),
      created_at=date_utils.ui_str_with_zone_to_datetime(
          ui_dict["created_at"]),
      updated_at=date_utils.ui_str_with_zone_to_datetime(
          ui_dict["updated_at"]),
      modified_by=email_to_app_person(ui_dict["modified_by"]),
      task_groups=[],
      code=ui_dict["code"],
      repeat_every=convert_workflow_repeat_frequency(
          ui_dict["repeat_workflow"]),
      repeat_unit=convert_workflow_repeat_unit(ui_dict["repeat_workflow"])
  )


def task_group_ui_to_app(ui_dict):
  """Converts TaskGroup ui dict to App entity."""
  return workflow_entity_factory.TaskGroupFactory().create_empty(
      title=ui_dict["title"],
      assignee=email_to_app_person(ui_dict["assignee"])
  )


def task_group_task_ui_to_app(ui_dict):
  """Converts TaskGroupTask ui dict to App entity."""
  return workflow_entity_factory.TaskGroupTaskFactory().create_empty(
      obj_id=ui_dict.get("obj_id"),
      title=ui_dict["task title"],
      assignees=emails_to_app_people(ui_dict.get("assignees")),
      start_date=str_to_date(ui_dict["start_date"]),
      due_date=str_to_date(ui_dict["due_date"])
  )


def cycle_task_ui_to_app(ui_dict):
  """Converts CycleTask ui dict to App entity."""
  return workflow_entity_factory.CycleTaskFactory().create_empty(
      title=ui_dict["title"],
      state=ui_dict["state"],
      assignees=emails_to_app_people(ui_dict.get("assignees")),
      due_date=str_to_date(ui_dict["due_date"]),
      comments=comment_dicts_to_entities(ui_dict["comments"])
  )


def threat_ui_to_app(ui_dict):
  """Converts Threat ui dict to App entity."""
  return threat_entity_factory.ThreatFactory().create_empty(
      admins=emails_to_app_people(ui_dict["admins"]),
      code=ui_dict["code"],
      comments=ui_dict["comments"],
      created_at=date_utils.ui_str_with_zone_to_datetime(
          ui_dict["created_at"]),
      modified_by=email_to_app_person(ui_dict["last_updated_by"]),
      obj_id=int(ui_dict["id"]),
      title=ui_dict["title"],
      state=ui_dict["state"],
      updated_at=date_utils.ui_str_with_zone_to_datetime(
          ui_dict["updated_at"])
  )


def emails_to_app_people(emails):
  """Converts emails to app people."""
  return [email_to_app_person(email) for email in emails]


def email_to_app_person(email):
  """Converts email to app person."""
  return person_entity_factory.PersonFactory().create_empty(
      email=email)


def str_to_date(date_str):
  """Converts date string to the date object."""
  return date_utils.str_to_date(date_str, "%m/%d/%Y")


def comment_dicts_to_entities(comment_dicts):
  """Converts the list of comment dicts to the list of comment entities."""
  return [comment_dict_to_entity(comment_dict)
          for comment_dict in comment_dicts]


def comment_dict_to_entity(comment_dict):
  """Converts comment dict to Comment app entity."""
  return entity_factory_common.CommentFactory().create_empty(
      created_at=date_utils.ui_str_with_zone_to_datetime(
          comment_dict["created_at"]),
      description=comment_dict["description"],
      modified_by=email_to_app_person(comment_dict["modified_by"])
  )


def convert_workflow_repeat_unit(repeat_workflow):
  """Convert workflow repeat unit."""
  repeat_unit_dict = {"weekday": "day", "weekdays": "day", "week": "week",
                      "weeks": "week", "month": "month", "months": "month"}
  repeat_unit = None
  if repeat_workflow != "Repeat Off":
    # Repeat unit is the last word in the phrase
    repeat_unit = (
        repeat_unit_dict[repeat_workflow.replace(
            "Repeat every ", "").split()[-1]])
  return repeat_unit


def convert_workflow_repeat_frequency(repeat_workflow):
  """Convert workflow repeat frequency."""
  # pylint: disable=invalid-name
  repeat_frequency = None
  if repeat_workflow != "Repeat Off":
    # If repeat workflow phrase has 4 words than frequency is the 3rd word
    # If repeat workflow phrase has 3 words than frequency equals 1
    # For example: "Repeat every weekday(week/month)"
    # or "Repeat every 2 weekdays(weeks/months)"
    repeat_frequency = 1
    if len(repeat_workflow.split()) == 4:
      repeat_frequency = repeat_workflow.split()[3]
  return repeat_frequency
