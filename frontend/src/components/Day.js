import React, { Component } from 'react';
import moment from 'moment';
import { connect } from 'react-redux';
import Entry from './Entry';

class Day extends Component {
  render() {
    const { day } = this.props;
    if (!day) {
      return null;
    }
    return (
      <React.Fragment key={day.id}>
        <thead className="thead-light">
          <tr className="active d-flex">
            <th className="col-sm-4 col-3 col-md-6">
              {moment.utc(day.day).format('dddd')}
            </th>
            <th className="col-sm-8 col-9 col-md-6">
              {moment.utc(day.day).format('MMM Do')}
            </th>
          </tr>
        </thead>
        {day.entries.map((entry, entry_index) => (
          <Entry key={entry} entryId={entry} />
        ))}
      </React.Fragment>
    );
  }
}

export default connect(
  (state, props) => {
    const dayId = props.dayId;
    return {
      day: state.days.byId[dayId]
    };
  },
  null
)(Day);
