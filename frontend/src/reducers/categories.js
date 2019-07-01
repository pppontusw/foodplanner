import {
  GET_CATEGORIES,
  GET_CATEGORIES_SUCCESS,
  CLEAR_CATEGORIES,
  NEW_CATEGORY_SUCCESS,
  DELETE_CATEGORY_SUCCESS
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  loading: true,
  firstFullLoad: true
};

export default function(state = initialState, action) {
  if (action.type === CLEAR_CATEGORIES) {
    return {
      ...state,
      byId: {},
      loading: true,
      firstFullLoad: true
    };
  }
  if (action.type === GET_CATEGORIES) {
    return {
      ...state,
      loading: true
    };
  }
  if (
    action.type === GET_CATEGORIES_SUCCESS ||
    action.type === NEW_CATEGORY_SUCCESS
  ) {
    const categoriesById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...categoriesById
      },
      loading: false
    };
  }
  if (action.type === DELETE_CATEGORY_SUCCESS) {
    const categoriesById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...categoriesById
      },
      loading: false
    };
  }
  return state;
}
