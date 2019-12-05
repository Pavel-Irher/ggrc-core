/*
 Copyright (C) 2019 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import canMap from 'can-map';
import {getComponentVM} from '../../../../js_specs/spec-helpers';
import Component from '../request-review-modal';
import * as ObjectReviewUtils from '../../../plugins/utils/object-review-utils';
import Review from '../../../models/service-models/review';

describe('request-review-modal component', () => {
  let viewModel;

  beforeEach(() => {
    viewModel = getComponentVM(Component);
  });

  describe('"isValidForm" getter', () => {
    beforeEach(() => {
      const review = new Review();

      viewModel.attr('review', review);
    });

    it('should return flase if ACL is empty', () => {
      expect(viewModel.attr('isValidForm')).toBeFalsy();
    });

    it('should return true if ACL is not empty', () => {
      viewModel.attr('review.access_control_list', [{person_id: 1}]);

      expect(viewModel.attr('isValidForm')).toBeTruthy();
    });
  });

  describe('"disabled" getter', () => {
    beforeEach(() => {
      const review = new Review();

      viewModel.attr({loading: false, review});
    });

    describe('if ACL is empty', () => {
      it('should return true', () => {
        expect(viewModel.attr('disabled')).toBeTruthy();
      });
    });

    describe('if ACL is not empty', () => {
      beforeEach(() => {
        viewModel.attr('review.access_control_list', [{person_id: 1}]);
      });

      it('should return false', () => {
        expect(viewModel.attr('disabled')).toBeFalsy();
      });

      it('should return true if loading attr is set to true', () => {
        viewModel.attr('loading', true);

        expect(viewModel.attr('disabled')).toBeTruthy();
      });
    });
  });

  describe('save() method', () => {
    const originalEmailComment = 'email comment...';
    const newACL = [{person_id: 1}];
    let saveDfd;
    let review;
    beforeEach(() => {
      saveDfd = $.Deferred();
      review = new Review({
        access_control_list: [],
        email_message: originalEmailComment,
      });

      spyOn(ObjectReviewUtils, 'saveReview').and.returnValue(saveDfd);

      viewModel.attr('review', review);
      viewModel.attr('modalState.open', true);
      viewModel.attr('parentInstance', {dispatch: () => {}});
    });

    it('should not save review in case of empty ACL', () => {
      viewModel.save();

      expect(ObjectReviewUtils.saveReview).not.toHaveBeenCalled();
    });

    it('should update ACL', (done) => {
      expect(viewModel.attr('review.access_control_list').serialize())
        .toEqual([]);

      review.attr('access_control_list', newACL);
      viewModel.save();

      saveDfd.then(() => {
        expect(ObjectReviewUtils.saveReview).toHaveBeenCalled();
        expect(viewModel.attr('review.access_control_list').serialize())
          .toEqual(newACL);
        done();
      });
      saveDfd.resolve(review);
    });

    it('should update "Email" notification text', () => {
      const fakeMsg = 'Some message';

      viewModel.attr('review.access_control_list', newACL);
      viewModel.attr('reviewEmailMessage', fakeMsg);

      viewModel.save();

      expect(viewModel.attr('review.email_message')).toEqual(fakeMsg);
    });

    it('should set Unreviewed status', (done) => {
      viewModel.attr('review.access_control_list', newACL);
      viewModel.attr('review.status', 'Reviewed');

      viewModel.save();

      saveDfd.then(() => {
        expect(ObjectReviewUtils.saveReview).toHaveBeenCalled();
        expect(viewModel.attr('review.status')).toEqual('Unreviewed');
        done();
      });
      saveDfd.resolve(review);
    });

    it('should change modal window state to false', (done) => {
      viewModel.attr('review.access_control_list', newACL);

      expect(viewModel.attr('modalState.open')).toBeTruthy();

      viewModel.save();

      saveDfd.then(() => {
        expect(viewModel.attr('modalState.open')).toBeFalsy();
        done();
      });
      saveDfd.resolve(review);
    });

    it('should change loading value to false', (done) => {
      viewModel.attr('review.access_control_list', newACL);

      viewModel.save();
      expect(viewModel.attr('loading')).toBeTruthy();

      saveDfd.then(() => {
        expect(viewModel.attr('loading')).toBeFalsy();
        done();
      });
      saveDfd.resolve(review);
    });
  });

  describe('cancel() method', () => {
    beforeEach(() => {
      const review = new canMap();
      review.restore = jasmine.createSpy('restore');
      viewModel.attr('review', review);
    });

    it('should change modal open state to false', () => {
      viewModel.attr('modalState.open', true);

      viewModel.cancel();

      expect(viewModel.attr('modalState.open')).toBe(false);
    });

    it('should restore Review model', () => {
      viewModel.cancel();

      expect(viewModel.attr('review').restore).toHaveBeenCalledWith(true);
    });

    it('should set reviewEmailMessage to null', () => {
      viewModel.attr('reviewEmailMessage', 'some value');

      viewModel.cancel();

      expect(viewModel.attr('reviewEmailMessage')).toBeNull();
    });
  });
});
