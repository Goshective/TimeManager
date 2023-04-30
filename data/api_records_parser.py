from flask_restful import reqparse
from datetime import datetime


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('work_hours', required=True, type=int)
parser.add_argument('work_min', required=True, type=int)
parser.add_argument('datetime', type=lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))