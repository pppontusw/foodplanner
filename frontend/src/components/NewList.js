import React, { Component, Fragment } from "react";
import { Link, Redirect } from "react-router-dom";
import { connect } from "react-redux";
import { createList } from "../actions";
import { createMessage } from "../actions/messages";
import $ from 'jquery';
import 'bootstrap';

export class NewList extends Component {
  state = {
    listname: ""
  };

  onSubmit = e => {
    e.preventDefault();
    this.props.createList(this.state.listname)
    this.setState({listname: ""})
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  hideModal = () => {
    $('#exampleModal').modal('hide');
  }

  render() {
    const { listname } = this.state;
    return (
      <Fragment>
      <div className="modal fade" id="exampleModal" tabIndex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="exampleModalLabel">New List</h5>
              <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={this.onSubmit}>
                <div className="form-group">
                  <label>Listname</label>
                  <input
                    type="text"
                    className="form-control"
                    id="listname"
                    name="listname"
                    onChange={this.onChange}
                    value={listname}
                  />
                </div>
                <div className="form-group modal-footer">
                    <button type="submit" onClick={this.hideModal.bind(this)} className="btn btn-primary">
                    Save
                    </button>
                </div>
              </form>
              </div>
            </div>
          </div>
        </div>
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
  isAuthenticated: state.auth.isAuthenticated
});

export default connect(
  mapStateToProps,
  { createList, createMessage }
)(NewList);