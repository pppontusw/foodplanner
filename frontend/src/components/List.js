import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getList } from '../actions/lists';
import { getDaysByList } from '../actions/days';
import { getEntriesByList } from '../actions/entries';
import { Link } from 'react-router-dom';
import Day from './Day';
import { Card, Button } from 'antd';

export class List extends Component {
  componentDidMount() {
    this.props.getList(this.props.match.params.id, 0, 15);
    this.props.getDaysByList(this.props.match.params.id);
    this.props.getEntriesByList(this.props.match.params.id);
  }

  render() {
    const { loading, list } = this.props;

    // if (loading) {
    //   return <Loader />;
    // }

    return (
      <div className="row">
        <Card
          loading={loading}
          title={list ? list.name : null}
          style={{ margin: '10px 10px', maxWidth: '600px' }}
        >
          {list ? (
            <Link to={`/list_settings/${list.id}`}>
              <Button style={{ float: 'right' }}>Settings</Button>
            </Link>
          ) : null}
          <br />
          <br />
          {list
            ? list.days.map((day, day_index) => (
                <Day key={day} listId={list.id} dayId={day} />
              ))
            : null}
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
  { getDaysByList, getEntriesByList, getList }
)(List);
