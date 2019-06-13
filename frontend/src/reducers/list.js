import { GET_LIST, CLEAR_LIST, UPDATE_ENTRY, GET_LIST_SETTINGS } from "../actions/types";
import produce from 'immer';
import { original } from 'immer';

const initialState = {
  list: {
    days: []
  },
  list_settings: {},
  list_shares: []
};

export default function (state = initialState, action) {
  if (action.type === GET_LIST) {
    return {
      list: action.payload
    }
  }
  if (action.type === CLEAR_LIST) {
    return {
      list: {
        days: []
      },
      list_settings: {},
      list_shares: []
    }
  }
  if (action.type === UPDATE_ENTRY) {
    return produce(state, draft => {
      draft.list.days[action.payload['day_index']].entries[action.payload['entry_index']]['value'] = action.payload['value']
    });
  }
  if (action.type === GET_LIST_SETTINGS) {
    return {
      list: {
        ...state.list
      },
      list_settings: action.payload['list_settings'],
      list_shares: action.payload['list_shares']
    }
  }
  return state;
};