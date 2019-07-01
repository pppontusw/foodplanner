import {
  GET_SHARES,
  GET_SHARES_SUCCESS,
  CLEAR_SHARES,
  NEW_SHARE_SUCCESS,
  NEW_SHARE,
  DELETE_SHARE,
  DELETE_SHARE_SUCCESS
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  loading: true,
  firstFullLoad: true
};

export default function(state = initialState, action) {
  if (action.type === CLEAR_SHARES) {
    return {
      ...state,
      byId: {},
      loading: true,
      firstFullLoad: true
    };
  }
  if (action.type === GET_SHARES) {
    return {
      ...state,
      loading: true
    };
  }
  if (action.type === GET_SHARES_SUCCESS || action.type === NEW_SHARE_SUCCESS) {
    const sharesById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...sharesById
      },
      loading: false
    };
  }
  if (action.type === DELETE_SHARE_SUCCESS) {
    const sharesById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...sharesById
      },
      loading: false
    };
  }
  return state;
}
