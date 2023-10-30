#!/usr/bin/python3
'''
Createw Flask app; and register the blueprint app_views to Flask instance app.
'''


from os import getenv
from flask import Flask, jsonify
from flask_cors import CORS
from models import storage
from api.v1.views import app_views


app = Flask(__name__)


# enable CORS and allow for origins:
CORS(app, resources={r'/api/v1/*': {'origins': '0.0.0.0'}})


app.register_blueprint(app_views)
app.url_map.strict_slashes = False




@app.teardown_appcontext
def teardown_engine(exception):
    '''
    Removes the current SQLAlchemy Session object after each request.
    '''
    storage.close()




# Error handlers for expected app behavior:
@app.errorhandler(404)
def not_found(error):
    '''
    Return errmsg `Not Found`.
    '''
    response = {'error': 'Not found'}
    return jsonify(response), 404




if __name__ == '__main__':
    HOST = getenv('HBNB_API_HOST', '0.0.0.0')
    PORT = int(getenv('HBNB_API_PORT', 5000))
    app.run(host=HOST, port=PORT, threaded=True)


api/v1/views/__init__.py


#!/usr/bin/python3
'''
Creates a Blueprint instance with `url_prefix` set to `/api/v1`.
'''




from flask import Blueprint


app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')


from api.v1.views.index import *
from api.v1.views.states import *
from api.v1.views.cities import *
from api.v1.views.amenities import *
from api.v1.views.users import *
from api.v1.views.places import *
from api.v1.views.places_reviews import *
from api.v1.views.places_amenities import *


api/v1/views/amenities.py


#!/usr/bin/python3
'''
Creates a view for Amenity objects - handles all default RESTful API actions.
'''


# Import necessary modules
from flask import abort, jsonify, request
from models.amenity import Amenity
from api.v1.views import app_views
from models import storage




# Route for retrieving all Amenity objects
@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
def get_all_amenities():
    '''Retrieves the list of all Amenity objects'''
    # Get all Amenity objects from the storage
    amenities = storage.all(Amenity).values()
    # Convert objects to dictionaries and jsonify the list
    return jsonify([amenity.to_dict() for amenity in amenities])




# Route for retrieving a specific Amenity object by ID
@app_views.route('/amenities/<amenity_id>',
                 methods=['GET'], strict_slashes=False)
def get_amenity(amenity_id):
    '''Retrieves an Amenity object'''
    # Get the Amenity object with the given ID from the storage
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        # Return the Amenity object in JSON format
        return jsonify(amenity.to_dict())
    else:
        # Return 404 error if the Amenity object is not found
        abort(404)




