# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


"""Tests for assessment service handle."""
import random

import ddt

from ggrc.models import all_models
from integration.ggrc import TestCase
from integration.ggrc.query_helper import WithQueryApi
from integration.ggrc.models import factories
from integration.ggrc.api_helper import Api
from integration.ggrc.generator import ObjectGenerator


@ddt.ddt
class TestCollection(TestCase, WithQueryApi):

  """Test for collection assessment objects."""

  def setUp(self):
    super(TestCollection, self).setUp()
    self.client.get("/login")
    self.clear_data()
    self.api = Api()
    self.generator = ObjectGenerator()

  @ddt.data(True, False)
  def test_order_by_test(self, desc):
    """Order by fultext attr"""
    expected_ids = []
    with factories.single_commit():
      assessments = [factories.AssessmentFactory() for _ in range(10)]
    random.shuffle(assessments)
    with factories.single_commit():
      for idx, assessment in enumerate(assessments):
        comment = factories.CommentFactory(description=str(idx))
        factories.RelationshipFactory(source=assessment, destination=comment)
        expected_ids.append(assessment.id)
    query = self._make_query_dict(
        "Assessment", order_by=[{"name": "comment", "desc": desc}]
    )
    if desc:
      expected_ids = expected_ids[::-1]
    results = self._get_first_result_set(query, "Assessment", "values")
    self.assertEqual(expected_ids, [i['id'] for i in results])

  @ddt.data("Assignees", "Creators", "Verifiers")
  def test_delete_assessment_by_role(self, role_name):
    """Delete assessment not allowed for based on Assignee Type."""
    with factories.single_commit():
      assessment = factories.AssessmentFactory()
      context = factories.ContextFactory(related_object=assessment)
      assessment.context = context
      person = factories.PersonFactory()
      factories.AccessControlPersonFactory(
          ac_list=assessment.acr_name_acl_map[role_name],
          person=person,
      )
    assessment_id = assessment.id
    role = all_models.Role.query.filter(
        all_models.Role.name == "Creator"
    ).first()
    self.generator.generate_user_role(person, role, context)
    self.api.set_user(person)
    assessment = all_models.Assessment.query.get(assessment_id)
    resp = self.api.delete(assessment)
    self.assert403(resp)
    self.assertTrue(all_models.Assessment.query.filter(
        all_models.Assessment.id == assessment_id).one())


@ddt.ddt
class TestAssessmentChangeState(TestCase, WithQueryApi):
  """Test change assessment state"""
  # pylint: disable=invalid-name

  def setUp(self):
    super(TestAssessmentChangeState, self).setUp()
    self.client.get("/login")
    self.clear_data()
    self.api = Api()
    self.generator = ObjectGenerator()

  @ddt.data(
      all_models.Assessment.REWORK_NEEDED,
      all_models.Assessment.FINAL_STATE,
  )
  def test_update_status_need_rework(self, status):
    """Test update assessment state from need rework to valid"""
    with factories.single_commit():
      assessment = factories.AssessmentFactory(
          status=all_models.Assessment.REWORK_NEEDED,
      )
    assessment_id = assessment.id
    resp = self.api.put(assessment, {"status": status})
    self.assert200(resp)
    self.assertEqual(
        status, all_models.Assessment.query.get(assessment_id).status)

  def test_update_status_need_rework_with_verifiers(self):
    """Test update assessment state where verifiers required"""
    expected_status = all_models.Assessment.DONE_STATE
    with factories.single_commit():
      assessment = factories.AssessmentFactory(
          status=all_models.Assessment.REWORK_NEEDED,
      )
      assessment.add_person_with_role_name(
          factories.PersonFactory(), "Verifiers"
      )
    assessment_id = assessment.id
    resp = self.api.put(assessment, {"status": expected_status})
    self.assert200(resp)
    self.assertEqual(
        expected_status, all_models.Assessment.query.get(assessment_id).status)

  def test_no_update_status_need_rework(self):
    """Test can't update assessment state to start state"""
    with factories.single_commit():
      assessment = factories.AssessmentFactory(
          status=all_models.Assessment.REWORK_NEEDED,
      )
    assessment_id = assessment.id
    resp = self.api.put(
        assessment,
        {"status": all_models.Assessment.START_STATE}
    )
    self.assert400(resp)
    expected_status = all_models.Assessment.REWORK_NEEDED
    self.assertEqual(
        expected_status, all_models.Assessment.query.get(assessment_id).status)
