# coding: utf-8

# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for /query api endpoint."""

import ddt

from freezegun import freeze_time
from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc.query_helper import WithQueryApi

CHANGETRACKED_MODELS = (
    'AccessGroup',
    'Assessment',
    'AssessmentTemplate',
    'Audit',
    'Contract',
    'Control',
    'DataAsset',
    'Document',
    'Evidence',
    'Facility',
    'Issue',
    'Market',
    'Objective',
    'OrgGroup',
    'Policy',
    'Process',
    'Product',
    'Program',
    'Project',
    'Regulation',
    'Risk',
    'Requirement',
    'Standard',
    'System',
    'TaskGroup',
    'TaskGroupTask',
    'Threat',
    'Vendor',
    'Workflow',
)


@ddt.ddt
class TestUpdatedAt(WithQueryApi, TestCase):
  """Tests for filtering by updated_at field"""

  def setUp(self):
    super(TestUpdatedAt, self).setUp()
    self.client.get("/login")

  @freeze_time("2018-05-20 12:23:17")
  @ddt.data(*CHANGETRACKED_MODELS)
  def test_updated_at_in_operator(self, model_name):
    """Test updated_at field filters correctly with ~ and !~ operators"""
    expected_in_id = set()
    expected_not_in_id = set()
    with freeze_time("2018-05-20 12:23:17"):
      expected_in = factories.get_model_factory(model_name)()
      expected_in_id.add(expected_in.id)
    with freeze_time("2018-06-25 12:00:00"):
      expected_not_in = factories.get_model_factory(model_name)()
      expected_not_in_id.add(expected_not_in.id)
    response_in = self.simple_query(
        model_name,
        expression=[
            "Task Last Updated Date" if model_name == "TaskGroupTask"
            else "Last Updated Date",
            "~",
            "05/20/2018"
        ],
        type_="ids",
        field="ids"
    )
    response_not_in = self.simple_query(
        model_name,
        expression=[
            "Task Last Updated Date" if model_name == "TaskGroupTask"
            else "Last Updated Date",
            "!~",
            "2018-05-20"
        ],
        type_="ids",
        field="ids"
    )
    self.assertItemsEqual(expected_in_id, response_in)
    self.assertItemsEqual(expected_not_in_id, response_not_in)
