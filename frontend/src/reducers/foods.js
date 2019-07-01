import {
  GET_FOODS,
  GET_FOODS_SUCCESS,
  CLEAR_FOODS,
  NEW_FOOD_SUCCESS,
  NEW_FOOD,
  DELETE_FOOD,
  DELETE_FOOD_SUCCESS,
  PUT_FOOD,
  PUT_FOOD_SUCCESS
} from '../actions/types';
import _ from 'lodash';

const initialState = {
  byId: {},
  loading: true,
  firstFullLoad: true,
  updatingFoods: false
};

export default function(state = initialState, action) {
  if (action.type === CLEAR_FOODS) {
    return {
      ...state,
      byId: {},
      loading: true,
      firstFullLoad: true
    };
  }
  if (action.type === GET_FOODS) {
    return {
      ...state,
      loading: true
    };
  }
  if (action.type === PUT_FOOD) {
    return {
      ...state,
      updatingFoods: true
    };
  }
  if (
    action.type === GET_FOODS_SUCCESS ||
    action.type === NEW_FOOD_SUCCESS ||
    action.type === PUT_FOOD_SUCCESS
  ) {
    const foodsById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...state.byId,
        ...foodsById
      },
      loading: false,
      updatingFoods: false
    };
  }
  if (action.type === DELETE_FOOD_SUCCESS) {
    const foodsById = _.keyBy(action.payload, 'id');
    return {
      ...state,
      byId: {
        ...foodsById
      },
      loading: false
    };
  }
  return state;
}
