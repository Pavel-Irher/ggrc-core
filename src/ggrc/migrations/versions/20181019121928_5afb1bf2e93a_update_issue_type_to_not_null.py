# Copyright (C) 2020 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Update issue_type to not NULL

Create Date: 2018-10-19 12:19:28.009600
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '5afb1bf2e93a'
down_revision = 'd9c56989ac07'


def update_nullable_valuses():
  """update nullable values with PROCESS"""
  sql = """
    UPDATE issuetracker_issues
    SET issue_type='PROCESS'
    WHERE issue_type is NULL;
  """
  op.execute(sql)


def make_issue_type_non_null():
  """Alter table to make issue_type NOT NULL"""
  sql = """
  ALTER TABLE issuetracker_issues
    MODIFY
    issue_type VARCHAR(50) NOT NULL DEFAULT 'PROCESS'
  """
  op.execute(sql)


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  update_nullable_valuses()
  make_issue_type_non_null()


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
