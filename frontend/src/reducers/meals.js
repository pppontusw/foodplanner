import {
  GET_MEALS,
  GET_MEALS_SUCCESS,
  CLEAR_MEALS,
  NEW_MEAL_SUCCESS,
  NEW_MEAL,
  DELETE_MEAL,
  DELETE_MEAL_SUCCESS,
  PUT_MEALS_SUCCESS,
  PUT_MEALS
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  loading: true,
  firstFullLoad: true
};

export default function(state = initialState, action) {
  if (action.type === CLEAR_MEALS) {
    return {
      ...state,
      byId: {},
      loading: true,
      firstFullLoad: true
    };
  }
  if (action.type === GET_MEALS) {
    return {
      ...state,
      loading: true
    };
  }
  if (action.type === GET_MEALS_SUCCESS || action.type === NEW_MEAL_SUCCESS) {
    const mealsById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...mealsById
      },
      loading: false
    };
  }
  if (
    action.type === DELETE_MEAL_SUCCESS ||
    action.type === PUT_MEALS_SUCCESS
  ) {
    const mealsById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...mealsById
      },
      loading: false
    };
  }
  return state;
}
