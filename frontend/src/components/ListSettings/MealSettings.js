import React, { Component } from 'react';
import { connect } from 'react-redux';

export class MealSettings extends Component {
  render() {
    return <div>{this.props.list ? this.props.list.name : null}</div>;
  }
}

export default connect((state, props) => {
  const list = state.lists.byId[props.list_id];
  const loading = state.lists.loading;

  return {
    list: list,
    loading
  };
})(MealSettings);
