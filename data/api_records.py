from flask import abort, jsonify
from flask_restful import abort, Resource

from data.db_session import *
from data.records import Records
from data.users import User
from data.act_names import Activities_names
from data.api_records_parser import parser


def abort_if_record_not_found(token, record_id):
    session, user = abort_if_records_not_found(token)
    record = session.query(Records).filter(Records.user == user, Records.id == record_id).all()
    if not record:
        session.close()
        abort(404, message=f"Record {record_id} not found for this user")
    return session, record[0]

def abort_if_records_not_found(token):
    session = create_session()
    user = session.query(User).filter(User.token == token).all()
    if not user:
        session.close()
        abort(404, message=f"User token not found")
    return session, user[0]

def abort_if_record_cant_be_posted(args, token):
    session = create_session()
    user = session.query(User).filter(User.token == token).all()
    if not user:
        session.close()
        abort(404, message=f"User token or activity_name not found")
    activity = session.query(Activities_names).filter(
            Activities_names.name == args['name'], Activities_names.user == user[0]).all()
    if not activity:
        session.close()
        abort(404, message=f"User token or activity_name not found")
    return session, user[0], activity[0]


class RecordsResource(Resource):
    def get(self, token, record_id):
        session, record = abort_if_record_not_found(token, record_id)
        js = jsonify({'records': record.to_dict(
            only=('user.login', 'act_n.name', 'work_hours', 'work_min', 'created_date'))})
        session.close()
        return js

    def delete(self, token, record_id):
        session, record = abort_if_record_not_found(token, record_id)
        session.delete(record)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
    

class RecordsListResource(Resource):
    def get(self, token):
        session, user = abort_if_records_not_found(token)
        records = session.query(Records).filter(Records.user == user).all()
        js = jsonify({'records': [item.to_dict(
            only=('user.login', 'act_n.name', 'work_hours', 'work_min', 'created_date')) for item in records]})
        session.close()
        return js

    def post(self, token):
        args = parser.parse_args()
        
        session, user, activity = abort_if_record_cant_be_posted(args, token)
        records = Records(
            name_id=activity.id,
            user_id=user.id,
            work_hours=args['work_hours'],
            work_min=args['work_min'],
            created_date=args['datetime']
        )
        session.add(records)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})