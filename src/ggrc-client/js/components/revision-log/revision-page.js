/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {exists, splitTrim} from '../../plugins/ggrc-utils';
import loCompact from 'lodash/compact';
import loMapValues from 'lodash/mapValues';
import loGroupBy from 'lodash/groupBy';
import loReverse from 'lodash/reverse';
import loFlow from 'lodash/flow';
import loXor from 'lodash/xor';
import loKeyBy from 'lodash/keyBy';
import loMerge from 'lodash/merge';
import loUniq from 'lodash/uniq';
import loCapitalize from 'lodash/capitalize';
import loIsObject from 'lodash/isObject';
import loForEach from 'lodash/forEach';
import loFind from 'lodash/find';
import loFindIndex from 'lodash/findIndex';
import loSortBy from 'lodash/sortBy';
import loIsEqual from 'lodash/isEqual';
import loMap from 'lodash/map';
import loFilter from 'lodash/filter';
import makeArray from 'can-util/js/make-array/make-array';
import canStache from 'can-stache';
import canMap from 'can-map';
import canComponent from 'can-component';
import './revision-log-data';
import {getRolesForType} from '../../plugins/utils/acl-utils';
import template from './revision-page.stache';
import Person from '../../models/business-models/person';
import Stub from '../../models/stub';
import {formatDate} from '../../plugins/utils/date-utils';
import {reify} from '../../plugins/utils/reify-utils';

const EMPTY_DIFF_VALUE = '—';

let DATE_FIELDS = {
  created_at: 1,
  updated_at: 1,
  start_date: 1,
  end_date: 1,
  requested_on: 1,
  finished_date: 1,
  verified_date: 1,
};

let LIST_FIELDS = {
  recipients: 1,
};

