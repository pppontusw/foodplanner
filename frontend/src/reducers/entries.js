import {
  GET_ENTRIES,
  UPDATE_ENTRY,
  GET_ENTRIES_SUCCESS,
  GET_ALL_ENTRIES_SUCCESS,
  CLEAR_ENTRIES
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  loading: true,
  firstFullLoad: true
};

export default function(state = initialState, action) {
  if (action.type === CLEAR_ENTRIES) {
    return {
      ...state,
      byId: {},
      loading: true,
      firstFullLoad: true
    };
  }
  if (action.type === GET_ENTRIES) {
    return {
      ...state,
      loading: true
    };
  }
  if (action.type === GET_ENTRIES_SUCCESS) {
    const entriesById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...entriesById
      },
      loading: false
    };
  }
  if (action.type === GET_ALL_ENTRIES_SUCCESS) {
    const entriesById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...entriesById
      },
      loading: false,
      firstFullLoad: false
    };
  }
  if (action.type === UPDATE_ENTRY) {
    return {
      ...state,
      byId: {
        ...state.byId,
        [action.payload.id]: action.payload
      }
    };
  }
  return state;
}
