import React, { Component, Fragment } from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { getList, renameList } from '../../actions/lists';
import { getSharesByList } from '../../actions/shares';
import { Card, Tabs, Icon, Button, Input, Spin } from 'antd';
import ShareSettings from './ShareSettings';
import ViewSettings from './ViewSettings';
import MealSettings from './MealSettings';
import FoodSettings from './FoodSettings';
import CategorySettings from './CategorySettings';

class ListSettings extends Component {
  state = {
    listTitle: 'Test',
    editingListTitle: false
  };

  componentDidMount() {
    const { id } = this.props.match.params;
    this.props.getList(id);
    this.props.getSharesByList(id);
  }

  startEdit = () => {
    this.setState({ editingListTitle: true, listTitle: this.props.list.name });
  };

  saveEntry = () => {
    this.setState({ editingListTitle: false });
    const newValue = this.state.listTitle;
    this.props.renameList(this.props.match.params.id, newValue);
  };

  cancelEditing = () => {
    this.setState({ editingListTitle: false });
  };

  onChange = e => {
    this.setState({ [e.target.name]: e.target.value });
  };

  render() {
    const { TabPane } = Tabs;
    const listId = this.props.match.params.id;

    const cardTitleNotEditing = this.props.updatingTitle ? (
      <Spin />
    ) : (
      <Fragment>
        {this.props.list ? this.props.list.name : null}
        <Button
          size="small"
          onClick={this.startEdit}
          icon="edit"
          style={{ marginLeft: '16px' }}
        />
      </Fragment>
    );

    const cardTitleEditing = (
      <Fragment>
        <Input
          style={{ width: 200 }}
          onChange={this.onChange}
          onPressEnter={this.saveEntry}
          name="listTitle"
          value={this.state.listTitle}
        />
        <Button
          style={{ marginLeft: '5px' }}
          icon="check-circle"
          // size="small"
          type="primary"
          onClick={this.saveEntry}
        />
        <Button
          style={{ marginLeft: '5px' }}
          icon="close-circle"
          // size="small"
          type="danger"
          onClick={this.cancelEditing}
        />
      </Fragment>
    );

    return (
      <div>
        <Link to={`/list/${listId}`}>
          <Button style={{ margin: '10px 10px 0px 10px' }}>
            <Icon type="left-circle" /> Back to list
          </Button>
        </Link>
        <Card
          style={{
            margin: '10px 10px',
            maxWidth: '800px',
            minHeight: '500px'
          }}
          title={
            this.state.editingListTitle ? cardTitleEditing : cardTitleNotEditing
          }
        >
          <Tabs tabPosition="right">
            <TabPane tab="View Settings" key="1">
              <ViewSettings listId={listId} />
            </TabPane>
            <TabPane tab="Meals" key="2">
              <MealSettings listId={listId} />
            </TabPane>
            <TabPane tab="Foods" key="3">
              <FoodSettings listId={listId} />
            </TabPane>
            <TabPane tab="Categories" key="4">
              <CategorySettings listId={listId} />
            </TabPane>
            <TabPane tab="Shares" key="5">
              <ShareSettings listId={listId} />
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
      loading: state.lists.loading,
      updatingTitle: state.lists.updatingTitle
    };
  },
  { getList, getSharesByList, renameList }
)(ListSettings);
