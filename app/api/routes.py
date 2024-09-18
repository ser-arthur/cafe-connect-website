from flask import request, jsonify
from flask_login import current_user, login_user
from marshmallow import ValidationError
from app.api.schemas import CafeSchema
from functools import wraps
from app.main.models import User, Cafe, db
from app.main.routes import generate_token
from app.main import limiter
from config import Config
from . import api
import jwt

def token_required(func):
    """Decorator that ensures a valid token is present in the request headers."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token format is invalid!'}), 400
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token and verify the user
            data = jwt.decode(token, Config.API_KEY, algorithms=["HS256"])
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'message': 'User not found!'}), 401

            login_user(user)

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired! Please login again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return func(*args, **kwargs)
    return decorated_function


def admin_required(func):
    """Grants admin privileges."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'message': 'Authentication required!'}), 401
        if not current_user.is_admin:
            return jsonify({'message': 'Access forbidden: Admin privileges required!'}), 403
        return func(*args, **kwargs)
    return wrapper


@api.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_login():
    """Logs in a user and returns a token."""
    if not request.is_json:
        return jsonify({'message': 'Check request body. Please provide login credentials in JSON format.'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is empty. Please provide login credentials.'}), 400

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Invalid credentials!'}), 400

    user = User.query.filter_by(email=data['email'].lower()).first()

    if user and user.check_password(data['password']):
        token = generate_token(user.id)

        if user.is_admin:
            # Bypass rate limiting for admin users
            limiter.reset()
            return jsonify({'token': token, 'message': 'Admin login successful!'}), 200

        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401


@api.route('/cafes', methods=['GET'])
@token_required
@limiter.limit("15 per minute")
def get_all_cafes():
    """Fetches a list of all cafes."""
    cafes = Cafe.query.all()
    cafes_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=cafes_list)


@api.route('/cafes/<int:cafe_id>', methods=['GET'])
@token_required
@limiter.limit("15 per minute")
def get_cafe(cafe_id):
    """Retrieves information about a specific cafe by ID."""
    cafe = Cafe.query.get(cafe_id)
    if not cafe:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    return jsonify(cafe=cafe.to_dict())


@api.route('/cafes', methods=['POST'])
@token_required
@limiter.limit("10 per minute")
def add_cafe():
    """Adds a new cafe to the database."""
    if current_user.is_admin:
        limiter.reset()
    if not request.is_json:
        return jsonify({'message': 'Check request body. Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is empty. Please provide data in JSON format.'}), 400

    schema = CafeSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    existing_cafe = Cafe.query.filter_by(name=data['name']).first()
    if existing_cafe:
        return jsonify({'message': f"Cafe '{existing_cafe.name}' already exists in the database."}), 409

    new_cafe = Cafe(
        name=data['name'],
        map_url=data['map_url'],
        city=data['city'],
        country=data['country'],
        coffee_price=data['coffee_price'],
        currency=data['currency'],
        wifi_strength=data['wifi_strength'],
        seats=data['seats'],
        has_sockets=data['has_sockets'],
        has_toilet=data['has_toilet'],
        images=data['images'],
        full_review=data['full_review'],
        full_rating=data['full_rating']
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify({"message": "Cafe added successfully!", "cafe": new_cafe.to_dict()}), 201


@api.route('/cafes/<int:cafe_id>', methods=['PUT'])
@token_required
@admin_required
def update_cafe(cafe_id):
    """Updates an existing cafe in the database."""
    cafe = Cafe.query.get(cafe_id)
    if not cafe:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404

    if not request.is_json:
        return jsonify({'message': 'Check request body. Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is empty. Please provide data in JSON format.'}), 400

    schema = CafeSchema()
    try:
        data = schema.load(request.get_json(), partial=True)    # partial=True allows partial updates
    except ValidationError as err:
        return jsonify(err.messages), 400

    cafe.name = data.get('name', cafe.name)
    cafe.map_url = data.get('map_url', cafe.map_url)
    cafe.city = data.get('city', cafe.city)
    cafe.country = data.get('country', cafe.country)
    cafe.coffee_price = data.get('coffee_price', cafe.coffee_price)
    cafe.currency = data.get('currency', cafe.currency)
    cafe.wifi_strength = data.get('wifi_strength', cafe.wifi_strength)
    cafe.seats = data.get('seats', cafe.seats)
    cafe.has_sockets = data.get('has_sockets', cafe.has_sockets)
    cafe.has_toilet = data.get('has_toilet', cafe.has_toilet)
    cafe.images = data.get('images', cafe.images)
    cafe.full_review = data.get('full_review', cafe.full_review)
    cafe.full_rating = data.get('full_rating', cafe.full_rating)

    db.session.commit()
    return jsonify({"message": f"{cafe.name} updated successfully!", "cafe": cafe.to_dict()})


@api.route('/cafes/<int:cafe_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_cafe(cafe_id):
    """Deletes a cafe from the database."""
    cafe = Cafe.query.get(cafe_id)
    if not cafe:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    db.session.delete(cafe)
    db.session.commit()
    return jsonify({"message": f"{cafe.name} deleted successfully!"}), 200
