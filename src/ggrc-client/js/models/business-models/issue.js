/*
    Copyright (C) 2020 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Cacheable from '../cacheable';
import CaUpdate from '../mixins/ca-update';
import AccessControlList from '../mixins/access-control-list';
import BaseNotifications from '../mixins/notifications/base-notifications';
import IssueTracker from '../mixins/issue-tracker';
import Stub from '../stub';

export default Cacheable.extend({
  root_object: 'issue',
  root_collection: 'issues',
  category: 'governance',
  findOne: 'GET /api/issues/{id}',
  findAll: 'GET /api/issues',
  update: 'PUT /api/issues/{id}',
  destroy: 'DELETE /api/issues/{id}',
  create: 'POST /api/issues',
  mixins: [
    CaUpdate,
    AccessControlList,
    BaseNotifications,
    IssueTracker,
  ],
  is_custom_attributable: true,
  isRoleable: true,
  attributes: {
    context: Stub,
  },
  tree_view_options: {
    add_item_view: 'issues/tree-add-item',
    attr_list: Cacheable.attr_list.concat([
      {attr_title: 'Reference URL', attr_name: 'reference_url'},
      {attr_title: 'Effective Date', attr_name: 'start_date'},
      {attr_title: 'Last Deprecated Date', attr_name: 'end_date'},
      {attr_title: 'Due Date', attr_name: 'due_date'},
      {
        attr_title: 'State',
        attr_name: 'status',
        order: 40,
      }, {
        attr_title: 'Ticket Tracker',
        attr_name: 'issue_url',
        deny: !GGRC.ISSUE_TRACKER_ENABLED,
      },
      {
        attr_title: 'Description',
        attr_name: 'description',
      }, {
        attr_title: 'Notes',
        attr_name: 'notes',
      }, {
        attr_title: 'Remediation Plan',
        attr_name: 'test_plan',
      }]),
    display_attr_names: ['title', 'Admin', 'status', 'updated_at'],
  },
  sub_tree_view_options: {
    default_filter: ['Control', 'Control_version'],
  },
  defaults: {
    status: 'Draft',
  },
  statuses: ['Draft', 'Deprecated', 'Active', 'Fixed', 'Fixed and Verified'],
  unchangeableIssueTrackerIdStatuses:
    ['Fixed', 'Fixed and Verified', 'Deprecated'],
  buildIssueTrackerConfig(instance) {
    return {
      hotlist_id: '1498476',
      component_id: '398781',
      issue_severity: 'S2',
      issue_priority: 'P2',
      issue_type: 'PROCESS',
      title: instance.title || '',
      enabled: instance.isNew(),
    };
  },
}, {
  define: {
    title: {
      value: '',
      validate: {
        required: true,
      },
    },
    due_date: {
      value: '',
      validate: {
        required: true,
      },
    },
    issue_tracker: {
      value: {},
      validate: {
        validateIssueTrackerEnabled() {
          return 'Issue';
        },
        validateIssueTrackerComponentId: true,
        validateIssueTrackerTitle: true,
        validateIssueTrackerIssueId() {
          return this.constructor.unchangeableIssueTrackerIdStatuses;
        },
      },
    },
  },
});
