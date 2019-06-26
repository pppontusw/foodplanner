import React, { Component } from 'react';
import EasyEdit from 'react-easy-edit';
import { connect } from 'react-redux';
import { updateEntry } from '../actions/entries';
import { Row } from 'antd';

class Entry extends Component {
  saveEntry(entry_id, text) {
    this.props.updateEntry(entry_id, text);
  }

  render() {
    const { entry } = this.props;
    if (!entry) {
      return null;
    }
    return (
      <Row>
        <div style={{ float: 'left' }}>
          <p>{entry.key}</p>
        </div>
        <div style={{ float: 'right' }}>
          <EasyEdit
            labelClassName={`label_${entry.id}`}
            value={entry.value}
            type="text"
            saveButtonStyle="btn btn-sm btn-primary ml-2"
            saveButtonLabel="✓"
            cancelButtonStyle="btn btn-sm btn-secondary ml-1"
            cancelButtonLabel="✕"
            placeholder="Empty"
            onSave={this.saveEntry.bind(this, entry.id)}
          />
        </div>
      </Row>
    );
  }
}

export default connect(
  (state, props) => {
    const entryId = props.entryId;
    return {
      entry: state.entries.byId[entryId]
    };
  },
  { updateEntry }
)(Entry);
