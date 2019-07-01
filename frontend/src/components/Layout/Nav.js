import React, { Component } from 'react';
import { connect } from 'react-redux';
import { logout } from '../../actions/auth';
import { Menu } from 'antd';

class Nav extends Component {
  render() {
    const loggedInNav = [
      <Menu.Item
        key="logout"
        onClick={this.props.logout}
        style={{ float: 'right' }}
      >
        Logout
      </Menu.Item>,
      <Menu.Item key="profile" style={{ float: 'right' }}>
        <a href="#/profile">Profile</a>
      </Menu.Item>
    ];

    const loggedOutNav = (
      <Menu.Item key="login" style={{ float: 'right' }}>
        <a href="#/login">Login</a>
      </Menu.Item>
    );

    return (
      <Menu mode="horizontal">
        <Menu.Item key="mail">
          <a href="#/">Foodplanner</a>
        </Menu.Item>
        {this.props.isAuthenticated ? loggedInNav : loggedOutNav}
      </Menu>
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
