import { combineReducers } from "redux";
import auth from './auth'
import lists from "./lists";
import list from "./list";
import errors from "./errors";
import messages from "./messages";

export default combineReducers({
  lists,
  list,
  errors,
  messages,
  auth
});