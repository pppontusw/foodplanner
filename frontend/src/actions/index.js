import {
  GET_LISTS,
  GET_LIST,
  CLEAR_LIST,
  UPDATE_ENTRY,
  NEW_LIST,
  GET_LIST_SETTINGS,
  GET_DAYS,
  GET_ENTRIES,
  GET_LISTS_SUCCESS,
  GET_DAYS_SUCCESS,
  GET_ENTRIES_SUCCESS,
  GET_LIST_SUCCESS,
  GET_ALL_ENTRIES_SUCCESS,
  GET_ALL_DAYS_SUCCESS
} from './types';
import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';

export const getData = () => dispatch => {
  dispatch({ type: GET_LISTS });
  axios
    .get(`${API_BASE_URL}/api/lists`, axios_config)
    .then(res => {
      dispatch({ type: GET_LISTS_SUCCESS, payload: res.data });
      dispatch(getFrontPage());
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getList = list_id => dispatch => {
  dispatch({ type: GET_LIST });
  axios
    .get(`${API_BASE_URL}/api/list/${list_id}`, axios_config)
    .then(res => {
      dispatch({ type: GET_LIST_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getDays = list_id => dispatch => {
  dispatch({ type: GET_DAYS });
  axios
    .get(`${API_BASE_URL}/api/days/${list_id}`, axios_config)
    .then(res => {
      dispatch({ type: GET_DAYS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getFrontPage = () => dispatch => {
  dispatch({ type: GET_DAYS });
  dispatch({ type: GET_ENTRIES });
  axios
    .get(`${API_BASE_URL}/api/days`, axios_config)
    .then(res => {
      dispatch({ type: GET_ALL_DAYS_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });

  axios
    .get(`${API_BASE_URL}/api/entry`, axios_config)
    .then(res => {
      dispatch({ type: GET_ALL_ENTRIES_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getDaysAndEntries = list_id => dispatch => {
  dispatch({ type: GET_DAYS });
  axios
    .get(`${API_BASE_URL}/api/days/${list_id}`, axios_config)
    .then(res => {
      dispatch({ type: GET_DAYS_SUCCESS, payload: res.data });
      dispatch(getEntries(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err));
    });
};

export const getEntries = list_id => dispatch => {
  dispatch({ type: GET_ENTRIES });
  axios
    .get(`${API_BASE_URL}/api/entries/${list_id}`, axios_config)
    .then(res => {
      dispatch({ type: GET_ENTRIES_SUCCESS, payload: res.data });
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
    .post(`${API_BASE_URL}/api/update/${entry_id}`, body, axios_config)
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

export const createList = listname => dispatch => {
  const body = {
    listname: listname
  };

  axios
    .post(`${API_BASE_URL}/api/new_list`, body, axios_config)
    .then(res => {
      dispatch({
        type: NEW_LIST,
        payload: res.data
      });
      dispatch(getDaysAndEntries(res.data.id));
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
