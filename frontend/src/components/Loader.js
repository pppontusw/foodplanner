import React, { Component } from 'react';
import { css } from '@emotion/core';
import { ClipLoader } from 'react-spinners';

const override = css`
  display: block !important;
  margin: 0 auto !important;
  border-color: red;
`;

class Loader extends Component {
  render() {
    return (
      <div>
        <ClipLoader
          css={override}
          sizeUnit={'px'}
          size={150}
          color={'#36D7B7'}
          loading={this.props.firstFullLoad}
        />
      </div>
    );
  }
}

export default Loader;
