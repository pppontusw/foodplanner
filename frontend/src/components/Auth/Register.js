import React, { Component } from 'react';
import { Link, Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { register } from '../../actions/auth';
import { createMessage } from '../../actions/messages';
import { Form, Button, Input } from 'antd';

class Register extends Component {
  state = {
    username: '',
    email: '',
    firstname: '',
    lastname: '',
    password: '',
    password2: ''
  };

  static propTypes = {
    register: PropTypes.func.isRequired,
    isAuthenticated: PropTypes.bool
  };

  onSubmit = e => {
    e.preventDefault();
    const {
      username,
      email,
      firstname,
      lastname,
      password,
      password2
    } = this.state;
    if (password !== password2) {
      this.props.createMessage({ passwordNotMatch: 'Passwords do not match' });
    } else {
      const newUser = {
        username,
        firstname,
        lastname,
        password,
        email
      };
      this.props.register(newUser);
    }
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  render() {
    if (this.props.isAuthenticated) {
      return <Redirect to="/" />;
    }
    const {
      username,
      email,
      firstname,
      lastname,
      password,
      password2
    } = this.state;
    return (
      <Form
        onSubmit={this.onSubmit}
        layout="horizontal"
        style={{ maxWidth: '800px', margin: '20px auto' }}
      >
        <h2 className="text-center">Register</h2>
        <Form.Item className="form-group">
          <Input
            // prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
            type="text"
            className="form-control"
            name="username"
            onChange={this.onChange}
            value={username}
            placeholder="Username"
          />
        </Form.Item>
        <Form.Item className="form-group">
          <Input
            // prefix={<Icon type="mail" style={{ color: 'rgba(0,0,0,.25)' }} />}
            type="email"
            className="form-control"
            name="email"
            onChange={this.onChange}
            value={email}
            placeholder="Email"
          />
        </Form.Item>
        <Form.Item className="form-group">
          <Input
            type="text"
            className="form-control"
            name="firstname"
            onChange={this.onChange}
            value={firstname}
            placeholder="Firstname"
          />
        </Form.Item>
        <Form.Item>
          <Input
            type="text"
            className="form-control"
            name="lastname"
            onChange={this.onChange}
            value={lastname}
            placeholder="Lastname"
          />
        </Form.Item>
        <Form.Item>
          <Input
            // prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
            type="password"
            className="form-control"
            name="password"
            onChange={this.onChange}
            value={password}
            placeholder="Password"
          />
        </Form.Item>
        <Form.Item>
          <Input
            // prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
            type="password"
            className="form-control"
            name="password2"
            onChange={this.onChange}
            value={password2}
            placeholder="Confirm Password"
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
            Register
          </Button>
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </Form.Item>
      </Form>
    );
  }
}

const mapStateToProps = state => ({
  isAuthenticated: state.auth.isAuthenticated
});

export default connect(
  mapStateToProps,
  { register, createMessage }
)(Register);
