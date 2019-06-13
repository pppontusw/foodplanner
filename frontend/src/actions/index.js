import { GET_LISTS, GET_LIST, CLEAR_LIST, UPDATE_ENTRY, NEW_LIST, GET_LIST_SETTINGS } from './types'
import { returnErrors } from "./messages";
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants'
import axios from 'axios';

export const getData = () => (dispatch) => {

  axios
    .get(`${API_BASE_URL}/api/lists`, axios_config)
    .then(res => {
      dispatch({ type: GET_LISTS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
}

export const getList = (id) => (dispatch) => {

  axios
    .get(`${API_BASE_URL}/api/list/${id}`, axios_config)
    .then(res => {
      dispatch({ type: GET_LIST, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
}

export const updateEntry = (day_index, entry_index, entry_id, text) => (dispatch) => {
  const body = {
    'value': text
  }

  axios
    .post(`${API_BASE_URL}/api/update/${entry_id}`, body, axios_config)
    .then(res => {
      dispatch({
        type: UPDATE_ENTRY, payload: {
          'day_index': day_index,
          'entry_index': entry_index,
          'value': text
        }
      });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
}

export const createList = (listname) => (dispatch) => {
  const body = {
    'listname': listname
  }

  axios
    .post(`${API_BASE_URL}/api/new_list`, body, axios_config)
    .then(res => {
      dispatch({
        type: NEW_LIST, payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });

}

export const getListSettings = (lid) => (dispatch) => {

  axios
    .get(`${API_BASE_URL}/api/list_settings/${lid}`, axios_config)
    .then(res => {
      dispatch({
        type: GET_LIST_SETTINGS, payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });

}


export function clearList() {
  return { type: CLEAR_LIST }
};