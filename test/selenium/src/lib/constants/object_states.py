# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""States for objects."""

# General
DRAFT = "Draft"
DEPRECATED = "Deprecated"

# For objects
ACTIVE = "Active"
IN_PROGRESS = "In Progress"
COMPLETED = "Completed"

# For Assessment
NOT_STARTED = "Not Started"
READY_FOR_REVIEW = "In Review"
VERIFIED = "Verified"
REWORK_NEEDED = "Rework Needed"
VERIFIER_REQUIRING_STATES = (REWORK_NEEDED, READY_FOR_REVIEW, VERIFIED)

# For Audit
PLANNED = "Planned"
MANAGER_REVIEW = "Manager Review"
READY_FOR_EXT_REVIEW = "Ready for External Review"

# For Issue
FIXED = "Fixed"
FIXED_AND_VERIFIED = "Fixed and Verified"

# For Proposal
PROPOSED = "PROPOSED"
APPLIED = "APPLIED"
DECLINED = "DECLINED"

# For Workflow
INACTIVE = "Inactive"

# For Workflow cycles
ASSIGNED = "Assigned"
FINISHED = "Finished"

# Assessment states for Bulk updates functionality
ASSESSMENT_STATES = (COMPLETED, VERIFIED, IN_PROGRESS, NOT_STARTED,
                     REWORK_NEEDED, DEPRECATED, READY_FOR_REVIEW)
OPENED_STATES = (NOT_STARTED, IN_PROGRESS, REWORK_NEEDED)
COMPLETED_STATES = (DEPRECATED, READY_FOR_REVIEW, COMPLETED, VERIFIED)
ASSESSMENT_STATUSES_NOT_READY_FOR_REVIEW = (
    COMPLETED, VERIFIED, IN_PROGRESS, NOT_STARTED, REWORK_NEEDED, DEPRECATED)
