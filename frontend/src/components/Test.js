import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getData, getList, getDaysAndEntries } from '../actions';
import { Link } from 'react-router-dom';
import Day from './Day';
import Loader from './Loader';

export class List extends Component {
  componentDidMount() {
    this.props.getList(this.props.match.params.id);
    this.props.getDaysAndEntries(this.props.match.params.id);
  }

  render() {
    const { loading } = this.props;

    if (loading) {
      return <Loader />;
    }

    return (
      <div className="row">
        <div className="col-md-12">
          <h2>{this.props.list ? this.props.list.name : null}</h2>
          <Link to={`/list_settings/${this.props.list.id}`}>
            <button className="btn btn-info float-right">Settings</button>
          </Link>
          <br />
          <br />
          <table className="table">
            {this.props.list.days.map((day, day_index) => (
              <Day key={day} listId={this.props.list.id} dayId={day} />
            ))}
          </table>
        </div>
      </div>
    );
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
  { getData, getDaysAndEntries, getList }
)(List);
