import React, { Component, Fragment } from 'react';
// import { Provider as AlertProvider } from 'react-alert';
// import AlertTemplate from 'react-alert-template-basic';
import { HashRouter as Router, Route, Switch } from 'react-router-dom';

import Lists from './components/Lists';
import Alerts from './components/Helpers/Alerts';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import List from './components/List';
import Nav from './components/Layout/Nav';
import PrivateRoute from './components/Helpers/PrivateRoute';
import ListSettings from './components/ListSettings';
import Profile from './components/Auth/Profile';

import { Provider } from 'react-redux';
import { store } from './store';
import { loadUser } from './actions/auth';

// Alert Options
// const alertOptions = {
// timeout: 3000,
// position: 'top center'
// };

class App extends Component {
  componentWillMount() {
    store.dispatch(loadUser());
  }

  render() {
    return (
      <Provider store={store}>
        {/* <AlertProvider template={AlertTemplate} {...alertOptions}> */}
        <Router>
          <Fragment>
            <Nav />
            <div>
              <Alerts />
              <Switch>
                <PrivateRoute exact path="/" component={Lists} />
                <Route exact path="/login" component={Login} />
                <Route exact path="/register" component={Register} />
                <PrivateRoute path="/list/:id" component={List} />
                <PrivateRoute path="/profile" component={Profile} />
                <PrivateRoute
                  path="/list_settings/:id"
                  component={ListSettings}
                />
              </Switch>
            </div>
          </Fragment>
        </Router>
        {/* </AlertProvider> */}
      </Provider>
    );
  }
}

export default App;
