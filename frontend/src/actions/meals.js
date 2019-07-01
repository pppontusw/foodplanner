import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';
import {
  GET_MEALS,
  GET_MEALS_SUCCESS,
  NEW_MEAL,
  NEW_MEAL_SUCCESS,
  DELETE_MEAL,
  DELETE_MEAL_SUCCESS,
  PUT_MEALS,
  PUT_MEALS_SUCCESS
} from './types';
import { getList } from './lists';

export const getMealsByList = (
  list_id,
  suppressLoading = false
) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/meals`;
  if (!suppressLoading) {
    dispatch({ type: GET_MEALS });
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_MEALS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const newMeal = (list_id, new_meal_name) => dispatch => {
  const body = {
    name: new_meal_name
  };

  let url = `${API_BASE_URL}/api/lists/${list_id}/meals`;
  dispatch({ type: NEW_MEAL });
  axios
    .post(url, body, axios_config)
    .then(res => {
      dispatch({ type: NEW_MEAL_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

// TODO, for responsiveness, PUT_MEALS should update state
// (and rollback if request fails) as this results in
// a noticeable delay when moving items in the list
export const putMeals = (list_id, data) => dispatch => {
  const body = data;

  let url = `${API_BASE_URL}/api/lists/${list_id}/meals`;
  dispatch({ type: PUT_MEALS });
  axios
    .put(url, body, axios_config)
    .then(res => {
      dispatch({ type: PUT_MEALS_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const deleteMeal = (list_id, meal_id) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/meals/${meal_id}`;
  dispatch({ type: DELETE_MEAL });
  axios
    .delete(url, axios_config)
    .then(res => {
      dispatch({ type: DELETE_MEAL_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};
