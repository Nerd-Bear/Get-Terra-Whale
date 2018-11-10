from flask_restful import Resource
from flasgger import swag_from
from flask import jsonify, Response, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from datetime import datetime

from docs.map import MAP_GET

from model.booth import BoothModel
from model.user import UserModel
from model.team import TeamModel


class MapView(Resource):

    @swag_from(MAP_GET)
    @jwt_required
    def get(self):
        user: UserModel = UserModel.objects(userId=get_jwt_identity()).first()
        if not user:
            return abort(403)

        default_team: TeamModel = TeamModel.objects(teamName='empty').first()
        end: datetime = current_app.config['END_TIME']
        end = {'year': end.year, 'month': end.month, 'day': end.day, 'hour': end.hour, 'minute': end.minute}
        map_ = {'map': {}, 'endTime': end, 'myTeam': user.team.teamName}
        for booth in BoothModel.objects():
            if booth.ownTeam == default_team:
                map_['map'][booth.boothName] = None
            elif booth.ownTeam == user.team:
                map_['map'][booth.boothName] = True
            else:
                map_['map'][booth.boothName] = False

        return jsonify(map_)