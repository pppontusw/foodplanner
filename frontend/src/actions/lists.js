import {
  GET_LISTS,
  GET_LIST,
  CLEAR_LISTS,
  NEW_LIST,
  GET_LIST_SETTINGS,
  GET_LISTS_SUCCESS,
  GET_LIST_SUCCESS,
  GET_ENTRIES,
  GET_DAYS,
  CLEAR_DAYS,
  CLEAR_ENTRIES,
  PUT_LIST_SETTINGS
} from './types';
import { getDaysByListThenEntries } from './days';
import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';

export const getLists = (start_today = true) => dispatch => {
  dispatch({ type: CLEAR_LISTS });
  dispatch({ type: CLEAR_DAYS });
  dispatch({ type: CLEAR_ENTRIES });
  dispatch({ type: GET_LISTS });
  axios
    .get(`${API_BASE_URL}/api/lists?start_today=${start_today}`, axios_config)
    .then(res => {
      dispatch({ type: GET_LISTS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getList = (list_id, offset = 0, limit = false) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  dispatch({ type: GET_LIST });
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_LIST_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getListThenDaysThenEntries = (
  list_id,
  offset = 0,
  limit = false,
  suppressLoading = false
) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  if (!suppressLoading) {
    dispatch({ type: GET_LIST });
    dispatch({ type: GET_DAYS });
    dispatch({ type: GET_ENTRIES });
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_LIST_SUCCESS, payload: res.data });
      dispatch(
        getDaysByListThenEntries(list_id, offset, limit, suppressLoading)
      );
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const createList = listname => dispatch => {
  const body = {
    listname: listname
  };

  axios
    .post(`${API_BASE_URL}/api/lists`, body, axios_config)
    .then(res => {
      dispatch({
        type: NEW_LIST,
        payload: res.data
      });
      dispatch(getDaysByListThenEntries(res.data.id));
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getListSettings = lid => dispatch => {
  axios
    .get(`${API_BASE_URL}/api/list_settings/${lid}`, axios_config)
    .then(res => {
      dispatch({
        type: GET_LIST_SETTINGS,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const putListSettings = (
  list_id,
  days_to_display,
  start_day_of_week
) => dispatch => {
  const body = {
    days_to_display,
    start_day_of_week
  };

  axios
    .put(`${API_BASE_URL}/api/lists/${list_id}/settings`, body, axios_config)
    .then(res => {
      dispatch({
        type: PUT_LIST_SETTINGS,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};
