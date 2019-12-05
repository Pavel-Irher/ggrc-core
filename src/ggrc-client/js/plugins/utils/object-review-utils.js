/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Review from '../../models/service-models/review';
import {refreshPermissions} from '../../permission';

const createReviewInstance = (reviewableInstance) => {
  return new Review({
    access_control_list: [],
    notification_type: 'email',
    context: null,
    reviewable: reviewableInstance,
  });
};
const saveReview = (review, reviewableInstance) => {
  if (!review.isNew()) {
    return review.save().then(async (review) => {
      /**
       * Refresh ReviewableInstance to get E-tag after PUT
       */
      await reviewableInstance.refresh();
      return review;
    });
  }

  return review.save().then(async () => {
    /**
     * We need to refresh Permission because user with Edit rights should have
     * permission for Review object after POST review.
     * ReviewableInstance should also be refreshed after POST review
     * to get review stub in properties
     */
    await Promise.all([refreshPermissions(), reviewableInstance.refresh()]);
    /**
     * Refresh Review object to get E-tag
     */
    return review.refresh();
  });
};

export {
  createReviewInstance,
  saveReview,
};
