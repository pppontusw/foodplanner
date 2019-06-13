import React, { Component, Fragment } from 'react';
// import { Link, Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import { getData, createList } from '../actions';
import { NewList } from './NewList';
import $ from 'jquery';
import 'bootstrap';
import _ from 'lodash';
import Day from './Day';
import Loader from './Loader';

const mapStateToProps = state => {
  const loading =
    state.lists.firstFullLoad ||
    state.days.firstFullLoad ||
    state.entries.firstFullLoad;
  return {
    lists: _.values(state.lists.byId),
    firstFullLoad: loading
  };
};

export class Lists extends Component {
  componentDidMount() {
    this.props.getData();
  }

  createListClick = () => {
    // this.props.openNewListModal()
    $('#exampleModal').modal('show');
  };

  render() {
    // if (this.props.lists.length === 1) {
    //   return <Redirect to={`list/${this.props.lists[0].id}`} />
    // }
    if (this.props.firstFullLoad) {
      return <Loader />;
    }
    return (
      <Fragment>
        <NewList {...this.props} />
        <div className="row">
          {this.props.lists.map(list => (
            <div
              key={list.id}
              className={this.props.lists.length > 1 ? 'col-md-6' : 'col-md-12'}
            >
              <h1 className="text-center">
                <a href={`#/list/${list.id}`}>{list.name}</a>
              </h1>
              <table className="table">
                {list.frontpagedays.map((day, day_index) => (
                  <Day key={day} listId={list.id} dayId={day} />
                ))}
              </table>
            </div>
          ))}
        </div>
        <div className="row">
          <button
            className="btn btn-primary"
            onClick={this.createListClick.bind(this)}
          >
            Create new list
          </button>
        </div>
        <br />
      </Fragment>
    );
  }
}

export default connect(
  mapStateToProps,
  { getData, createList }
)(Lists);
