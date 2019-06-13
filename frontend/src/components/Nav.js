import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import { logout } from '../actions/auth';

const navStyle = {
  backgroundColor: '#e3f2fd'
};

export class Nav extends Component {
  render() {
    const loggedInNav = (
      <ul className="navbar-nav ml-auto">
        <li className="nav-item mr-2">
          <a className="nav-link" href="#/profile">
            Profile
          </a>
        </li>
        <li className="nav-item">
          <a className="nav-link" onClick={this.props.logout}>
            Logout
          </a>
        </li>
      </ul>
    );

    const loggedOutNav = (
      <ul className="navbar-nav ml-auto">
        <li className="nav-item">
          <a className="nav-link" href="#/login">
            Login
          </a>
        </li>
      </ul>
    );

    return (
      <Fragment>
        <nav className="navbar navbar-expand-lg navbar-light" style={navStyle}>
          <a className="navbar-brand" href="#/">
            Foodplanner
          </a>
          <button
            className="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon" />
          </button>

          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav mr-auto">
              <li className="nav-item active">
                <a className="nav-link" href="#/">
                  Lists <span className="sr-only">(current)</span>
                </a>
              </li>
              <li className="nav-item">
                <a className="nav-link" href="#/">
                  Link
                </a>
              </li>
              <li className="nav-item dropdown">
                <a
                  className="nav-link dropdown-toggle"
                  href="#/"
                  id="navbarDropdown"
                  role="button"
                  data-toggle="dropdown"
                  aria-haspopup="true"
                  aria-expanded="false"
                >
                  Dropdown
                </a>
                <div className="dropdown-menu" aria-labelledby="navbarDropdown">
                  <a className="dropdown-item" href="#/">
                    Action
                  </a>
                  <a className="dropdown-item" href="#/">
                    Another action
                  </a>
                  <div className="dropdown-divider" />
                  <a className="dropdown-item" href="#/">
                    Something else here
                  </a>
                </div>
              </li>
              <li className="nav-item">
                <a
                  className="nav-link disabled"
                  href="#/"
                  tabIndex="-1"
                  aria-disabled="true"
                >
                  Disabled
                </a>
              </li>
            </ul>
            {this.props.isAuthenticated ? loggedInNav : loggedOutNav}
          </div>
        </nav>
        <br />
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
  isAuthenticated: state.auth.isAuthenticated
});

export default connect(
  mapStateToProps,
  { logout }
)(Nav);
