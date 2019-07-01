import {
  GET_LISTS,
  NEW_LIST,
  GET_LISTS_SUCCESS,
  GET_LIST,
  GET_LIST_SUCCESS,
  CLEAR_LISTS,
  PUT_LIST_SETTINGS,
  UPDATE_LIST_TITLE
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  firstFullLoad: true,
  loading: true,
  updatingTitle: false
};

export default function(state = initialState, action) {
  if (action.type === CLEAR_LISTS) {
    return {
      ...state,
      byId: {},
      loading: true,
      firstFullLoad: true
    };
  }
  if (action.type === UPDATE_LIST_TITLE) {
    return {
      ...state,
      updatingTitle: true
    };
  }
  if (action.type === GET_LISTS || action.type === GET_LIST) {
    return {
      ...state,
      loading: true
    };
  }
  if (action.type === GET_LIST_SUCCESS || action.type === PUT_LIST_SETTINGS) {
    const listsById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...listsById
      },
      loading: false,
      updatingTitle: false
    };
  }
  if (action.type === GET_LISTS_SUCCESS) {
    const listsById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...listsById
      },
      loading: false,
      firstFullLoad: false
    };
  }
  if (action.type === NEW_LIST) {
    const list = action.payload;
    return {
      ...state,
      byId: {
        ...state.byId,
        [list.id]: list
      }
    };
  }
  return state;
}
