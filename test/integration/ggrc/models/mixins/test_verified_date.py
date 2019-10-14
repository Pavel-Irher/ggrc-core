# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration tests for VerifiedDate mixin"""

from ggrc.models.assessment import Assessment
from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc import api_helper


# pylint: disable=super-on-old-class; TestCase is a new-style class
class TestVerifiedDate(TestCase):
  """Integration tests suite for TestVerifiedDate mixin"""

  # pylint: disable=invalid-name

  def setUp(self):
    super(TestVerifiedDate, self).setUp()
    self.api_helper = api_helper.Api()

  def test_validates_with_no_mandatory_ca(self):
    """Test verified date and verified flag are reset on Undo."""
    with factories.single_commit():
      person = factories.PersonFactory()
      assessment = factories.AssessmentFactory(
          status=Assessment.PROGRESS_STATE,
      )
      assessment.add_person_with_role_name(person, "Verifiers")

    response = self.api_helper.modify_object(assessment, {
        "status": "Verified",
    })
    self.assertEqual(response.json["assessment"]["verified"], True)
    response = self.api_helper.modify_object(assessment, {
        "status": "In Review",
    })
    self.assertEqual(response.json["assessment"]["verified"], False)
