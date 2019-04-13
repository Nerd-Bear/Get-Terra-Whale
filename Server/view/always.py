from typing import List

from flask_restful import Resource
from flasgger import swag_from
from flask import jsonify, g, Response

from doc import ALWAYS_MAP_GET
import model


class AlwaysMapView(Resource):

    @swag_from(ALWAYS_MAP_GET)
    def get(self) -> Response:
        map_: dict = {'map': {}}
        booths: List[model.AlwaysBoothModel] = model.AlwaysBoothModel.objects()

        for booth in booths:
            map_['map'][booth.booth_name] = {
                'captured': booth in g.user.always_capture,
                'latitude': booth.latitude,
                'longitude': booth.longitude,
            }

        return jsonify(map_)