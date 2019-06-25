import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getListThenDaysThenEntries } from '../actions/lists';
import { Link } from 'react-router-dom';
import Day from './Day';
import { Card, Button, Icon } from 'antd';

export class List extends Component {
  state = {
    page: 0,
    visitedPages: [0]
  };

  componentDidMount() {
    this.props.getListThenDaysThenEntries(
      this.props.match.params.id,
      this.state.page
    );
  }

  refreshData = suppressLoading => {
    this.props.getListThenDaysThenEntries(
      this.props.match.params.id,
      this.state.page,
      false,
      suppressLoading
    );
  };

  pageBack = () => {
    let suppressLoading = true;
    const { page, visitedPages } = this.state;
    const newPage = page - 1;
    if (!visitedPages.includes(newPage)) {
      visitedPages.push(newPage);
      suppressLoading = false;
    }
    this.setState({ page: newPage, visitedPages: visitedPages }, () => {
      this.refreshData(suppressLoading);
    });
  };

  pageForward = () => {
    let suppressLoading = true;
    const { page, visitedPages } = this.state;
    const newPage = page + 1;
    if (!visitedPages.includes(newPage)) {
      visitedPages.push(newPage);
      suppressLoading = false;
    }
    this.setState({ page: newPage, visitedPages: visitedPages }, () => {
      this.refreshData(suppressLoading);
    });
  };

  render() {
    const { loading, list } = this.props;

    // if (loading) {
    //   return <Loader />;
    // }

    return (
      <div>
        <Card
          loading={loading}
          title={list ? list.name : null}
          style={{ margin: '10px 10px', maxWidth: '600px' }}
          extra={
            list ? (
              <Link to={`/list_settings/${list.id}`}>
                <Button
                // style={{ float: 'right', marginTop: '10px' }}
                >
                  <Icon type="setting" />
                </Button>
              </Link>
            ) : null
          }
        >
          {list
            ? list.days.map((day, day_index) => (
                <Day key={day} listId={list.id} dayId={day} />
              ))
            : null}

          <div style={{ display: 'flex' }}>
            <Button
              style={{ marginRight: 'auto', marginTop: '20px' }}
              onClick={this.pageBack}
            >
              <Icon type="left-circle" />
            </Button>
            <Button
              style={{ marginLeft: 'auto', marginTop: '20px' }}
              onClick={this.pageForward}
            >
              <Icon type="right-circle" />
            </Button>
          </div>
        </Card>
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
  { getListThenDaysThenEntries }
)(List);
