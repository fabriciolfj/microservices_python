import copy
import uuid
from datetime import datetime

from flask import abort
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import ValidationError

from api.schemas import (
    GetScheduledOrdersSchema,
    ScheduleOrderSchema,
    GetScheduledOrderSchema,
    ScheduleStatusSchema,
    GetKitchenScheduleParameters
)

schedules = []

blueprint = Blueprint('kitchen', __name__, description='Kitchen Api')


def validation_schedule(schedule):
    schedule = copy.deepcopy(schedule)
    schedule['scheduled'] = schedule['scheduled'].isoformat()
    errors = GetScheduledOrderSchema().validate(schedule)
    if errors:
        raise ValidationError(errors)

@blueprint.route('/kitchen/schedules')
class KitchenSchedules(MethodView):

    @blueprint.arguments(GetKitchenScheduleParameters, location='query')
    @blueprint.response(status_code=200, schema=GetScheduledOrdersSchema)
    def get(self, parameters):
        for schedule in schedules:
            validation_schedule(schedule)

        if not parameters:
            return {'schedules': schedules}

        query_set = [schedule for schedule in schedules]

        in_progress = parameters.get('progress')
        if in_progress is not None:
            if in_progress:
                query_set = [schedule for schedule in schedules
                            if schedule['status'] == 'progress'
                ]
            else:
                query_set = [schedule for schedules in schedules
                             if schedule != 'progress']

        since = parameters.get('sincomce')
        if since is not None:
            if since:
                query_set = [schedule for schedule in schedules
                             if schedule['scheduled'] >= since
                ]

        limit = parameters.get('limit')
        if limit is not None and len(query_set) > limit:
            query_set = query_set[:limit]

        return {'schedules': query_set}

    @blueprint.arguments(ScheduleOrderSchema)
    @blueprint.response(status_code=201, schema=GetScheduledOrderSchema)
    def post(self, payload):
        payload['id'] = str(uuid.uuid4())
        payload['scheduled'] = datetime.utcnow()
        payload['status'] = 'pending'
        schedules.append(payload)

        validation_schedule(payload)
        return payload


@blueprint.route('/kitchen/schedules/<schedule_id>')
class KitchenSchedule(MethodView):

    @blueprint.response(status_code=200, schema=GetScheduledOrderSchema)
    def get(self, schedule_id):
        for schedule in schedules:
            if schedule['id'] == schedule_id:
                validation_schedule(schedule)
                return schedule

        abort(404, description=f'Resource with id {schedule_id} not found')

    @blueprint.arguments(ScheduleOrderSchema)
    @blueprint.response(status_code=200, schema=GetScheduledOrderSchema)
    def put(self, payload, schedule_id):
        for schedule in schedules:
            if schedule['id'] == schedule_id:
                schedules.update(payload)

                validation_schedule(schedule)
                return schedule

        abort(404, f'Resource id {schedule_id} not found')

    @blueprint.response(status_code=204)
    def delete(self, schedule_id):
        for index, schedule in enumerate(schedules):
            if schedule['id'] == schedule_id:
                schedules.pop(index)
                return

        abort(404, description=f'Resouce id {schedule_id}, not found')


@blueprint.response(status_code=200, schema=GetScheduledOrderSchema)
@blueprint.route('/kitchen/schedules/<schedule_id>/cancel', methods=['POST'])
def cancel_schedule(schedule_id):
    for schedule in schedules:
        if schedule['id'] == schedule_id:
            schedule['status'] = 'cancelled'
            validation_schedule(schedule)
            return schedule

    abort(404, description=f'Resouce id {schedule_id}, not found')


@blueprint.response(status_code=200, schema=ScheduleStatusSchema)
@blueprint.route('/kitchen/schedules/<schedule_id>/status', methods=['GET'])
def get_schedule_status(schedule_id):
    for schedule in schedules:
        if schedule['id'] == schedule_id:
            validation_schedule(schedule)
            return {'status': schedule['status']}

    abort(404, description=f'Resouce id {schedule_id}, not found')

