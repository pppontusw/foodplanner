import { combineReducers } from 'redux';
import auth from './auth';
import lists from './lists';
import days from './days';
import errors from './errors';
import messages from './messages';
import entries from './entries';

export default combineReducers({
  lists,
  days,
  errors,
  entries,
  messages,
  auth
});
