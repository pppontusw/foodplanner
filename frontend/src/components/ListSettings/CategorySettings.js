import React, { Component } from 'react';
import { connect } from 'react-redux';

import { List, Icon, Form, Input, Popconfirm, Card } from 'antd';
import {
  newCategory,
  deleteCategory,
  getCategoriesByList
} from '../../actions/categories';

// todo this could be a selector (reselect)
const categoriesMap = (list, categories) => {
  let newCategories = [];
  const oldCategories = list ? list.categories : [];

  if (list) {
    newCategories = oldCategories.map((category_id, index) => {
      const category = categories.byId[category_id];
      if (category) {
        return {
          name: category.name,
          id: category_id,
          key: index
        };
      } else {
        return {
          key: index
        };
      }
    });
  }
  return newCategories;
};

class CategorySettings extends Component {
  state = {
    newCategory: ''
  };

  onSubmit = e => {
    e.preventDefault();
    const { newCategory } = this.state;
    this.props.newCategory(this.props.listId, newCategory);
    this.setState({ newCategory: '' });
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  deleteCategory = id => {
    this.props.deleteCategory(this.props.listId, id);
  };

  componentDidMount() {
    this.props.getCategoriesByList(this.props.listId);
  }

  render() {
    if (this.props.loading) {
      return <Card loading={this.props.loading} />;
    }
    return (
      <div>
        <List
          header={<strong>Categories</strong>}
          bordered
          dataSource={this.props.categories}
          renderItem={item => (
            <List.Item
              key={item.id}
              actions={[
                <Popconfirm
                  title="Are you sure you want to delete this category?"
                  onConfirm={() => this.deleteCategory(item.id)}
                  okText="Yes"
                  cancelText="No"
                >
                  <Icon
                    type="delete"
                    // theme="twoTone"
                    // twoToneColor="#d63737"
                    style={{ fontSize: '16px' }}
                  />
                </Popconfirm>
              ]}
            >
              {item.name}
            </List.Item>
          )}
        />
        <br />
        {this.props.list ? (
          <Form layout="vertical" onSubmit={this.onSubmit}>
            <Form.Item>
              <Input
                placeholder="Add category"
                name="newCategory"
                onChange={this.onChange}
                value={this.state.newCategory}
                addonAfter={<Icon type="plus" onClick={this.onSubmit} />}
              />
            </Form.Item>
          </Form>
        ) : null}
      </div>
    );
  }
}

export default connect(
  (state, props) => {
    const list = state.lists.byId[props.listId];
    const loading = state.categories.loading;

    return {
      list: list,
      categories: categoriesMap(list, state.categories),
      username: state.auth.user.user,
      loading
    };
  },
  { newCategory, deleteCategory, getCategoriesByList }
)(CategorySettings);
