import {
  GET_LISTS,
  GET_LIST,
  CLEAR_LISTS,
  NEW_LIST,
  GET_LIST_SETTINGS,
  GET_LISTS_SUCCESS,
  GET_LIST_SUCCESS,
  PUT_LIST_SETTINGS,
  UPDATE_LIST_TITLE
} from './types';
import { getDaysByList } from './days';
import { getEntriesByList } from './entries';
import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';

export const getLists = (
  offset = 0,
  limit = false,
  start_today = true
) => dispatch => {
  dispatch({ type: CLEAR_LISTS });
  dispatch({ type: GET_LISTS });
  let url = `${API_BASE_URL}/api/lists?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  if (start_today) {
    url += `&start_today=${start_today}`;
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_LISTS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getList = (
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
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_LIST_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const createList = (
  listname,
  offset = 0,
  limit = 2,
  start_today = true
) => dispatch => {
  const body = {
    listname: listname
  };

  axios
    .post(
      `${API_BASE_URL}/api/lists?start_today=${start_today}&limit=${limit}`,
      body,
      axios_config
    )
    .then(res => {
      dispatch({
        type: NEW_LIST,
        payload: res.data
      });
      dispatch(getDaysByList(res.data.id, offset, limit, start_today));
      dispatch(getEntriesByList(res.data.id, offset, limit, start_today));
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const renameList = (list_id, listname) => dispatch => {
  const body = {
    listname: listname
  };

  dispatch({
    type: UPDATE_LIST_TITLE
  });

  axios
    .patch(`${API_BASE_URL}/api/lists/${list_id}`, body, axios_config)
    .then(res => {
      dispatch({
        type: GET_LIST_SUCCESS,
        payload: res.data
      });
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
