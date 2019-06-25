import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';
import {
  GET_ENTRIES,
  GET_ENTRIES_SUCCESS,
  UPDATE_ENTRY,
  GET_ALL_ENTRIES_SUCCESS
} from './types';

export const getEntriesByList = (
  list_id,
  offset = 0,
  limit = false
) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/entries?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  dispatch({ type: GET_ENTRIES });
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_ENTRIES_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getEntries = (
  offset = 0,
  limit = false,
  start_today = true
) => dispatch => {
  dispatch({ type: GET_ENTRIES });
  let url = `${API_BASE_URL}/api/entries?offset=${offset}`;
  if (limit) {
    url += `&limit=${limit}`;
  }
  if (start_today) {
    url += `&start_today=${start_today}`;
  }
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({
        type: GET_ALL_ENTRIES_SUCCESS,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const updateEntry = (entry_id, text) => dispatch => {
  const body = {
    value: text
  };

  axios
    .put(`${API_BASE_URL}/api/entries/${entry_id}`, body, axios_config)
    .then(res => {
      dispatch({
        type: UPDATE_ENTRY,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};
