import {
  GET_LISTS,
  GET_LIST,
  NEW_LIST,
  GET_LIST_SETTINGS,
  GET_LISTS_SUCCESS,
  GET_LIST_SUCCESS
} from './types';
import { getDaysByList } from './days';
import { getEntriesByList } from './entries';
import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';

export const getLists = (start_today = true) => dispatch => {
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
      dispatch(getDaysByList(res.data.id));
      dispatch(getEntriesByList(res.data.id));
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
