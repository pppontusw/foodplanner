import React, { Component } from 'react';
import EasyEdit from 'react-easy-edit';
import { connect } from 'react-redux';
import { updateEntry } from '../actions';

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
      <tbody key={entry.id}>
        <tr className="d-flex">
          <td className="col-sm-4 col-3 col-md-6">{entry.key}</td>
          <td className="col-sm-8 col-9 col-md-6">
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
          </td>
        </tr>
      </tbody>
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
