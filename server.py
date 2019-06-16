from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.sql.expression import func
import os
import random

import porter_utils as putils
from simulator.hospital import Hospital
from simulator.location import Location as SimLocation
from solver_with_urgency import solver

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'porteroo.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Porter(db.Model):
    __tablename__ = 'porters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    active = db.Column(db.Integer)
    location = db.Column(db.Integer)


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)


class LocationDistance(db.Model):
    __tablename__ = 'location_distances'
    id = db.Column(db.Integer, primary_key=True)
    from_location = db.Column(db.Integer)
    to_location = db.Column(db.Integer)
    distance = db.Column(db.Integer)


class Delivery(db.Model):
    __tablename__ = 'deliveries'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer)
    priority = db.Column(db.Integer)
    from_location = db.Column(db.Integer)
    to_location = db.Column(db.Integer)
    status = db.Column(db.String(80))
    picked_up_at = db.Column(db.Integer)
    delivered_at = db.Column(db.Integer)


class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    porter = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    location = db.Column(db.Integer)
    estimated_pickup = db.Column(db.Integer)
    estimated_dropoff = db.Column(db.Integer)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    porter = db.Column(db.Integer)
    location = db.Column(db.Integer)
    created_at = db.Column(db.Integer)


class LocationSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name')


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)


class PorterSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name', 'location')


class DeliverySchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'from_location', 'created_at', 'status', 'priority')


class RouteSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'porter')


class LocationDistanceSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'from_location', 'to_location', 'distance')


def runSimulation():
    # Get Locations
    all_locations = LocationSchema(many=True).dump(Location.query.all())
    locations = [SimLocation(x['name'], x['id']) for x in all_locations[0]]
    print(locations)
    # Get Location Distances
    location_distance_query = LocationDistance.query.order_by(LocationDistance.from_location.asc(),LocationDistance.to_location.asc()).all()
    all_location_distances = LocationDistanceSchema(many=True).dump(location_distance_query)
    distances = []
    for x in enumerate(locations):
        distances.append([])
    for ld in all_location_distances[0]:
        distances[ld['from_location']].append(ld['distance'])
    print(distances)
    current_hospital = Hospital(locations, distances)
    porters = PorterSchema(many=True).dump(Porter.query.all())
    # Add Porters
    for p in porters[0]:
        current_hospital.add_porter(name=p['name'], current_location=p['location'], id=p['id'])
    deliveries = DeliverySchema(many=True).dump(Delivery.query.all())
    # Add Deliveries
    for d in deliveries[0]:
        print(d)
        if d['priority'] == 1:
            window = 600
        else:
            window = 1500
        print(d['created_at'])
        delivery_deadline = putils.deadline(d['created_at'], window)
        current_hospital.add_sample(d['id'], d['id'], d['from_location'], delivery_deadline)
    # Run through Solver
    routes = solver(current_hospital, putils.current_time())
    print(routes)
    return routes


# endpoint to create new user
@app.route("/location", methods=["POST"])
def add_location():

    all_locations = LocationSchema(many=True).dump(Location.query.all())
    new_location_id = len(all_locations[0])

    name = request.json['name']

    new_location = Location(name=name)
    db.session.add(new_location)

    db.session.add(LocationDistance(from_location=new_location_id,
                                    to_location=new_location_id,
                                    distance=0))

    for l in all_locations[0]:
        distance = random.randint(1,500)
        from_location_distance = LocationDistance(from_location=new_location_id,
                                                  to_location=l['id'],
                                                  distance=distance)
        db.session.add(from_location_distance)
        to_location_distance = LocationDistance(from_location=l['id'],
                                                  to_location=new_location_id,
                                                  distance=distance)
        db.session.add(to_location_distance)


    db.session.commit()

    return "True"


# endpoint to create new user
@app.route("/request", methods=["POST"])
def add_delivery():
    fromLocation = request.json['location']
    toLocation = request.json['destination']
    urgent = request.json['urgent']
    status = 'requested'
    createdAt = putils.current_time()

    new_delivery = Delivery(from_location=fromLocation,
                            to_location=toLocation, priority=urgent,
                            status=status, created_at=createdAt)

    db.session.add(new_delivery)
    db.session.commit()

    return "True"


# endpoint to create new user
@app.route("/checkin", methods=["PUT"])
def checkin(id):
    delivery = Delivery.query.get(id)

    delivery.status = 'collected'
    delivery.picked_up_at = putils.current_time()

    db.session.commit()
    return DeliverySchema().jsonify(delivery)


# endpoint to show all users
@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    all_deliveries = Delivery.query.all()
    result = DeliverySchema(many=True).dump(all_deliveries)
    return jsonify(result.data)


# endpoint to show all users
@app.route("/locations", methods=["GET"])
def get_locations():
    all_locations = Location.query.all()
    result = locations_schema.dump(all_locations)
    return jsonify(result.data)


# endpoint to get user detail by id
@app.route("/porter/<id>", methods=["GET"])
def user_detail(id):
    user = Porter.query.get(id)
    return PorterSchema().jsonify(user)


# endpoint to get user detail by id
@app.route("/routes", methods=["GET"])
def get_routes():
    all_routes = Route.query.all()
    result = RouteSchema(many=True).dump(all_routes)
    return jsonify(result.data)

# endpoint to get user detail by id
@app.route("/test", methods=["GET"])
def test():
    runSimulation()
    return "True"


if __name__ == '__main__':
    app.run(debug=True)
