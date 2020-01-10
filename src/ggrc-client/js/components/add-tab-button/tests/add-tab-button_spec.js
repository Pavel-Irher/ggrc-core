/*
  Copyright (C) 2020 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import canMap from 'can-map';
import {getComponentVM} from '../../../../js_specs/spec-helpers';
import Component from '../add-tab-button';
import * as Permission from '../../../permission';

describe('add-tab-button component', () => {
  'use strict';

  let viewModel;

  beforeEach(() => {
    viewModel = getComponentVM(Component);
    viewModel.attr('instance', new canMap());
  });

  describe('isAuditInaccessibleAssessment attribute get() method', () => {
    describe('returns false', () => {
      it('if instance type is not Assessment', () => {
        viewModel.attr('instance.type', 'Type');

        let result = viewModel.attr('isAuditInaccessibleAssessment');

        expect(result).toBe(false);
      });

      it('if instance type is Assessment but there is no audit', () => {
        viewModel.attr('instance', {
          type: 'Assessment',
          audit: null,
        });

        let result = viewModel.attr('isAuditInaccessibleAssessment');

        expect(result).toBe(false);
      });

      it(`if instance type is Assessment, there is audit and
        it is allowed to read instance.audit`, () => {
        viewModel.attr('instance', {
          type: 'Assessment',
          audit: {},
        });
        spyOn(Permission, 'isAllowedFor').and.returnValue(true);

        let result = viewModel.attr('isAuditInaccessibleAssessment');

        expect(result).toBe(false);
      });
    });

    describe('returns true', () => {
      it(`if instance type is Assessment, there is audit but
        it is not allowed to read instance.audit`, () => {
        spyOn(Permission, 'isAllowedFor').and.returnValue(false);
        viewModel.attr('instance', {
          type: 'Assessment',
          audit: {},
        });
        viewModel.attr('isAuditInaccessibleAssessment', false);

        let result = viewModel.attr('isAuditInaccessibleAssessment');

        expect(result).toBe(true);
      });
    });
  });

  describe('helpers', () => {
    let helpers;

    beforeAll(() => {
      helpers = Component.prototype.helpers;
    });

    describe('shouldCreateObject helper', () => {
      let shouldCreateObject;
      let options;
      let instance;
      let model;

      beforeEach(() => {
        shouldCreateObject = helpers.shouldCreateObject;
        options = {
          fn: jasmine.createSpy(),
          inverse: jasmine.createSpy(),
        };
        instance = jasmine.createSpy();
        model = jasmine.createSpy();
      });

      it('calls fn if instance is Program and model is Audit', () => {
        instance.and.returnValue({type: 'Program'});
        model.and.returnValue('Audit');

        shouldCreateObject(instance, model, options);

        expect(options.fn).toHaveBeenCalled();
      });

      it('calls inverse if instance is Program and model is not Audit', () => {
        instance.and.returnValue({type: 'Program'});
        model.and.returnValue('Vendor');

        shouldCreateObject(instance, model, options);

        expect(options.inverse).toHaveBeenCalled();
      });

      it('calls inverse if instance is not Program and model is Audit', () => {
        instance.and.returnValue({type: 'Assessment'});
        model.and.returnValue('Audit');

        shouldCreateObject(instance, model, options);

        expect(options.inverse).toHaveBeenCalled();
      });

      it('calls fn if instance is Assessment and model is Issue', () => {
        instance.and.returnValue({type: 'Assessment'});
        model.and.returnValue('Issue');

        shouldCreateObject(instance, model, options);

        expect(options.fn).toHaveBeenCalled();
      });

      it('calls inverse if instance is Assessment and model is not Issue',
        () => {
          instance.and.returnValue({type: 'Assessment'});
          model.and.returnValue('Vendor');

          shouldCreateObject(instance, model, options);

          expect(options.inverse).toHaveBeenCalled();
        });

      it('calls inverse if instance is not Assessment and model is Issue',
        () => {
          instance.and.returnValue({type: 'Program'});
          model.and.returnValue('Issue');

          shouldCreateObject(instance, model, options);

          expect(options.inverse).toHaveBeenCalled();
        });
    });
  });
});