# Route for deleting a specific Amenity object by ID
@app_views.route('/amenities/<amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    '''Deletes an Amenity object'''
    # Get the Amenity object with the given ID from the storage
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        # Delete the Amenity object from the storage and save changes
        storage.delete(amenity)
        storage.save()
        # Return an empty JSON with 200 status code
        return jsonify({}), 200
    else:
        # Return 404 error if the Amenity object is not found
        abort(404)




# Route for creating a new Amenity object
@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
def create_amenity():
    '''Creates an Amenity object'''
    if not request.get_json():
        # Return 400 error if the request data is not in JSON format
        abort(400, 'Not a JSON')


    # Get the JSON data from the request
    data = request.get_json()
    if 'name' not in data:
        # Return 400 error if 'name' key is missing in the JSON data
        abort(400, 'Missing name')


    # Create a new Amenity object with the JSON data
    amenity = Amenity(**data)
    # Save the Amenity object to the storage
    amenity.save()
    # Return the newly created Amenity
    #   object in JSON format with 201 status code
    return jsonify(amenity.to_dict()), 201




# Route for updating an existing Amenity object by ID
@app_views.route('/amenities/<amenity_id>', methods=['PUT'],
                 strict_slashes=False)
def update_amenity(amenity_id):
    '''Updates an Amenity object'''
    # Get the Amenity object with the given ID from the storage
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        # Return 400 error if the request data is not in JSON format
        if not request.get_json():
            abort(400, 'Not a JSON')


        # Get the JSON data from the request
        data = request.get_json()
        ignore_keys = ['id', 'created_at', 'updated_at']
        # Update the attributes of the Amenity object with the JSON data
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(amenity, key, value)


        # Save the updated Amenity object to the storage
        amenity.save()
        # Return the updated Amenity object in JSON format with 200 status code
        return jsonify(amenity.to_dict()), 200
    else:
        # Return 404 error if the Amenity object is not found
        abort(404)




# Error Handlers:
@app_views.errorhandler(404)
def not_found(error):
    '''Returns 404: Not Found'''
    # Return a JSON response for 404 error
    response = {'error': 'Not found'}
    return jsonify(response), 404




@app_views.errorhandler(400)
def bad_request(error):
    '''Return Bad Request message for illegal requests to the API.'''
    # Return a JSON response for 400 error
    response = {'error': 'Bad Request'}
    return jsonify(response), 400


api/v1/views/cities.py


#!/usr/bin/python3
'''
Create a new view for City objects - handles all default RESTful API actions.
'''


# Import necessary modules
from flask import abort, jsonify, request
# Import the State and City models
from models.state import State
from models.city import City
from api.v1.views import app_views
from models import storage




# Route for retrieving all City objects of a specific State
@app_views.route('/states/<state_id>/cities', methods=['GET'],
                 strict_slashes=False)
def get_cities_by_state(state_id):
    '''
    Retrieves the list of all City objects of a State.
    '''
    # Get the State object with the given ID from the storage
    state = storage.get(State, state_id)
    if not state:
        # Return 404 error if the State object is not found
        abort(404)


    # Get all City objects associated with
    #   the State and convert them to dictionaries
    cities = [city.to_dict() for city in state.cities]
    return jsonify(cities)




# Route for retrieving a specific City object by ID
@app_views.route('/cities/<city_id>', methods=['GET'], strict_slashes=False)
def get_city(city_id):
    '''
    Retrieves a City object.
    '''
    # Get the City object with the given ID from the storage
    city = storage.get(City, city_id)
    if city:
        # Return the City object in JSON format
        return jsonify(city.to_dict())
    else:
        # Return 404 error if the City object is not found
        abort(404)




# Route for deleting a specific City object by ID
@app_views.route('/cities/<city_id>', methods=['DELETE'])
def delete_city(city_id):
    '''
    Deletes a City object.
    '''
    # Get the City object with the given ID from the storage
    city = storage.get(City, city_id)
    if city:
        # Delete the City object from the storage and save changes
        storage.delete(city)
        storage.save()
        # Return an empty JSON with 200 status code
        return jsonify({}), 200
    else:
        # Return 404 error if the City object is not found
        abort(404)




# Route for creating a new City object under a specific State
@app_views.route('/states/<state_id>/cities', methods=['POST'],
                 strict_slashes=False)
def create_city(state_id):
    '''
    Creates a City object.
    '''
    # Get the State object with the given ID from the storage
    state = storage.get(State, state_id)
    if not state:
        # Return 404 error if the State object is not found
        abort(404)


    # Check if the request data is in JSON format
    if not request.get_json():
        # Return 400 error if the request data is not in JSON format
        abort(400, 'Not a JSON')


    # Get the JSON data from the request
    data = request.get_json()
    if 'name' not in data:
        # Return 400 error if 'name' key is missing in the JSON data
        abort(400, 'Missing name')


    # Assign the 'state_id' key in the JSON data
    data['state_id'] = state_id
    # Create a new City object with the JSON data
    city = City(**data)
    # Save the City object to the storage
    city.save()
    # Return the newly created City object in JSON format with 201 status code
    return jsonify(city.to_dict()), 201




# Route for updating an existing City object by ID
@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)
def update_city(city_id):
    '''
    Updates a City object.
    '''
    # Get the City object with the given ID from the storage
    city = storage.get(City, city_id)
    if city:
        # Check if the request data is in JSON format
        if not request.get_json():
            # Return 400 error if the request data is not in JSON format
            abort(400, 'Not a JSON')


        # Get the JSON data from the request
        data = request.get_json()
        ignore_keys = ['id', 'state_id', 'created_at', 'updated_at']
        # Update the attributes of the City object with the JSON data
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(city, key, value)


        # Save the updated City object to the storage
        city.save()
        # Return the updated City object in JSON format with 200 status code
        return jsonify(city.to_dict()), 200
    else:
        # Return 404 error if the City object is not found
        abort(404)




# Error Handlers:
@app_views.errorhandler(404)
def not_found(error):
    '''
    404: Not Found.
    '''
    # Return a JSON response for 404 error
    return jsonify({'error': 'Not found'}), 404




@app_views.errorhandler(400)
def bad_request(error):
    '''
    Return Bad Request message for illegal requests to API.
    '''
    # Return a JSON response for 400 error
    return jsonify({'error': 'Bad Request'}), 400


api/v1/views/index.py


#!/usr/bin/python3
'''
Create a route `/status` on the object app_views.
'''




from flask import jsonify
from api.v1.views import app_views
from models import storage




@app_views.route('/status', methods=['GET'])
def api_status():
    '''
    Returns a JSON response for RESTful API health.
    '''
    response = {'status': 'OK'}
    return jsonify(response)




@app_views.route('/stats', methods=['GET'])
def get_stats():
    '''
    Retrieves the number of each objects by type.
    '''
    stats = {
        'amenities': storage.count('Amenity'),
        'cities': storage.count('City'),
        'places': storage.count('Place'),
        'reviews': storage.count('Review'),
        'states': storage.count('State'),
        'users': storage.count('User')
    }
    return jsonify(stats)
