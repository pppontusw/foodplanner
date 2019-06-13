import { GET_LISTS, NEW_LIST, CLEAR_LISTS } from "../actions/types";
import produce from 'immer';

const initialState = {
  lists: []
};

export default function (state = initialState, action) {
  if (action.type === GET_LISTS) {
    return {
      lists: action.payload
    }
  }
  if (action.type === NEW_LIST) {
    return produce(state, draft => {
      draft.lists.push(action.payload)
    });
  }
  if (action.type === CLEAR_LISTS) {
    return {
      lists: []
    }
  }
  return state;
};