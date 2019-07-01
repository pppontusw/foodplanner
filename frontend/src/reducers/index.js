import { combineReducers } from 'redux';
import auth from './auth';
import lists from './lists';
import days from './days';
import errors from './errors';
import messages from './messages';
import entries from './entries';
import shares from './shares';
import meals from './meals';
import foods from './foods';
import categories from './categories';

export default combineReducers({
  lists,
  days,
  errors,
  entries,
  messages,
  auth,
  shares,
  meals,
  foods,
  categories
});
