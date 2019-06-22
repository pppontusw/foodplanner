import React, { Component } from 'react';
import { Link, Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { login } from '../actions/auth';
import { Form, Button, Icon, Checkbox, Input } from 'antd';

export class Login extends Component {
  state = {
    username: '',
    password: ''
  };

  static propTypes = {
    login: PropTypes.func.isRequired,
    isAuthenticated: PropTypes.bool
  };

  onSubmit = e => {
    e.preventDefault();
    this.props.login(this.state.username, this.state.password);
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  render() {
    if (this.props.isAuthenticated) {
      return <Redirect to="/" />;
    }
    const { username, password } = this.state;
    return (
      <Form
        onSubmit={this.onSubmit}
        style={{ maxWidth: '500px', margin: '20px auto' }}
      >
        <h3 className="text-center">Sign in</h3>
        <Form.Item>
          <Input
            prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
            placeholder="Username"
            name="username"
            onChange={this.onChange}
            value={username}
          />
        </Form.Item>
        <Form.Item>
          <Input
            prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
            placeholder="Password"
            name="password"
            onChange={this.onChange}
            value={password}
          />
        </Form.Item>
        <Form.Item>
          {/* <Checkbox>Remember me</Checkbox> */}
          <Button
            type="primary"
            htmlType="submit"
            className="login-form-button"
            style={{ width: '100%' }}
          >
            Log in
          </Button>
          <Link className="login-form-forgot" to="/forgot">
            Forgot password
          </Link>
          <Link to="/register" style={{ float: 'right' }}>
            Or register now!
          </Link>
        </Form.Item>
      </Form>
      // <div className="col-md-6 m-auto">
      //   <div className="card card-body mt-5">
      //     <form onSubmit={this.onSubmit}>
      //       <div className="form-group">
      //         <label>Username</label>
      //         <input
      //           type="text"
      //           className="form-control"
      //           name="username"
      //           onChange={this.onChange}
      //           value={username}
      //         />
      //       </div>

      //       <div className="form-group">
      //         <label>Password</label>
      //         <input
      //           type="password"
      //           className="form-control"
      //           name="password"
      //           onChange={this.onChange}
      //           value={password}
      //         />
      //       </div>

      //       <div className="form-group">
      //         <button type="submit" className="btn btn-primary">
      //           Login
      //         </button>
      //       </div>
      //       <p>
      //         Don't have an account? <Link to="/register">Register</Link>
      //       </p>
      //     </form>
      //   </div>
      // </div>
    );
  }
}

const mapStateToProps = state => ({
  isAuthenticated: state.auth.isAuthenticated
});

export default connect(
  mapStateToProps,
  { login }
)(Login);