export default canComponent.extend({
  tag: 'revision-page',
  view: canStache(template),
  leakScope: true,
  viewModel: canMap.extend({
    define: {
      revisions: {
        set(newValue, setter) {
          setter(newValue);

          if (newValue) {
            this.computeChanges();
          }
        },
      },
    },
    instance: null,
    changeHistory: [],
    isLoading: false,
    computeChanges() {
      // calculate history of role changes
      let revisions = this.attr('revisions');

      // combine all the changes and sort them by date descending
      let changeHistory = [
        ...makeArray(this._computeObjectChanges(
          revisions.object,
          revisions.revisionsForCompare)),
        ...makeArray(this._computeMappingChanges(revisions.mappings)),
      ];
      changeHistory = loSortBy(changeHistory, 'updatedAt');
      changeHistory = loReverse(changeHistory);

      this.attr('changeHistory', changeHistory);
    },
    /**
     * Compute the the history of object changes from a list of Revisions.
     *
     * The computed list of changes is sorted from oldest to newest (the method
     * assumes that the `revisions` list is also sorted chronologically with
     * the oldest Revision placed first).
     *
     *
     * @param {Array} revisions - the list of revisions of the instance
     *   being handled by the component, sorted from oldest to newest.
     *
     * @param {Array} revisionsForCompare - the list with one or zero revisions
     *   if present will be used to compute changes for first revision.
     *
     * @return {Array} - the history of changes to the instance. Each
     *   element follows the format returned by the `_objectChangeDiff` method.
     */
    _computeObjectChanges: function (revisions, revisionsForCompare) {
      let prevRevision = {content: {}};
      if (revisionsForCompare.length === 1) {
        prevRevision = revisionsForCompare[0];
      }

      revisions = loReverse(revisions);
      let diffList = loMap(revisions, function (revision, i) {
        // default to empty revision
        let prev = revisions[i - 1] || prevRevision;
        return this._objectChangeDiff(prev, revision);
      }.bind(this));
      return loFilter(diffList, 'changes.length');
    },
    /**
     * A helper function for computing the difference between the two Revisions
     * of an object.
     *
     * The function assumes that the given revisions are two distinct Revisions
     * of the same object (application entity).
     *
     * NOTE: The object fields that do not have a user-friendly alias defined are
     * considered 'internal', and are thus not included in the resulting diff
     * objects, because they are not meant to be shown to the end user.
     *
     * @param {Revision} rev1 - the older of the two revisions
     * @param {Revision} rev2 - the newer of the two revisions
     *
     * @return {Object} - A 'diff' object describing the changes between the
     *   revisions. The object has the following attributes:
     *   - madeBy: the user who made the changes
     *   - updatedAt: the time when the changes have been made
     *   - role: highest role at the time of change
     *   - changes:
     *       A list of objects describing the modified attributes of the
     *       instance`, with each object having the following attributes:
     *         - fieldName: the name of the changed`instance` attribute
     *         - origVal: the attribute's original value
     *         - newVal: the attribute's new (modified) value
     */
    _objectChangeDiff: function (rev1, rev2) {
      let diff = {
        madeBy: null,
        updatedAt: null,
        changes: [],
        role: null,
      };
      let attrDefs = GGRC.model_attr_defs[rev2.resource_type];

      diff.madeBy = rev2.modified_by;
      diff.updatedAt = rev2.updated_at;
      diff.role = 'none';

      loForEach(rev2.content, function (value, fieldName) {
        let origVal = rev1.content[fieldName];
        let displayName;
        let unifyValue = function (value) {
          value = value || EMPTY_DIFF_VALUE;
          value = value.length ? value : EMPTY_DIFF_VALUE;
          if (loIsObject(value)) {
            value = value.map((item) =>
              loIsObject(item) ? item.display_name : item
            );
          }
          return value;
        };
        if (attrDefs) {
          displayName = (loFind(attrDefs, function (attr) {
            return attr.attr_name === fieldName;
          }) || {}).display_name;
        } else {
          displayName = fieldName;
        }

        if (displayName && value !== origVal) {
          // format date fields
          if (DATE_FIELDS[fieldName]) {
            if (value) {
              value = formatDate(value, true);
            }
            if (origVal) {
              origVal = formatDate(origVal, true);
            }
          }
          if (LIST_FIELDS[fieldName]) {
            if (value) {
              value = splitTrim(value, ',');
              value = value.sort();
              value = loCompact(value);
              value = value.join(', ');
            }
            if (origVal) {
              origVal = splitTrim(origVal, ',');
              origVal = origVal.sort();
              origVal = loCompact(origVal);
              origVal = origVal.join(', ');
            }
          }
          if (origVal || value) {
            origVal = unifyValue(origVal);
            value = unifyValue(value);
            let isDifferent = false;
            if (loIsObject(origVal) && loIsObject(value)) {
              isDifferent = !loIsEqual(loSortBy(origVal), loSortBy(value));
            } else {
              isDifferent = origVal !== value;
            }

            if (isDifferent) {
              diff.changes.push({
                fieldName: displayName,
                origVal: origVal,
                newVal: value,
              });

              if (fieldName === 'review_status') {
                diff.reviewWasChanged = value.toLowerCase();
              }
            }
          }
        }
      });
      diff.changes = diff.changes.concat(
        this._accessControlListDiff(rev1, rev2)
      );
      diff.changes = diff.changes.concat(
        this._objectCADiff(
          rev1.content.custom_attribute_values,
          rev1.content.custom_attribute_definitions,
          rev2.content.custom_attribute_values,
          rev2.content.custom_attribute_definitions));
      return diff;
    },
    /**
     * A helper function for computing the difference between the two Revisions
     * of an access_control_list.
     * @param {Revision} rev1 - the older of the two revisions
     * @param {Revision} rev2 - the newer of the two revisions
     *
     * @return {Array} - A list of objects describing the modified attributes of the
     * instance's access_control_list, with each object having the following attributes:
     *  - fieldName: the name of the changed custom role
     *  - origVal: the attribute's original value
     *  - newVal: the attribute's new (modified) value
     *  - isRole: the flag describing that diff related to access_control_list
     */
    _accessControlListDiff: function (rev1, rev2) {
      const rev1content = rev1.content;
      const rev2content = rev2.content;
      let diff = [];
      let roles;

      if (!this.attr('instance.type')) {
        return [];
      }

      roles = getRolesForType(this.attr('instance.type'));

      roles.forEach((role) => {
        let rev1people = this._getPeopleForRole(role, rev1content);
        let rev2people = this._getPeopleForRole(role, rev2content);
        let roleDiff;

        // if arrays are not equal by person id
        let idsDiff = loXor(
          loMap(rev1people, (person) => person.id),
          loMap(rev2people, (person) => person.id)
        );
        if (idsDiff.length) {
          roleDiff = new canMap({
            fieldName: role.name,
            origVal: [],
            newVal: [],
            isRole: true,
          });

          roleDiff.attr('origVal', this._buildPeopleEmails(rev1people));
          roleDiff.attr('newVal', this._buildPeopleEmails(rev2people));

          diff.push(roleDiff);
        }
      });

      return diff;
    },
    _objectCADiff: function (origValues, origDefs, newValues, newDefs) {
      let ids;
      let defs;
      let showValue = function (value, def) {
        let obj;
        switch (def.attribute_type) {
          case 'Checkbox':
            return loFlow(Number, Boolean)(value.attribute_value)
              ? '✓'
              : undefined;
          case 'Map:Person':
            if (!value.attribute_object) {
              return;
            }
            obj = Person.findInCacheById(value.attribute_object.id);
            if (obj === undefined) {
              return value.attribute_value;
            }
            return obj.name || obj.email || value.attribute_value;
          case 'Date':
            if (!value.attribute_value) {
              return value.attribute_value;
            }
            return formatDate(value.attribute_value, true);
          default:
            return value.attribute_value;
        }
      };

      origValues = loKeyBy(origValues, 'custom_attribute_id');
      origDefs = loKeyBy(origDefs, 'id');
      newValues = loKeyBy(newValues, 'custom_attribute_id');
      newDefs = loKeyBy(newDefs, 'id');

      ids = loUniq(Object.keys(origValues).concat(Object.keys(newValues)));
      defs = loMerge(origDefs, newDefs);

      let resultIds = loFilter(ids, (id) => !!defs[id]);
      resultIds = loMap(resultIds, (id) => {
        const def = defs[id];
        const diff = {
          fieldName: def.title,
          origVal:
            showValue(origValues[id] || {}, def) || EMPTY_DIFF_VALUE,
          newVal:
            showValue(newValues[id] || {}, def) || EMPTY_DIFF_VALUE,
        };
        if (diff.origVal === diff.newVal) {
          return undefined;
        }
        return diff;
      });
      resultIds = loFilter(resultIds);
      return resultIds;
    },
    /**
     * Compute the instance's object mapping-related changes from the list of
     * mapping revisions.
     *
     * @param {Array} revisions - the list of instance mappings' revision
     *   history, sorted from oldest to newest.
     *
     * @return {Array} - the history of instance mappings' changes. Each
     *   element follows the format returned by the `_mappingChange` helper
     *   method.
     */
    _computeMappingChanges: function (revisions) {
      let chains = loGroupBy(revisions, 'resource_id');
      chains = loMapValues(chains, (chain) => {
        return loSortBy(chain, 'updated_at');
      });

      return loMap(revisions, (revision) =>
        this._mappingChange(revision, chains[revision.resource_id]));
    },
    /**
     * A helper function for extracting the mapping change information from a
     * Revision object.
     *
     * @param {Revision} revision - a Revision object describing a
     *   mapping between the object instance the component is handling, and an
     *   external object
     *
     * @param {Array} chain - revisions of the same resource ordered
     *   chronologically
     *
     * @return {Object} - A 'change' object describing a single modification
     *   of a mapping. The object has the following attributes:
     *   - madeBy: the user who made the changes
     *   - updatedAt: the time when the changes have been made
     *   - role: highest role at the time of change
     *   - changes:
     *       A list of objects describing the modified attributes of the
     *       instance`, with each object having the following attributes:
     *         - fieldName: the name of the changed`instance` attribute
     *         - origVal: the attribute's original value
     *         - newVal: the attribute's new (modified) value
     */
    _mappingChange: function (revision, chain) {
      let object;
      let displayName;
      let displayType;
      let fieldName;
      let origVal;
      let newVal;
      let previous;
      let automapping;
      let person;

      if (revision.destination_type === this.attr('instance.type') &&
        revision.destination_id === this.attr('instance.id')) {
        object = revision.source;
      } else {
        object = revision.destination;
      }

      if (object instanceof Stub) {
        object = reify(object);
      }

      displayName = object.display_name() || object.description;
      displayType = object.display_type() || object.type;
      if (displayType === 'Comment') {
        fieldName = 'Response/Comments';
      } else {
        fieldName = 'Mapping to ' + displayType + ': ' + displayName;
      }

      origVal = EMPTY_DIFF_VALUE;
      newVal = loCapitalize(revision.action);
      previous = chain[loFindIndex(chain, revision) - 1];
      if (revision.action !== 'deleted' &&
        exists(revision.content, 'attrs.AssigneeType')) {
        newVal = revision.content.attrs.AssigneeType;
      }
      if (exists(previous, 'content.attrs.AssigneeType')) {
        origVal = previous.content.attrs.AssigneeType;
      } else if (revision.action === 'deleted') {
        origVal = 'Created';
      }

      // automapping has different description
      automapping = revision.content && revision.content.automapping;
      if (automapping) {
        if (automapping.destination instanceof Stub) {
          automapping.destination = reify(automapping.destination);
        }
        if (automapping.source instanceof Stub) {
          automapping.source = reify(automapping.source);
        }
        if (revision.modified_by) {
          person = revision.modified_by.name || revision.modified_by.email;
        } else {
          person = '"unknown" user';
        }
        const automappingTitle =
          `(automapping triggered after ${person} mapped ` +
          `${automapping.destination.type} "${automapping.destination.title}"` +
          ` to ${automapping.source.type} "${automapping.source.title}")`;
        return {
          automapping: {
            title: automappingTitle,
          },
          updatedAt: revision.updated_at,
          role: 'none',
          changes: {
            origVal: origVal,
            newVal: newVal,
            fieldName: fieldName,
          },
        };
      }

      return {
        madeBy: revision.modified_by,
        updatedAt: revision.updated_at,
        role: 'none',
        changes: {
          origVal: origVal,
          newVal: newVal,
          fieldName: fieldName,
        },
      };
    },
    /**
     * Get people list from access_contro_list by role
     *
     * @param {Object} role - access_control_role object
     *
     * @param {Object} revisionContent - content of current revision
     *
     * @return {Array} - array of people.
     */
    _getPeopleForRole: function (role, revisionContent) {
      if (!revisionContent.access_control_list) {
        return [];
      }

      return revisionContent.access_control_list
        .filter((item) => item.ac_role_id === role.id)
        .map((item) => item.person);
    },
    /**
     * Build list of users emails
     *
     * @param {Array} people - list of people
     *
     * @return {Array} - array of people emails or empty value.
     */
    _buildPeopleEmails: function (people) {
      const peopleList = people.map((person) =>
        Person.findInCacheById(person.id) ?
          Person.findInCacheById(person.id).email :
          ''
      );

      return peopleList.length ? peopleList : [EMPTY_DIFF_VALUE];
    },
  }),
});
