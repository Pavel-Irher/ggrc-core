/*
 Copyright (C) 2020 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import canStache from 'can-stache';
import canMap from 'can-map';
import canComponent from 'can-component';
import {REFRESH_RELATED} from '../../events/event-types';
import template from './add-issue-button.stache';
import {
  getPageInstance,
} from '../../plugins/utils/current-page-utils';
import {initCounts} from '../../plugins/utils/widgets-utils';
import Issue from '../../models/business-models/issue';
import pubSub from '../../pub-sub';

export default canComponent.extend({
  tag: 'add-issue-button',
  view: canStache(template),
  leakScope: true,
  viewModel: canMap.extend({
    define: {
      prepareJSON: {
        get: function () {
          let instance = this.attr('relatedInstance');
          let json = {
            assessment: {
              title: instance.title,
              id: instance.id,
              type: instance.type,
              title_singular: instance.constructor.title_singular,
              table_singular: instance.constructor.table_singular,
            },
          };

          return JSON.stringify(json);
        },
      },
      buttonText: {
        value: 'Raise Issue',
      },
      extraCssClass: {
        value: 'btn-red',
      },
    },
    relatedInstance: {},
    pubSub,
  }),
  events: {
    refreshIssueList: function (window, event, instance) {
      let model = 'Issue';

      if (instance instanceof Issue) {
        let pageInstance = getPageInstance();
        initCounts(
          [model],
          pageInstance.type,
          pageInstance.id
        );
      }

      this.viewModel.attr('relatedInstance').dispatch({
        ...REFRESH_RELATED,
        model,
      });
    },
    '[data-toggle="modal-ajax-form"] modal:added': 'refreshIssueList',
    '[data-toggle="modal-ajax-form"] modal:success': 'refreshIssueList',
    '{pubSub} objectDeleted'(pubSub, event) {
      let instance = event.instance;
      if (instance instanceof Issue) {
        this.refreshIssueList(window, event, instance);
      }
    },
  },
});
