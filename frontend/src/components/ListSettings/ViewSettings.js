import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Form, Select, Button, Icon } from 'antd';
import { putListSettings } from '../../actions/lists';

const { Option } = Select;

export class ViewSettings extends Component {
  onSubmit = e => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        const { days_to_display, start_day_of_week } = values;
        const { list_id } = this.props;
        this.props.putListSettings(list_id, days_to_display, start_day_of_week);
      }
    });
  };

  render() {
    const { days_to_display, start_day_of_week } = this.props.settings || {};
    const { getFieldDecorator } = this.props.form;
    return (
      <Form onSubmit={this.onSubmit}>
        <Form.Item label="Number of days to display" hasFeedback>
          {getFieldDecorator('days_to_display', {
            rules: [{ required: true }],
            initialValue: days_to_display
          })(
            <Select>
              {[...Array(21)].map((x, i) => (
                <Option value={i + 3} key={i + 3}>
                  {i + 3}
                </Option>
              ))}
            </Select>
          )}
        </Form.Item>
        <Form.Item label="Start day of the week" hasFeedback>
          {getFieldDecorator('start_day_of_week', {
            rules: [{ required: true }],
            initialValue: start_day_of_week
          })(
            <Select>
              <Option value="Today">Today</Option>
              <Option value="Monday">Monday</Option>
              <Option value="Tuesday">Tuesday</Option>
              <Option value="Wednesday">Wednesday</Option>
              <Option value="Thursday">Thursday</Option>
              <Option value="Friday">Friday</Option>
              <Option value="Saturday">Saturday</Option>
              <Option value="Sunday">Sunday</Option>
            </Select>
          )}
        </Form.Item>
        <Form.Item>
          <Button htmlType="submit" type="primary">
            <Icon type="save" /> Save
          </Button>
        </Form.Item>
      </Form>
    );
  }
}

const WrappedViewSettingsForm = Form.create({ name: 'view_settings' })(
  ViewSettings
);

export default connect(
  (state, props) => {
    const list = state.lists.byId[props.list_id];

    return {
      settings: list.settings
    };
  },
  { putListSettings }
)(WrappedViewSettingsForm);
