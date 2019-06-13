import React, { Component } from 'react'
import { connect } from 'react-redux';
import { getList, updateEntry } from '../actions'
import { Link } from 'react-router-dom'
import moment from 'moment';
import EasyEdit from 'react-easy-edit';

const mapStateToProps = state => {
  return { list: state.list.list }
}


export class List extends Component {
  state = {
    tempValue: "",
    value: ""
  };

  componentWillMount() {
    this.props.getList(this.props.match.params.id);
  }

  saveEntry(entry_index, entry_id, day_index, text) {
    this.props.updateEntry(day_index, entry_index, entry_id, text);
  }

  render() {

    return (
      <div className="row">
          <div className='col-md-12'>
            {/* <h2>
              {this.props.list.name}
            </h2> */}
            <Link to={`/list_settings/${this.props.list.id}`}>
            <button className="btn btn-info float-right">Settings</button>
            </Link>
            <br></br>
            <br></br>
            <table className="table">
              {
                this.props.list.days.map((day, day_index) => (
                  <React.Fragment key={day.id}>
                    <thead className="thead-light">
                      <tr className="active d-flex">
                        <th className="col-sm-4 col-3 col-md-6">
                          {moment.utc(day.day).format("dddd")}
                        </th>
                        <th className="col-sm-8 col-9 col-md-6">
                          {moment.utc(day.day).format("MMM Do")}
                        </th>
                      </tr>
                    </thead>
                    {day.entries.map((entry, entry_index) => (
                      <tbody key={entry.id}>
                        <tr className="d-flex">
                          <td className="col-sm-4 col-3 col-md-6">{entry.meal}</td>
                          <td className="col-sm-8 col-9 col-md-6"><EasyEdit labelClassName={`label_${entry.id}`}
                              value={entry.value}
                              type="text"
                              saveButtonStyle="btn btn-sm btn-primary ml-2"
                              saveButtonLabel="✓"
                              cancelButtonStyle="btn btn-sm btn-secondary ml-1"
                              cancelButtonLabel="✕"
                              placeholder="Empty"
                              onSave={this.saveEntry.bind(this, entry_index, entry.id, day_index)}
                              />
                          </td>
                        </tr>
                      </tbody>
                    ))}
                  </React.Fragment>
                ))}
            </table>
          </div>
      </div>
    )
  }
}

export default connect(mapStateToProps, { getList, updateEntry })(List)
