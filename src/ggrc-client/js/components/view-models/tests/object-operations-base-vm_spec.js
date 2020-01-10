/*
 Copyright (C) 2020 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import loEvery from 'lodash/every';
import canMap from 'can-map';
import ObjectOperationsBaseVM from '../object-operations-base-vm';
import * as Mappings from '../../../models/mappers/mappings';
import * as modelsUtils from '../../../plugins/utils/models-utils';
import Control from '../../../models/business-models/control';

describe('object-operations-base viewModel', function () {
  'use strict';

  let baseVM;

  beforeEach(function () {
    baseVM = ObjectOperationsBaseVM();
  });

  describe('availableTypes() method', () => {
    it('returns grouped types if object is not Assessment', () => {
      baseVM.attr('object', 'testObject');

      spyOn(Mappings, 'getMappingList').and.returnValue('list');
      spyOn(modelsUtils, 'groupTypes')
        .withArgs('list')
        .and.returnValue('grouped allowed to map objects');

      expect(baseVM.availableTypes()).toEqual('grouped allowed to map objects');
    });

    it('returns grouped types if object is Assessment', () => {
      baseVM.attr('object', 'Assessment');

      spyOn(modelsUtils, 'groupTypes')
        .withArgs(GGRC.config.snapshotable_objects)
        .and.returnValue('grouped snapshotable objects');

      expect(baseVM.availableTypes()).toEqual('grouped snapshotable objects');
    });
  });

  describe('get() for baseVM.parentInstance', function () {
    beforeEach(function () {
      spyOn(modelsUtils, 'getInstance')
        .and.returnValue('parentInstance');
    });

    it('returns parentInstance', function () {
      let result = baseVM.attr('parentInstance');
      expect(result).toEqual('parentInstance');
    });
  });

  describe('get() for baseVM.model', () => {
    it('returns model based on type attribute', () => {
      baseVM.attr('type', 'Control');

      let result = baseVM.attr('model');
      expect(result).toEqual(Control);
    });
  });

  describe('set() for baseVM.type', function () {
    let method;
    let vm;

    beforeEach(function () {
      vm = new canMap({
        config: {
          general: {},
          special: [
            {
              types: ['Type1', 'Type2'],
              config: {},
            },
            {
              types: ['Type1'],
              config: {},
            },
          ],
        },
        update: jasmine.createSpy('update'),
      });
      method = ObjectOperationsBaseVM
        .prototype
        .define
        .type
        .set.bind(vm);
    });

    it('sets passed type', function () {
      let type = 'Type1';
      let result = method(type);
      expect(result).toBe(type);
    });

    it('calls update method',
      function () {
        let type = 'Type1';
        method(type);
        expect(vm.update).toHaveBeenCalled();
      });

    it('removes "type" property from config passed in appopriate ' +
    'config handler', function () {
      let args;
      method('Type1');

      args = vm.update.calls.argsFor(0);
      expect(args[0]).not.toEqual(jasmine.objectContaining({
        type: jasmine.any(String),
      }));
    });
  });

  describe('update() method', function () {
    let baseConfig;
    let method;
    let vm;

    beforeEach(function () {
      baseConfig = {
        a: 'a',
        b: {
          c: 'c',
        },
      };
      vm = new canMap(baseConfig);
      method = baseVM.update.bind(vm);
      spyOn(vm, 'attr').and.callThrough();
    });

    it('sets new values for VM', function () {
      let config = {
        a: 'new A',
        b: {
          h: 'new H',
        },
        c: [],
      };
      method(config);

      expect(vm.attr()).toEqual(config);
    });

    it('does not set values for VM from config if appopriate fields from ' +
    'VM and config have the same values', function () {
      let allArgs;
      method(baseConfig);

      allArgs = vm.attr.calls.allArgs();

      expect(loEvery(allArgs, function (args) {
        return args.length === 1;
      })).toBe(true);
    });
  });

  describe('extractConfig() method', function () {
    let method;
    let config;

    beforeAll(function () {
      method = ObjectOperationsBaseVM.extractConfig;
    });

    beforeEach(function () {
      config = {
        general: {},
        special: [{
          types: ['T1', 'T2'],
          config: {},
        }, {
          types: ['T3'],
          config: {
            field: 1,
            field2: 2,
          },
        }],
      };
    });

    it('extracts general config if there is no special config for type',
      function () {
        let result = method('T0', config);
        expect(result).toBe(config.general);
      });

    it('extracts special config if there is special config for type',
      function () {
        let result = method('T2', config);
        expect(result).toEqual(config.special[0].config);
      });
  });
});
