import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import { getListSettings } from '../../actions/lists';

export class ListSettings extends Component {
  componentDidMount() {
    // this.props.getList(this.props.match.params.id);
  }

  render() {
    return <Fragment />;
  }
}

export default connect(
  (state, props) => {
    const list = state.lists.byId[props.match.params.id];
    const listLoading =
      state.lists.loading || state.days.loading || state.entries.loading;

    return {
      list,
      loading: listLoading
    };
  },
  { getListSettings }
)(ListSettings);
