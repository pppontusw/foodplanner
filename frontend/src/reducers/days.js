import {
  GET_DAYS,
  GET_DAYS_SUCCESS,
  GET_ALL_DAYS_SUCCESS
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  loading: true,
  firstFullLoad: true
};

export default function(state = initialState, action) {
  if (action.type === GET_DAYS) {
    return {
      ...state
      // loading: true
    };
  }
  if (action.type === GET_DAYS_SUCCESS) {
    const daysById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...daysById
      },
      loading: false
    };
  }
  if (action.type === GET_ALL_DAYS_SUCCESS) {
    const daysById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...daysById
      },
      loading: false,
      firstFullLoad: false
    };
  }
  return state;
}
