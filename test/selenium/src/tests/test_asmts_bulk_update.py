# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for bulk update functionality."""
# pylint: disable=no-self-use
# pylint: disable=unused-argument
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
import pytest

from lib import base, users
from lib.constants import object_states, roles, element
from lib.rest_facades import roles_rest_facade
from lib.service import rest_facade, webui_facade, webui_service, rest_service


def audit_page(audit):
  """Opens generic widget class of mapped objects according to source obj."""
  return webui_service.AssessmentsService().open_widget_of_mapped_objs(audit)


def my_assessments_page(*args):
  """Opens 'My Assessment' page."""
  return webui_service.AssessmentsService().open_my_assessments_page()


class TestBulkComplete(base.Test):
  """Tests for Bulk Complete functionality."""

  @pytest.fixture()
  def deprecated_asmts(self, audit):
    """Returns 5 assessments in 'Deprecated' status."""
    return [rest_facade.create_asmt(audit, status=object_states.DEPRECATED)
            for _ in xrange(5)]

  @pytest.fixture()
  def three_assessments_w_lcas(self, audit):
    """Creates and returns 3 Assessments from template with all local CAs."""
    controls = [rest_facade.create_control() for _ in xrange(3)]
    for control in controls:
      rest_facade.map_objs(audit, control)
    cads_list = [
        {"cad_type": cad_type}
        for cad_type in element.AdminWidgetCustomAttributes.ALL_CA_TYPES]
    for cad_dict in cads_list:
      if cad_dict["cad_type"] == element.AdminWidgetCustomAttributes.DROPDOWN:
        cad_dict.update({"dropdown_types_list": ["url_comment", "url_comment"],
                         "mandatory": True})
    asmt_template = rest_facade.create_asmt_template(
        audit, assessment_type="Control", cads_list=cads_list)
    assessments_w_lcas = rest_facade.create_asmts_from_template(
        audit, asmt_template, controls)
    for index, asmt in enumerate(assessments_w_lcas):
      asmt.update_attrs(mapped_objects=[controls[index].title])
    return assessments_w_lcas

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("page", [audit_page, my_assessments_page])
  def test_bulk_complete_state_for_author(
      self, login_as_creator, audit, deprecated_asmts, soft_assert, page,
      selenium
  ):
    """Confirms that 'Bulk complete' option/button is displayed correctly
    for author of objects."""
    page = page(audit)
    webui_facade.soft_assert_bulk_complete_for_completed_asmts(
        soft_assert, deprecated_asmts, page)
    webui_facade.soft_assert_bulk_complete_for_opened_asmts(
        soft_assert, deprecated_asmts, page)
    soft_assert.assert_expectations()

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("page", [audit_page, my_assessments_page])
  @pytest.mark.parametrize(
      "audit_role, asmt_role, bulk_complete_btn_visibility",
      [(roles_rest_facade.custom_audit_read_role,
        roles_rest_facade.custom_asmt_read_role, False),
       (roles.AUDITORS, roles.VERIFIERS, True)],
      ids=["reader", "editor"])
  def test_bulk_complete_state_for_reader_and_editor(
      self, audit_role, asmt_role, creator, second_creator,
      login_as_creator, audit, deprecated_asmts, bulk_complete_btn_visibility,
      soft_assert, page, selenium
  ):
    """Confirms that 'Bulk complete' option/button is displayed correctly
    for user with Read/Edit rights."""
    rest_facade.update_acl(
        [audit], second_creator,
        **roles_rest_facade.get_role_name_and_id(audit.type, audit_role))
    rest_facade.update_acl(
        deprecated_asmts, second_creator,
        **roles_rest_facade.get_role_name_and_id(deprecated_asmts[0].type,
                                                 asmt_role))
    users.set_current_user(second_creator)
    page = page(audit)
    users.set_current_user(creator)
    webui_facade.soft_assert_bulk_complete_for_completed_asmts(
        soft_assert, deprecated_asmts, page)
    webui_facade.soft_assert_bulk_complete_for_opened_asmts(
        soft_assert, deprecated_asmts, page,
        is_displayed=bulk_complete_btn_visibility)
    soft_assert.assert_expectations()

  @pytest.mark.xfail(reason="Bulk Complete flow currently disabled and will "
                            "be reworked.")
  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("page", [audit_page, my_assessments_page])
  def test_creator_can_perform_bulk_complete(
      self, login_as_creator, three_assessments_w_lcas, audit,
      soft_assert, page, selenium
  ):
    """Confirms that Assessments creator can perform bulk complete."""
    webui_facade.check_user_can_perform_bulk_complete(
        soft_assert, page(audit), three_assessments_w_lcas)

  @pytest.mark.xfail(reason="Bulk Complete flow currently disabled and will "
                            "be reworked.")
  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("page", [audit_page, my_assessments_page])
  def test_editor_can_perform_bulk_complete(
      self, second_creator, login_as_creator, three_assessments_w_lcas, audit,
      soft_assert, page, selenium
  ):
    """Confirms that user with Edit rights for Assessments can perform bulk
    complete."""
    for asmt in three_assessments_w_lcas:
      rest_asmt_obj = rest_service.ObjectsInfoService().get_obj(asmt)
      asmt.update_attrs(access_control_list=rest_asmt_obj.access_control_list,
                        assignees=asmt.assignees + [second_creator.email])
    rest_facade.update_acl(
        three_assessments_w_lcas, second_creator,
        **roles_rest_facade.get_role_name_and_id(
            three_assessments_w_lcas[0].type, roles.ASSIGNEES))
    users.set_current_user(second_creator)
    webui_facade.check_user_can_perform_bulk_complete(
        soft_assert, page(audit), three_assessments_w_lcas)
