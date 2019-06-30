import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';
import { GET_DAYS, GET_DAYS_SUCCESS, GET_ALL_DAYS_SUCCESS } from './types';

export const getDaysByList = (
  list_id,
  offset = 0,
  limit = false,
  suppressLoading = false
) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/days?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  if (!suppressLoading) {
    dispatch({ type: GET_DAYS });
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_DAYS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const getDays = (
  offset = 0,
  limit = false,
  start_today = true
) => dispatch => {
  dispatch({ type: GET_DAYS });
  let url = `${API_BASE_URL}/api/days?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  if (start_today) {
    url += `&start_today=${start_today}`;
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_ALL_DAYS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};
