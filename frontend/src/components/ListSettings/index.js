import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import { getList } from '../../actions/lists';
import { Card, Tabs } from 'antd';
import ShareSettings from './ShareSettings';
import ViewSettings from './ViewSettings';
import MealSettings from './MealSettings';
import Loader from '../Loader';

export class ListSettings extends Component {
  componentDidMount() {
    this.props.getList(this.props.match.params.id);
  }

  render() {
    const { TabPane } = Tabs;
    const list_id = this.props.match.params.id;

    if (this.props.loading) {
      return <Loader />;
    }

    return (
      <Card style={{ margin: '10px 10px', maxWidth: '700px' }}>
        <Tabs tabPosition="right">
          <TabPane tab="View Settings" key="1">
            <ViewSettings list_id={list_id} />
          </TabPane>
          <TabPane tab="Meals" key="2">
            <MealSettings list_id={list_id} />
          </TabPane>
          <TabPane tab="Shares" key="3">
            <ShareSettings list_id={list_id} />
          </TabPane>
        </Tabs>
      </Card>
    );
  }
}

export default connect(
  (state, props) => {
    const list = state.lists.byId[props.match.params.id];

    return {
      list,
      loading: state.lists.loading
    };
  },
  { getList }
)(ListSettings);
