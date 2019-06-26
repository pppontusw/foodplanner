import { returnErrors } from './messages';
import { axios_config } from './auth';
import { API_BASE_URL } from '../constants';
import axios from 'axios';
import {
  GET_SHARES,
  GET_SHARES_SUCCESS,
  NEW_SHARE,
  NEW_SHARE_SUCCESS,
  DELETE_SHARE,
  DELETE_SHARE_SUCCESS
} from './types';
import { getList } from './lists';

export const getSharesByList = list_id => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/shares`;
  dispatch({ type: GET_SHARES });
  axios
    .get(url, axios_config)
    .then(res => {
      dispatch({ type: GET_SHARES_SUCCESS, payload: res.data });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const newShare = (list_id, new_share_username) => dispatch => {
  const body = {
    username: new_share_username
  };

  let url = `${API_BASE_URL}/api/lists/${list_id}/shares`;
  dispatch({ type: NEW_SHARE });
  axios
    .post(url, body, axios_config)
    .then(res => {
      dispatch({ type: NEW_SHARE_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

export const deleteShare = (list_id, share_id) => dispatch => {
  let url = `${API_BASE_URL}/api/lists/${list_id}/shares/${share_id}`;
  dispatch({ type: DELETE_SHARE });
  axios
    .delete(url, axios_config)
    .then(res => {
      dispatch({ type: DELETE_SHARE_SUCCESS, payload: res.data });
      dispatch(getList(list_id));
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};
