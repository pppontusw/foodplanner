import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { getList } from '../../actions/lists';
import { getSharesByList } from '../../actions/shares';
import { Card, Tabs, Icon, Button } from 'antd';
import ShareSettings from './ShareSettings';
import ViewSettings from './ViewSettings';
import MealSettings from './MealSettings';

export class ListSettings extends Component {
  componentDidMount() {
    const { id } = this.props.match.params;
    this.props.getList(id);
    this.props.getSharesByList(id);
  }

  render() {
    const { TabPane } = Tabs;
    const list_id = this.props.match.params.id;

    return (
      <div>
        <Link to={`/list/${list_id}`}>
          <Button style={{ margin: '10px 10px 0px 10px' }}>
            <Icon type="left-circle" /> Back to list
          </Button>
        </Link>
        <Card
          style={{ margin: '10px 10px', maxWidth: '700px', minHeight: '500px' }}
        >
          <Tabs tabPosition="right">
            <TabPane forceRender={true} tab="View Settings" key="1">
              <ViewSettings list_id={list_id} />
            </TabPane>
            <TabPane forceRender={true} tab="Meals" key="2">
              <MealSettings list_id={list_id} />
            </TabPane>
            <TabPane forceRender={true} tab="Shares" key="3">
              <ShareSettings list_id={list_id} />
            </TabPane>
          </Tabs>
        </Card>
      </div>
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
  { getList, getSharesByList }
)(ListSettings);
