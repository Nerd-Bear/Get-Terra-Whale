from datetime import datetime, timedelta

from flask import Flask, abort, request, current_app, Response
from flask_restful import Api, Resource

from const import ADMIN_CODE
import model


class Router:
    def __init__(self, app: Flask):
        self.app = app
        self.api = Api(app)

    def register(self):
        from view.auth import AuthView
        self.api.add_resource(AuthView, '/auth/<deviceUUID>')

        from view.map import MapView
        self.api.add_resource(MapView, '/map')

        from view.solve import SolveView
        self.api.add_resource(SolveView, '/solve/<boothName>')

        from view.team import TeamView
        self.api.add_resource(TeamView, '/team')

        from view.stamp import StampCaptureView, StampMapView
        self.api.add_resource(StampMapView, '/stamp/map')
        self.api.add_resource(StampCaptureView, '/stamp')

        from view.coupon import CouponView
        self.api.add_resource(CouponView, '/coupon')

        self.app.add_url_rule('/admin/initialize', 'initialize', view_func=initialize, methods=['POST'])


def get_all_models():
    return [getattr(model, m) for m in dir(model) if m.endswith('Model')]


def initialize():
    admin_code = request.json.get('adminCode')
    if admin_code != ADMIN_CODE:
        return abort(403)

    models = get_all_models()
    for m in models:
        m.initialize()

    return Response('', 201)


class BaseResource(Resource):

    @staticmethod
    def get_kst_now():
        return datetime.utcnow() + timedelta(hours=9)

    @staticmethod
    def get_start_time() -> datetime:
        return current_app.config['START_TIME']

    @staticmethod
    def get_end_time() -> datetime:
        return current_app.config['END_TIME']

    def check_time(self):
        start_time = self.get_start_time()
        now = self.get_kst_now()
        end_time = self.get_end_time()

        if now < start_time:
            abort(406)
        elif end_time < now:
            abort(408)

    def get_left_time(self):
        left_time: datetime = self.get_end_time() - self.get_kst_now()
        return f'{left_time.minute}:{left_time.second}'

    @staticmethod
    def get_current_user():
        user = model.UserModel.get_user_by_device_uuid(device_uuid=request.headers['deviceUUID'])
        if user is None:
            return abort(403)
        return user
