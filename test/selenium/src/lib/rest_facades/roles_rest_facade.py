# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""REST facade for roles."""
from lib import users
from lib.constants import roles, objects, object_states
from lib.decorator import memoize
from lib.entities import entities_factory
from lib.entities.entity import AccessControlRoleEntity
from lib.service import rest_facade


def get_role_name_and_id(object_type, role):
  """Returns role name and id as dict according to passed role entity or
  name and object type."""
  if isinstance(role, AccessControlRoleEntity):
    return {"role_name": role.name, "role_id": role.id}
  return {"role_name": role, "role_id": roles.ACLRolesIDs.id_of_role(
      object_type, role)}


def custom_read_role(object_type):
  """Creates and returns custom access control role for object with 'Read'
  rights."""
  current_user = users.current_user()
  users.set_current_user(entities_factory.PeopleFactory.superuser)
  role = rest_facade.create_access_control_role(
      object_type=object_type, read=True, update=False, delete=False)
  users.set_current_user(current_user)
  return role


@memoize
def custom_audit_read_role():
  """Returns custom access control role with 'Read' rights for Audit."""
  return custom_read_role(objects.get_singular(objects.AUDITS, title=True))


@memoize
def custom_asmt_read_role():
  """Returns custom access control role with 'Read' rights for Assessment."""
  return custom_read_role(objects.get_singular(objects.ASSESSMENTS,
                                               title=True))


def add_verifier_to_set_obj_state(obj, state, person):
  """Assign a person as verifier if verifier presence is necessary for
  setting an object into specific state and obj has no verifiers assigned."""
  if state in object_states.VERIFIER_REQUIRING_STATES and not obj.verifiers:
    rest_facade.update_acl(
        objs=[obj], people=person,
        **get_role_name_and_id(obj.type, roles.VERIFIERS))
