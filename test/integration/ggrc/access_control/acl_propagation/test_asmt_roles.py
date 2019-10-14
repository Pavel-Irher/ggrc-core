# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test ACR propagation for assessment Assignees, Creators and Verifiers."""

import ddt

from ggrc.models import all_models
from integration.ggrc.access_control import rbac_factories
from integration.ggrc.access_control.acl_propagation import base
from integration.ggrc.utils import helpers


@ddt.ddt
class TestAsmtRolesPropagation(base.TestACLPropagation):
  """Test Assignees, Creators, Verifiers roles permission propagation."""

  PERMISSIONS = {
      "Creator": {
          "Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "create": False,
                  "read": True,
                  "update": True,
                  "delete": False,
                  "map_snapshot": False,
                  "read_revisions": True,
                  "deprecate": True,
                  "complete": True,
                  "in_progress": True,
                  "not_started": True,
                  "decline": (False, "unimplemented"),
                  "verify": (False, "unimplemented"),
                  "map_comment": True,
                  "map_evidence": True,
                  "related_assessments": True,
                  "related_objects": True,
              },
          },
          "Snapshot Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_original": False,
                  "update": False,
                  "get_latest_version": False,
              },
          },
          "Snapshot Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": False,
                  "read_original": False,
                  "update": False,
                  "get_latest_version": False,
              },
          },
          "Issue Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_revisions": True,
                  "map": False,
                  "create_and_map": True,
                  "raise_issue": True,
              },
              ("Assignees",): {
                  "update": True,
                  "delete": True,
                  "unmap": True,
              },
              ("Creators", "Verifiers"): {
                  "update": False,
                  "delete": False,
                  "unmap": False,
              },
          },
          "Issue Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": False,
                  "update": False,
                  "delete": False,
                  "read_revisions": False,
                  "map": False,
                  "create_and_map": False,
                  "unmap": False,
              },
          },
          "Evidence Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "create_and_map": False,
                  "read": True,
                  "update": False,
                  "delete": False,
                  "read_comments": True,
                  "add_comment": False,
              },
          },
          "Evidence Assessment": {
              ("Assignees", "Creators", "Verifiers", "Primary Contacts",
               "Secondary Contacts"): {
                  "create_and_map": True,
                  "read": True,
                  "update": True,
                  "delete": True,
                  "read_comments": True,
                  "add_comment": True,
              },
          },
      },
      "Reader": {
          "Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "update": True,
                  "delete": False,
                  "map_snapshot": False,
                  "read_revisions": True,
                  "deprecate": True,
                  "complete": True,
                  "in_progress": True,
                  "not_started": True,
                  "verify": (False, "unimplemented"),
                  "map_comment": True,
                  "map_evidence": True,
                  "related_assessments": True,
                  "related_objects": True,
              },
          },
          "Snapshot Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_original": True,
                  "update": False,
                  "get_latest_version": True,
              },
          },
          "Snapshot Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_original": True,
                  "update": False,
                  "get_latest_version": True,
              },
          },
          "Issue Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_revisions": True,
                  "map": False,
                  "create_and_map": True,
                  "raise_issue": True,
              },
              ("Assignees",): {
                  "update": True,
                  "delete": True,
                  "unmap": True,
              },
              ("Creators", "Verifiers"): {
                  "update": False,
                  "delete": False,
                  "unmap": False,
              },
          },
          "Issue Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "update": False,
                  "delete": False,
                  "read_revisions": True,
                  "map": False,
                  "create_and_map": False,
                  "unmap": False,
              },
          },
          "Evidence Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "create_and_map": False,
                  "read": True,
                  "update": False,
                  "delete": False,
                  "add_comment": False,
                  "read_comments": True
              },
          },
          "Evidence Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "create_and_map": True,
                  "read": True,
                  "update": True,
                  "delete": True,
                  "add_comment": True,
                  "read_comments": True,
              },
          },
      },
      "Editor": {
          "Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "update": True,
                  "delete": True,
                  "map_snapshot": True,
                  "read_revisions": True,
                  "deprecate": True,
                  "complete": True,
                  "in_progress": True,
                  "not_started": True,
                  "decline": (False, "unimplemented"),
                  "verify": (False, "unimplemented"),
                  "map_comment": True,
                  "map_evidence": True,
                  "related_assessments": True,
                  "related_objects": True,
              },
          },
          "Snapshot Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_original": True,
                  "update": True,
                  "get_latest_version": True,
              },
          },
          "Snapshot Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "read_original": True,
                  "update": True,
                  "get_latest_version": True,
              },
          },
          "Issue Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "update": True,
                  "delete": True,
                  "read_revisions": True,
                  "map": True,
                  "create_and_map": True,
                  "raise_issue": True,
                  "unmap": True,
              },
          },
          "Issue Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "read": True,
                  "update": True,
                  "delete": True,
                  "read_revisions": True,
                  "map": True,
                  "create_and_map": True,
                  "unmap": True,
              },
          },
          "Evidence Audit": {
              ("Assignees", "Creators", "Verifiers"): {
                  "create_and_map": True,
                  "read": True,
                  "update": True,
                  "delete": True,
                  "read_comments": True,
                  "add_comment": True,
              },
          },
          "Evidence Assessment": {
              ("Assignees", "Creators", "Verifiers"): {
                  "create_and_map": True,
                  "read": True,
                  "update": True,
                  "delete": True,
                  "read_comments": True,
                  "add_comment": True,
              },
          },
      },
  }

  def init_factory(self, role, model, parent, **kwargs):
    """Initialize RBAC factory with propagated Assignees role.

    Args:
        role: Global Custom role that user have (Creator/Reader/Editor).
        model: Model name for which factory should be got.
        parent: Model name in scope of which objects should be installed.

    Returns:
        Initialized RBACFactory object.
    """
    if "acr_name" not in kwargs:
      raise ValueError("runtest should be called with 'acr_name' kwarg")

    self.setup_people()
    acr = all_models.AccessControlRole.query.filter_by(
        name=kwargs["acr_name"],
        object_type="Assessment",
    ).first()

    rbac_factory = rbac_factories.TEST_FACTORIES_MAPPING[model]
    return rbac_factory(self.people[role].id, acr, parent)

  @helpers.unwrap(PERMISSIONS, unwrap_keys=True)
  # pylint: disable=too-many-arguments
  def test_access(self, role, model, acr_name, action_name, expected_result):
    """{0:<7}: On {1:<20} as {2:<9} test {3:<20} - Expected {4:<2} """
    self.runtest(role, model, action_name, expected_result, acr_name=acr_name)

  @helpers.unwrap({
      "Creator": {
          "complete": {
            "Assignees": True,
            "Creators": True,
            "Verifiers": (False, "unimplemented"),
          },
      },
      "Reader": {
          "complete": {
              "Assignees": True,
              "Creators": True,
              "Verifiers": (False, "unimplemented"),
          },
          "decline": {
              "Assignees": (False, "unimplemented"),
              "Creators": (False, "unimplemented"),
              "Verifiers": True,
          },
      },
      "Editor": {
          "complete": {
              "Assignees": True,
              "Creators": True,
              "Verifiers": (False, "unimplemented"),
          },
      },
  }, unwrap_keys=True)
  def test_access_verified_related(self, role, action_name,
                                   acr_name, expected_result):
    """{0:<7}: On Assessment as {2:<9} test {1:<20} - Expected {4:<2} """
    model_name = "Assessment"
    rbac_factory = self.init_factory(role, model_name, None, acr_name=acr_name)
    action = getattr(rbac_factory, action_name, None)
    response = action()
    self.assert_result(response, expected_result, action_name, model_name)
