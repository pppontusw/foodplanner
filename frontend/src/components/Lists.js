import React, { Component, Fragment } from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { getLists, createList } from '../actions/lists';
import { getDays } from '../actions/days';
import { getEntries } from '../actions/entries';
import _ from 'lodash';
import Day from './Day';
import Loader from './Helpers/Loader';
import { Modal, Form, Input, Card, Row, Col, Button } from 'antd';

const mapStateToProps = state => {
  const loading =
    state.lists.firstFullLoad ||
    state.days.firstFullLoad ||
    state.entries.firstFullLoad;

  return {
    lists: _.values(state.lists.byId),
    firstFullLoad: loading,
    listsLoading: state.lists.loading
  };
};

class Lists extends Component {
  state = {
    newListModalVisible: false,
    listname: ''
  };

  componentDidMount() {
    this.props.getLists(0, 2);
    this.props.getDays(0, 2);
    this.props.getEntries(0, 2);
  }

  onSubmit = e => {
    e.preventDefault();
    this.props.createList(this.state.listname);
    this.setState({ listname: '' });
    this.hideModal();
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  createListClick = () => {
    this.setState({ newListModalVisible: true });
  };

  hideModal = () => {
    this.setState({ newListModalVisible: false });
  };

  render() {
    if (this.props.listsLoading) {
      return <Loader />;
    }
    return (
      <Fragment>
        <Modal
          visible={this.state.newListModalVisible}
          onOk={this.onSubmit}
          onCancel={this.hideModal}
        >
          <h2 className="modal-title" id="exampleModalLabel">
            New List
          </h2>
          <Form onSubmit={this.onSubmit}>
            <Input
              type="text"
              className="form-control"
              id="listname"
              name="listname"
              placeholder="List name"
              onChange={this.onChange}
              value={this.state.listname}
            />
          </Form>
        </Modal>
        <Row>
          {this.props.lists.map(list => (
            <Col key={list.id} xs={24} sm={24} md={12}>
              <Card
                loading={this.props.firstFullLoad}
                title={list.name}
                style={{ margin: '10px 10px' }}
                extra={<Link to={`/list/${list.id}`}>Go to list</Link>}
              >
                {list.days.map((day, day_index) => (
                  <Day key={day} listId={list.id} dayId={day} />
                ))}
              </Card>
            </Col>
          ))}
        </Row>
        <Row>
          <Button
            style={{ margin: '10px' }}
            type="primary"
            onClick={this.createListClick.bind(this)}
          >
            Create new list
          </Button>
        </Row>
      </Fragment>
    );
  }
}

export default connect(
  mapStateToProps,
  { getLists, getDays, getEntries, createList }
)(Lists);
