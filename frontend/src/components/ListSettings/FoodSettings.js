import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';

import {
  Icon,
  Form,
  Input,
  Popconfirm,
  Table,
  Divider,
  Tag,
  Card,
  Modal,
  Select,
  Button
} from 'antd';
import {
  getFoodsByList,
  newFood,
  deleteFood,
  putFood
} from '../../actions/foods';
import { getCategoriesByList } from '../../actions/categories';

const { Option } = Select;

// todo this could be a selector (reselect)
const foodsMap = (list, foods, categories) => {
  let newFoods = [];
  let mapping_categories = [];
  const oldFoods = list ? list.foods : [];

  if (list) {
    newFoods = oldFoods.map((food_id, index) => {
      const food = foods.byId[food_id];
      if (food) {
        mapping_categories = food.categories.map((category_id, index) => {
          const category = categories.byId[category_id];
          if (category) {
            return {
              name: category.name,
              color: 'blue',
              id: category.id,
              key: index
            };
          } else {
            return {
              key: index
            };
          }
        });
        return {
          name: food.name,
          id: food_id,
          key: index,
          categories: mapping_categories
        };
      } else {
        return {
          key: index
        };
      }
    });
  }
  return newFoods;
};

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

class FoodSettings extends Component {
  state = {
    new_food: '',
    modalVisible: false,
    modalTitle: '',
    modalFoodName: '',
    modalFoodCategories: [],
    editingFoodName: false,
    modalFoodId: ''
  };

  columns = [
    {
      title: 'Foods',
      dataIndex: 'name',
      key: 'key'
    },
    {
      title: 'Categories',
      key: 'categories',
      dataIndex: 'key',
      render: (index, record) =>
        record.categories ? (
          <span>
            {record.categories.map((category, index) => {
              if (category.name) {
                return (
                  <Tag color={category.color} key={category.key}>
                    {category.name}
                  </Tag>
                );
              } else {
                return <Fragment key={category.key} />;
              }
            })}
          </span>
        ) : null
    },
    {
      title: 'Action',
      key: 'delete',
      align: 'right',
      render: (text, record) => (
        <Fragment>
          <a href="javascript:;" onClick={() => this.openModal(record)}>
            Edit
          </a>
          <Divider type="vertical" />
          <Popconfirm
            title="Are you sure you want to delete this food?"
            onConfirm={() => this.deleteFood(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <a href="javascript:;">Delete</a>
          </Popconfirm>
        </Fragment>
      )
    }
  ];

  openModal = record => {
    this.setState({
      modalVisible: true,
      modalFoodName: record.name,
      modalFoodId: record.id,
      modalFoodCategories: record.categories.map(el => {
        return el.name;
      })
    });
  };

  handleModalOk = () => {
    const newData = {
      name: this.state.modalFoodName,
      id: this.state.modalFoodId,
      categories: this.state.modalFoodCategories
    };
    this.props.putFood(this.props.listId, newData);
    this.clearFoodModalFromState();
  };

  handleModalCancel = () => {
    this.clearFoodModalFromState();
  };

  handleModalCategoryChange = e => {
    this.setState({
      modalFoodCategories: e
    });
  };

  clearFoodModalFromState = () => {
    this.setState({
      modalVisible: false,
      modalTitle: '',
      modalFoodName: '',
      modalFoodCategories: [],
      modalFoodId: '',
      editingFoodName: false
    });
  };

  saveFoodName = () => {
    this.setState({ editingFoodName: false });
  };

  startEditingFoodName = () => {
    this.setState({
      editingFoodName: true
    });
  };

  cancelEditingFoodName = () => {
    this.setState({ editingFoodName: false });
  };

  onSubmit = e => {
    e.preventDefault();
    const new_food_name = this.state.new_food;
    this.props.newFood(this.props.listId, new_food_name);
    this.setState({ new_food: '' });
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  deleteFood = id => {
    this.props.deleteFood(this.props.listId, id);
  };

  componentDidMount() {
    this.props.getFoodsByList(this.props.listId);
    this.props.getCategoriesByList(this.props.listId);
  }

  render() {
    if (this.props.loading) {
      return <Card loading={this.props.loading} />;
    }

    const foodNameNotEditing = (
      <Fragment>
        {this.state.modalFoodName}
        <Button
          size="small"
          onClick={this.startEditingFoodName}
          icon="edit"
          style={{ marginLeft: '16px' }}
        />
      </Fragment>
    );

    const foodNameEditing = (
      <Fragment>
        <Input
          style={{ width: 200 }}
          onChange={this.onChange}
          onPressEnter={this.modalFoodName}
          name="modalFoodName"
          value={this.state.modalFoodName}
        />
        <Button
          style={{ marginLeft: '5px', color: 'blue' }}
          icon="check-circle"
          type="primary"
          // size="small"
          onClick={this.saveFoodName}
        />
        <Button
          style={{ marginLeft: '5px', color: 'red' }}
          icon="close-circle"
          type="danger"
          // size="small"
          onClick={this.cancelEditingFoodName}
        />
      </Fragment>
    );

    const editModal = (
      <Modal
        title={this.state.modalFoodName}
        // bodyStyle={{ minHeight: '400px' }}
        visible={this.state.modalVisible}
        onOk={this.handleModalOk}
        onCancel={this.handleModalCancel}
        confirmLoading={this.props.updatingFood}
        destroyOnClose
      >
        <Form>
          <Form.Item label="Food Name">
            {this.state.editingFoodName ? foodNameEditing : foodNameNotEditing}
          </Form.Item>
          <Form.Item style={{ paddingBottom: '100px' }} label="Categories">
            <Select
              mode="tags"
              placeholder="Type to add categories.."
              defaultValue={
                this.state.modalFoodCategories
                  ? this.state.modalFoodCategories.map(el => {
                      return el;
                    })
                  : []
              }
              onChange={this.handleModalCategoryChange}
            >
              {this.props.categories
                ? this.props.categories.map((el, idx) => {
                    return (
                      <Option key={idx} title={el.name} value={el.name}>
                        {el.name}
                      </Option>
                    );
                  })
                : null}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    );

    return (
      <div>
        {editModal}
        <Table
          columns={this.columns}
          dataSource={this.props.foods ? this.props.foods : []}
          pagination={false}
        />
        <br />
        {this.props.list ? (
          <Form layout="vertical" onSubmit={this.onSubmit}>
            <Form.Item>
              <Input
                placeholder="Add a new food"
                name="new_food"
                onChange={this.onChange}
                value={this.state.new_food}
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
    const loading = state.foods.loading || state.categories.loading;
    const mappedFoods = foodsMap(list, state.foods, state.categories);
    const mappedCategories = categoriesMap(list, state.categories);

    return {
      list: list,
      foods: mappedFoods,
      categories: mappedCategories,
      username: state.auth.user.user,
      loading,
      updatingFood: state.foods.updatingFood
    };
  },
  { getFoodsByList, getCategoriesByList, newFood, deleteFood, putFood }
)(FoodSettings);
