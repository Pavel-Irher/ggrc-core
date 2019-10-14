# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration tests for Assessment cad and status change."""

from collections import OrderedDict

from ggrc.models import all_models

from integration import ggrc
from integration.ggrc.models import factories


class TestAssessmentComplete(ggrc.TestCase):
  """Test Assessment complete status with cad."""
  def setUp(self):
    """Set up audit and cad for test cases."""
    super(TestAssessmentComplete, self).setUp()
    self.api = ggrc.api_helper.Api()
    with factories.single_commit():
      self.audit = factories.AuditFactory()
      self.asmt = factories.AssessmentFactory(audit=self.audit,
                                              status="In Progress")
      self.cad = factories.CustomAttributeDefinitionFactory(
          title="test cad",
          definition_type="assessment",
          definition_id=self.asmt.id,
          attribute_type="Text",
          mandatory=True,
      )

  def _validate_response(self, response, status_code, status, cad):
    """Validate response status_code, assessment status and cad."""
    self.assertEqual(response.status_code, status_code)
    response_asmt = response.json["assessment"]
    response_cads = response_asmt["custom_attribute_values"]
    resonse_cad_value = response_cads[0]["attribute_value"]
    self.assertEqual(response_asmt["status"], status)
    self.assertEqual(resonse_cad_value, cad)

  def test_put_cad_and_status(self):
    """Test update mandatory cad and status in single PUT."""
    with factories.single_commit():
      asmt = factories.AssessmentFactory()
      asmt_id = asmt.id
      self.update_assessment_verifiers(asmt, "In Review")
    assessment_data = {
        "status": "In Review",
        "custom_attribute_values": [{
            "custom_attribute_id": self.cad.id,
            "attribute_value": "test",
        }],
    }
    response = self.api.put(asmt, assessment_data)
    self._validate_response(response, 200, "In Review", "test")

    asmt = all_models.Assessment.query.get(asmt_id)
    self.assertEqual(asmt.status, "In Review")
    self.assertEqual(asmt.custom_attribute_values[0].attribute_value, "test")

  def test_put_cad_and_status_empty(self):
    """Test update empty mandatory cad and status in single PUT."""
    with factories.single_commit():
      person = factories.PersonFactory()
      self.asmt.add_person_with_role_name(person, "Verifiers")
    asmt_id = self.asmt.id
    assessment_data = {
        "status": "In Review",
        "custom_attribute_values": [{
            "custom_attribute_id": self.cad.id,
            "attribute_value": None,
        }],
    }
    response = self.api.put(self.asmt, assessment_data)
    self.assertEqual(response.status_code, 400)
    self.assertIn("CA-introduced completion preconditions are not satisfied.",
                  response.json["message"])

    asmt = all_models.Assessment.query.get(asmt_id)
    self.assertEqual(asmt.status, "In Progress")
    self.assertEqual(len(asmt.custom_attribute_values), 0)

  def test_cad_service_import(self):
    """Test double insert by /_service/import_csv"""
    cav = factories.CustomAttributeValueFactory(
        custom_attribute=self.cad,
        attributable=self.asmt,
        attribute_value="Text",
    )
    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code", self.asmt.slug),
        (self.cad.title, cav.attribute_value)
    ]))
    self.assertItemsEqual(response[0]['row_errors'], [])
