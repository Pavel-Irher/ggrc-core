# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Pluralize admin role

Create Date: 2019-05-31 07:48:12.359629
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import datetime

from alembic import op
from sqlalchemy.sql import select

from ggrc.models import all_models
from ggrc.migrations.utils import migrator


# revision identifiers, used by Alembic.
revision = '350d0894b526'
down_revision = '22c80af7da75'

OBJECT_TYPES = (
    "AccountBalance",
    "AccessGroup",
    "Contract",
    "Control",
    "DataAsset",
    "Facility",
    "Issue",
    "KeyReport",
    "Market",
    "Metric",
    "Objective",
    "OrgGroup",
    "Policy",
    "Process",
    "Product",
    "ProductGroup",
    "Project",
    "Regulation",
    "Requirement",
    "Risk",
    "Standard",
    "System",
    "TechnologyEnvironment",
    "Threat",
    "Vendor",
    "Workflow",
)

OLD_ROLE_NAME = "Admin"
NEW_ROLE_NAME = "Admins"


def update_role_names(connection, migrator_id):
  """Updates role names for objects defined in OBJECT_TYPES. """
  roles_table = all_models.AccessControlRole.__table__

  for object_type in OBJECT_TYPES:
    connection.execute(
        roles_table.update().where(
            roles_table.c.object_type == object_type
        ).where(
            roles_table.c.name == OLD_ROLE_NAME
        ).values(name=NEW_ROLE_NAME,
                 updated_at=datetime.datetime.utcnow(),
                 modified_by_id=migrator_id)
    )


def update_propagated_role_ids(connection, migrator_id, roleid):
  """"Determines the propagated role ids."""
  roles_table = all_models.AccessControlRole.__table__
  query = select([roles_table.c.id]).where(roles_table.c.parent_id == roleid)
  roles = connection.execute(query)
  roles = roles.fetchall()

  if not roles:
    return None

  for role in roles:
    role_name = connection.execute(
        select([roles_table.c.name]).where(
            roles_table.c.id == role.id
        )
    )
    role_name = role_name.fetchone()
    role_name = role_name.name
    new_role_name = role_name.replace(OLD_ROLE_NAME, NEW_ROLE_NAME)

    connection.execute(
        roles_table.update().where(
            roles_table.c.id == role.id
        ).values(name=new_role_name,
                 updated_at=datetime.datetime.utcnow(),
                 modified_by_id=migrator_id)
    )
    update_propagated_role_ids(connection, migrator_id, role.id)


def update_propagated_role_names(connection, migrator_id):
  """"Updates propagated role names."""
  roles_table = all_models.AccessControlRole.__table__

  query = select([roles_table.c.id]).where(roles_table.c.name == NEW_ROLE_NAME)
  roles = connection.execute(query)
  role_ids = [role.id for role in roles]

  for role_id in role_ids:
    update_propagated_role_ids(connection, migrator_id, role_id)


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  connection = op.get_bind()
  migrator_id = migrator.get_migration_user_id(connection)
  update_role_names(connection, migrator_id)
  update_propagated_role_names(connection, migrator_id)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  raise NotImplementedError("Downgrade is not supported")
