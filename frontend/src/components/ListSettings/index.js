import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import { getListSettings } from '../../actions';

const mapStateToProps = state => {
  return {
    list: state.list.list
  };
};

export class ListSettings extends Component {
  componentDidMount() {
    // this.props.getList(this.props.match.params.id);
  }

  render() {
    return <Fragment />;
  }
}

export default connect(
  mapStateToProps,
  { getListSettings }
)(ListSettings);
