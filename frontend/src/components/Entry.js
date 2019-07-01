import React, { Component } from 'react';
import { connect } from 'react-redux';
import { updateEntry } from '../actions/entries';
import { Row, Button, AutoComplete, Input } from 'antd';

const foodsMap = (list, foods) => {
  let newFoods = [];
  const oldFoods = list ? list.foods : [];

  if (list) {
    newFoods = oldFoods.map((food_id, index) => {
      const food = foods.byId[food_id];
      if (food) {
        return food.name;
      } else {
        return null;
      }
    });
  }
  return newFoods;
};

class NewEntry extends Component {
  state = {
    value: '',
    orig_value: '',
    editing: false,
    hovering: false,
    dataSource: ['test', 'Pest']
  };

  constructor(props) {
    super(props);
    this.myRef = React.createRef();
  }

  componentDidMount() {
    let value;
    if (this.props.entry) {
      value = this.props.entry.value ? this.props.entry.value : 'Empty';
    } else {
      value = 'Empty';
    }
    this.setState({ value, orig_value: value });
  }

  saveEntry = () => {
    this.setState({ editing: false });
    const newValue = this.state.value;
    this.props.updateEntry(this.props.entry.id, newValue);
    this.setState({ orig_value: newValue });
  };

  onSelect = (value, option) => {
    this.setState({ value: value }, () => {
      this.saveEntry();
    });
  };

  revertEntry = () => {
    this.setState({ value: this.state.orig_value });
    this.setState({ editing: false });
  };

  startEdit = () => {
    this.setState({ editing: true }, () => {
      this.myRef.current.focus();
    });
  };

  toggleHover = () => {
    this.setState({ hovering: !this.state.hovering });
  };

  onChange = e => {
    this.setState({ value: e });
  };

  render() {
    const { entry } = this.props;

    const notEditing = (
      <div style={{ float: 'right' }}>
        <p>
          {this.state.value}
          <Button
            size="small"
            onClick={this.startEdit}
            icon="edit"
            style={{ marginLeft: '10px', float: 'right' }}
          />
        </p>
      </div>
    );

    const Editing = (
      <div style={{ float: 'right' }}>
        <AutoComplete
          style={{ width: 200 }}
          dataSource={this.props.foods}
          placeholder="Type food here"
          defaultValue={this.state.value !== 'Empty' ? this.state.value : ''}
          onChange={this.onChange}
          onSelect={this.onSelect}
          ref={this.myRef}
          filterOption={(inputValue, option) =>
            option.props.children
              .toUpperCase()
              .indexOf(inputValue.toUpperCase()) !== -1
          }
        >
          <Input
            onPressEnter={this.saveEntry}
            ref={input => (this.testInput = input)}
          />
        </AutoComplete>
        <Button
          style={{ marginLeft: '2px' }}
          icon="check-circle"
          // size="small"
          type="primary"
          onClick={this.saveEntry}
        />
        <Button
          style={{ marginLeft: '2px' }}
          icon="close-circle"
          // size="small"
          type="danger"
          onClick={this.revertEntry}
        />
      </div>
    );

    if (!entry) {
      return null;
    }
    return (
      <Row style={{ marginTop: '10px' }}>
        <div style={{ float: 'left' }}>
          <p>{entry.key}</p>
        </div>
        {this.state.editing ? Editing : notEditing}
      </Row>
    );
  }
}

export default connect(
  (state, props) => {
    const list = state.lists.byId[props.listId];
    const entryId = props.entryId;
    return {
      entry: state.entries.byId[entryId],
      foods: foodsMap(list, state.foods)
    };
  },
  { updateEntry }
)(NewEntry);
