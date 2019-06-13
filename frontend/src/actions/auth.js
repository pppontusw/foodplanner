import axios from "axios";
import { returnErrors } from "./messages";
import { API_BASE_URL } from '../constants'

import {
  USER_LOADED,
  USER_LOADING,
  AUTH_ERROR,
  LOGIN_SUCCESS,
  LOGIN_FAIL,
  LOGOUT_SUCCESS,
  REGISTER_SUCCESS,
  REGISTER_FAIL,
  CLEAR_LISTS
} from "./types";


export const axios_config = {
  headers: {
    "Content-Type": "application/json"
  },
  withCredentials: true
};

// CHECK TOKEN & LOAD USER
export const loadUser = () => (dispatch, getState) => {
  // User Loading
  dispatch({ type: USER_LOADING });

  axios
    .get(`${API_BASE_URL}/api/auth/user`, {withCredentials: true})
    .then(res => {
      dispatch({
        type: USER_LOADED,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
      dispatch({
        type: AUTH_ERROR
      });
    });
};

// LOGIN USER
export const login = (username, password) => dispatch => {

  // Request Body
  const body = JSON.stringify({ username, password });

  axios
    .post(`${API_BASE_URL}/api/auth/login`, body, axios_config)
    .then(res => {
      dispatch({
        type: LOGIN_SUCCESS,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch({
        type: LOGIN_FAIL
      });
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};

// REGISTER USER
export const register = ({ username, firstname, lastname, password, email }) => dispatch => {

  // Request Body
  const body = JSON.stringify({ username, firstname, lastname, email, password });

  axios
    .post(`${API_BASE_URL}/api/auth/register`, body, axios_config)
    .then(res => {
      dispatch({
        type: REGISTER_SUCCESS,
        payload: res.data
      });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
      dispatch({
        type: REGISTER_FAIL
      });
    });
};

// LOGOUT USER
export const logout = () => (dispatch, getState) => {
  axios
    .get(`${API_BASE_URL}/api/auth/logout`, {withCredentials: true})
    .then(res => {
      dispatch({
        type: LOGOUT_SUCCESS
      });
      dispatch({
        type: CLEAR_LISTS
      });
    })
    .catch(err => {
      dispatch(returnErrors(err.response.data, err.response.status));
    });
};