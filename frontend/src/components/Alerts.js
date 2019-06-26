import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { notification } from 'antd';

const openNotificationWithIcon = (type, status, description) => {
  let title;

  switch (status) {
    case 400:
      title = 'Request Error';
      break;
    case 401:
      title = 'Login Failed';
      break;
    case 403:
      title = 'Permission Denied';
      break;
    case 404:
      title = 'Not Found';
      break;
    case 500:
      title = 'Server Error';
      break;
    default:
      title = status;
      break;
  }

  notification[type]({
    message: title,
    description
  });
};

export class Alerts extends Component {
  static propTypes = {
    error: PropTypes.object.isRequired,
    message: PropTypes.object.isRequired
  };

  componentDidUpdate(prevProps) {
    const { error, message } = this.props;
    if (error !== prevProps.error) {
      if (error.msg.message)
        openNotificationWithIcon(
          'error',
          error.status,
          error.msg.message.toString()
        );
    }

    if (message !== prevProps.message) {
      if (message.passwordNotMatch)
        openNotificationWithIcon(
          'error',
          message.passwordNotMatch,
          message.passwordNotMatch
        );
      if (message.updateUserSuccess)
        openNotificationWithIcon(
          'success',
          message.updateUserSuccess,
          message.updateUserSuccess
        );
    }
  }

  render() {
    return <Fragment />;
  }
}

const mapStateToProps = state => ({
  error: state.errors,
  message: state.messages
});

export default connect(mapStateToProps)(Alerts);
