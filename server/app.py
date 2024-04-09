#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''


class Campers(Resource):

    def get(self):
        campers = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]

        return make_response(
            campers,
            200
        )
        
    def post(self):
        try:
            new_camper = Camper(
                name=request.json.get('name'),
                age=request.json.get('age')
            )

            db.session.add(new_camper)
            db.session.commit()

            return make_response(new_camper.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
    
api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()

        if camper:
            response_body = camper.to_dict(rules=('-signups.camper', '-signups.activity.signups'))
            return make_response(response_body, 200)
        else:
            response_body = make_response(
                {"error": "Camper not found"},
                404
            )
            return response_body
        
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()

        if(camper):
            try:
                for attr in request.json:
                    setattr(camper, attr, request.json[attr])
                
                db.session.commit()
                reponse_body = camper.to_dict(only=('id', 'name', 'age'))
                return make_response(reponse_body, 202)
            except:
                response_body = {
                    "errors": ["validation errors"]
                }
                return make_response(response_body, 400)
        else:
            reponse_body = {
                "error": "Camper not found"
            }
            return make_response(reponse_body, 404)
        
api.add_resource(CamperByID, '/campers/<int:id>')
    

class Activites(Resource):
    def get(self):
        response_body = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in Activity.query.all()]
        return make_response(response_body, 200)

        
    
api.add_resource(Activites, '/activities')

class ActivityByID(Resource):

    def delete(self, id):
        activity = db.session.get(Activity, id)

        if(activity):
            db.session.delete(activity)
            db.session.commit()
            response_body = {}
            return make_response(response_body, 204)
        else:
            response_body = {
                "error": "Activity not found"
            }
            return make_response(response_body, 404)

api.add_resource(ActivityByID, '/activities/<int:id>')
        
        
class AllSignups(Resource):

    def post(self):
        try:
            new_signup = Signup(
                camper_id=request.json.get('camper_id'), 
                activity_id=request.json.get('activity_id'), 
                time=request.json.get('time')
                )
            db.session.add(new_signup)
            db.session.commit()
            response_body = new_signup.to_dict(rules=('-activity.signups', '-camper.signups'))
            return make_response(response_body, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

api.add_resource(AllSignups, '/signups')





if __name__ == '__main__':
    app.run(port=5555, debug=True)
