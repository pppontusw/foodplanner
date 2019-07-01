import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Icon, Form, Input, Popconfirm, Table, Card } from 'antd';
import {
  newMeal,
  deleteMeal,
  getMealsByList,
  putMeals
} from '../../actions/meals';
import { DndProvider } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
import update from 'immutability-helper';
import { DragableBodyRow } from '../Helpers/BodyRow';

// todo this could be a selector (reselect)
const mealsMap = (list, meals) => {
  let newMeals = [];
  const oldMeals = list ? list.meals : [];

  if (list) {
    newMeals = oldMeals.map((meal_id, index) => {
      const meal = meals.byId[meal_id];
      if (meal) {
        return {
          name: meal.name,
          id: meal_id,
          key: index
        };
      } else {
        return {
          key: index
        };
      }
    });
  }
  return newMeals;
};

class MealSettings extends Component {
  state = {
    new_meal: '',
    data: []
  };

  components = {
    body: {
      row: DragableBodyRow
    }
  };

  columns = [
    {
      title: 'Meals',
      dataIndex: 'name',
      key: 'key'
    },
    {
      title: '',
      key: 'delete',
      align: 'right',
      render: (text, record) => (
        <Popconfirm
          title="Are you sure you want to delete this meal?"
          onConfirm={() => this.deleteMeal(record.id)}
          okText="Yes"
          cancelText="No"
        >
          <Icon
            type="close-circle"
            // theme="twoTone"
            // twoToneColor="#d63737"
            style={{ fontSize: '16px' }}
          />
        </Popconfirm>
      )
    }
  ];

  moveRow = (dragIndex, hoverIndex) => {
    const { meals } = this.props;
    const dragRow = meals[dragIndex];
    const newData = update(this.props.meals, {
      $splice: [[dragIndex, 1], [hoverIndex, 0, dragRow]]
    });

    this.props.putMeals(this.props.listId, newData);
  };

  onSubmit = e => {
    e.preventDefault();
    const new_meal_name = this.state.new_meal;
    this.props.newMeal(this.props.listId, new_meal_name);
    this.setState({ new_meal: '' });
  };

  onChange = e => this.setState({ [e.target.name]: e.target.value });

  deleteMeal = id => {
    this.props.deleteMeal(this.props.listId, id);
  };

  componentDidMount() {
    this.props.getMealsByList(this.props.listId);
  }

  render() {
    if (this.props.loading) {
      return <Card loading={this.props.loading} />;
    }
    return (
      <div>
        <DndProvider backend={HTML5Backend}>
          <Table
            columns={this.columns}
            dataSource={this.props.meals ? this.props.meals : []}
            components={this.components}
            pagination={false}
            onRow={(record, index) => ({
              index,
              moveRow: this.moveRow
            })}
          />
        </DndProvider>
        <br />
        {this.props.list ? (
          <Form layout="vertical" onSubmit={this.onSubmit}>
            <Form.Item>
              <Input
                placeholder="Add a new meal"
                name="new_meal"
                onChange={this.onChange}
                value={this.state.new_meal}
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
    const loading = state.meals.loading;
    const mappedMeals = mealsMap(list, state.meals);

    return {
      list: list,
      meals: mappedMeals,
      username: state.auth.user.user,
      loading
    };
  },
  { newMeal, deleteMeal, getMealsByList, putMeals }
)(MealSettings);
