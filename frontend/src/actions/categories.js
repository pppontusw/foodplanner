import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';
import {
  GET_CATEGORIES,
  GET_CATEGORIES_SUCCESS,
  NEW_CATEGORY,
  NEW_CATEGORY_SUCCESS,
  DELETE_CATEGORY,
  DELETE_CATEGORY_SUCCESS
} from './types';
import { getList } from './lists';

export const getCategoriesByList = list_id => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/categories`;
  dispatch({ type: GET_CATEGORIES });
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_CATEGORIES_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const newCategory = (list_id, new_category_name) => dispatch => {
  const body = {
    name: new_category_name
  };

  let url = `${API_BASE_URL}/api/lists/${list_id}/categories`;
  dispatch({ type: NEW_CATEGORY });
  axios
    .post(url, body, axios_config)
    .then(res => {
      dispatch({ type: NEW_CATEGORY_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const deleteCategory = (list_id, category_id) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/categories/${category_id}`;
  dispatch({ type: DELETE_CATEGORY });
  axios
    .delete(url, axios_config)
    .then(res => {
      dispatch({ type: DELETE_CATEGORY_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};
