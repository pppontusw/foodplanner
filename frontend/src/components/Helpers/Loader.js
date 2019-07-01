import React, { Component } from 'react';
import { Spin } from 'antd';

class Loader extends Component {
  render() {
    return (
      <div style={{ textAlign: 'center', marginTop: '10px' }}>
        <Spin size="large" />
      </div>
    );
  }
}

export default Loader;
