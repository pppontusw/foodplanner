import React, { Component, Fragment } from 'react'
import { Link, Redirect } from 'react-router-dom'
import { connect } from 'react-redux';
import { getData, clearList, createList } from '../actions'
import moment from 'moment';
import { NewList } from './NewList';
import $ from 'jquery';
import 'bootstrap';

const mapStateToProps = state => {
  return { lists: state.lists.lists }
}

export class Lists extends Component {

  componentWillMount() {
    this.props.getData();
    this.props.clearList();
  }

  createListClick = () => {
    // this.props.openNewListModal()
    $('#exampleModal').modal('show');
  }

  render() {
    // if (this.props.lists.length === 1) {
    //   return <Redirect to={`list/${this.props.lists[0].id}`} />
    // }
      
    
    return (
      <Fragment>
      <NewList {...this.props} />
      <div className="row">
        {this.props.lists.map(el => (
          <div key={el.id} className={this.props.lists.length > 1 ? 'col-md-6' : 'col-md-12'}>
            <h1 className='text-center'>
                <a href={`#/list/${el.id}`}>{el.name}</a>
              </h1>
              <table className="table table">
                
                {
                  el.days.map(day => (
                  <React.Fragment key={day.id}>
                    <thead className="thead-light">
                    <tr className="active">
                      <th>
                          {moment.utc(day.day).format("dddd")}
                      </th>
                      <th>
                          {moment.utc(day.day).format("MMM Do")}
                      </th>
                    </tr>
                    </thead>
                    {day.entries.map(entry => (
                      <tbody key={entry.id}>
                      <tr>
                        <td>{entry.meal}</td>
                        <td>{entry.value}</td>
                      </tr>
                      </tbody>
                    ))}
                  </React.Fragment>
                ))}
                
              </table>
           
            </div>
        ))}
      </div>
        <div className="row">
          <button className="btn btn-primary" onClick={this.createListClick.bind(this)}>Create new list</button>
        </div>
        <br></br>
      </Fragment>
    )
  }
}

export default connect(mapStateToProps, { getData, clearList, createList })(Lists)
