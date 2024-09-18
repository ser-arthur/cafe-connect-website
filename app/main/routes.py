from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .forms import CafeForm, LoginForm, RegistrationForm
from .models import db, Cafe, User
from werkzeug.utils import secure_filename
from functools import wraps
from config import Config
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from uuid import uuid4
import jwt
import os


UPLOAD_FOLDER = 'app/main/static/assets/img_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

main = Blueprint('main', __name__)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'message': 'Authentication required! Please log in.'}), 401

        if not current_user.is_admin:
            return jsonify({'message': 'Access denied! Admin privileges required.'}), 403

        return func(*args, **kwargs)

    return wrapper


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_token(user_id):
    """Generates a JWT token with an expiration time of 1 hour."""
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration
    }, Config.API_KEY, algorithm="HS256")
    return token


@main.route('/')
def home():
    """Displays the homepage."""
    return render_template('index.html', user=current_user)


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Registers a new user."""
    user_logged_in = False

    if current_user.is_authenticated:
        flash('User already logged in! Please log out first.', 'info')
        user_logged_in = True

    form = RegistrationForm()

    if form.validate_on_submit() and not user_logged_in:
        form.email.data = form.email.data.lower()
        username = form.create_username(form.email.data)
        new_user = User(username=username, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please sign in.', 'success')
        return redirect(url_for('main.login'))

    # Flash errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text} - {error}", 'error')

    return render_template('register.html', form=form, user_logged_in=user_logged_in)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in a user."""
    next_page = request.args.get('next')

    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login successful!', 'success')
            flash(f'Welcome {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text} - {error}", 'error')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    """Logs out a user."""
    next_page = request.args.get('next_page')
    print(next_page)
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for(next_page)) if next_page else redirect(url_for('main.home'))


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_cafe():
    """Adds a new cafe to the database."""
    form = CafeForm()

    if form.validate_on_submit():
        image_files = request.files.getlist('images')
        filepaths = []
        for image_file in image_files:
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid4().hex}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                image_file.save(filepath)
                filepaths.append(filepath)

        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            city=form.city.data,
            country=form.country.data,
            coffee_price=form.coffee_price.data,
            currency=form.currency.data,
            wifi_strength=int(form.wifi_strength.data),
            seats=form.seats.data,
            has_sockets=(form.has_sockets.data == 'True'),
            has_toilet=(form.has_toilet.data == 'True'),
            images=",".join(filepaths),
            full_review=form.full_review.data,
            full_rating=form.full_rating.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('main.give_feedback', action='add'))

    # Flash errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text} - {error}", 'error')

    return render_template('add.html', form=form)


@main.route('/update/<int:cafe_id>', methods=['GET', 'PATCH', 'POST'])
@login_required
@admin_required
def update_cafe(cafe_id):
    """Updates the details of a specific cafe."""
    cafe = Cafe.query.get(cafe_id)
    if not cafe:
        flash('Cafe not found!', 'error')
        return redirect(url_for('main.give_feedback', action='notfound'))

    form = CafeForm(obj=cafe)

    if request.method == 'GET':
        # Render template with prepopulated data
        return render_template('update.html', form=form, cafe=cafe)

    elif request.method in ['POST', 'PATCH']:
        if form.validate_on_submit():
            form.populate_obj(cafe)
            # Manually convert string boolean fields to actual booleans
            cafe.has_sockets = form.has_sockets.data == 'True'
            cafe.has_toilet = form.has_toilet.data == 'True'
            # Handle file uploads
            image_files = request.files.getlist('images')
            if image_files and image_files[0].filename != '':
                filepaths = []
                for image_file in image_files:
                    if image_file and allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        unique_filename = f"{uuid4().hex}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                        image_file.save(filepath)
                        filepaths.append(filepath)
                cafe.images = ",".join(filepaths)

            db.session.commit()
            return redirect(url_for('main.give_feedback', action='update'))

        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{getattr(form, field).label.text} - {error}", 'error')

    return render_template('update.html', form=form, cafe=cafe)


@main.route('/feedback', methods=['GET'])
@login_required
def give_feedback():
    """Gives feedback after adding or updating a cafe."""
    action = request.args.get('action')
    return render_template('feedback.html', action=action)


@main.route('/all', methods=['GET', 'POST'])
def get_all_cafes():
    """Retrieves all cafes from the database."""
    is_rated = request.args.get('is_rated')
    all_cafes = Cafe.query.all()
    cafes_list = [cafe.to_dict() for cafe in all_cafes]
    for cafe in cafes_list:
        cafe['country'] = cafe['country'].split('(')[1].strip(')')

    if is_rated:
        cafes_list = [cafe for cafe in cafes_list if cafe['full_rating'] == 5]
        cafes_list = sorted(cafes_list, key=lambda cafe: cafe['full_rating'], reverse=True)

    cafe_columns = ["Name", "Map URL", "Location", "Coffee Price", "Wifi Strength", "Seats", "Has Sockets",
                    "Has Toilet", "Cafe Rating"]
    return render_template('cafes.html', cafe_rows=cafes_list, cafe_columns=cafe_columns, is_rated=is_rated)


@main.route('/search', methods=['GET'])
def search_cafes():
    """Searches for cafes based on user input."""
    find_nearby = request.args.get('nearby')
    form = CafeForm()

    query = request.args.get('query') or request.args.get('city')
    cafes_list = Cafe.query.all()
    matching_cafes = []

    if query:
        for cafe in cafes_list:
            if (fuzz.partial_ratio(query.lower(), cafe.name.lower()) > 70 or
                    fuzz.partial_ratio(query.lower(), cafe.city.lower()) > 70 or
                    fuzz.partial_ratio(query.lower(), cafe.country.lower()) > 70):
                matching_cafes.append(cafe.to_dict())
        if not matching_cafes:
            flash("Sorry, no cafes matching your search criteria were found.", "info")
    else:
        if not find_nearby:
            flash("Please enter a search query.", "info")

    cafe_columns = ["Name", "Map URL", "Location", "Coffee Price", "Wifi Strength", "Seats", "Has Sockets",
                    "Has Toilet", "Cafe Rating"]

    return render_template('cafes.html', cafe_rows=matching_cafes, cafe_columns=cafe_columns,
                           find_nearby=find_nearby, form=form, mode="search")


@main.route('/delete_cafe/<int:cafe_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_cafe(cafe_id):
    """Deletes a cafe from the database."""
    cafe = Cafe.query.get(cafe_id)
    if not cafe:
        return redirect(url_for('main.give_feedback', action='notfound'))
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('main.give_feedback', action='delete'))
