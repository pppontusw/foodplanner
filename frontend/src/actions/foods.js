import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';
import {
  GET_FOODS,
  GET_FOODS_SUCCESS,
  NEW_FOOD,
  NEW_FOOD_SUCCESS,
  DELETE_FOOD,
  DELETE_FOOD_SUCCESS,
  PUT_FOOD_SUCCESS,
  PUT_FOOD
} from './types';
import { getList } from './lists';
import { getCategoriesByList } from './categories';

export const getFoodsByList = list_id => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/foods`;
  dispatch({ type: GET_FOODS });
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_FOODS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const newFood = (list_id, new_food_name) => dispatch => {
  const body = {
    name: new_food_name
  };

  let url = `${API_BASE_URL}/api/lists/${list_id}/foods`;
  dispatch({ type: NEW_FOOD });
  axios
    .post(url, body, axios_config)
    .then(res => {
      dispatch({ type: NEW_FOOD_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

// continue
export const putFood = (list_id, newData) => dispatch => {
  const body = newData;

  let url = `${API_BASE_URL}/api/lists/${list_id}/foods/${newData.id}`;
  dispatch({ type: PUT_FOOD });
  axios
    .put(url, body, axios_config)
    .then(res => {
      dispatch({ type: PUT_FOOD_SUCCESS, payload: res.data });
      dispatch(getCategoriesByList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const deleteFood = (list_id, food_id) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/foods/${food_id}`;
  dispatch({ type: DELETE_FOOD });
  axios
    .delete(url, axios_config)
    .then(res => {
      dispatch({ type: DELETE_FOOD_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};
