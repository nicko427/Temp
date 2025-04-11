import os, csv
from flask import Flask, redirect, render_template, request, flash, url_for
from App.models import *
from datetime import timedelta

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
    current_user,
)


def create_app():
  app = Flask(__name__, static_url_path='/static')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
  app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
  app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
  app.config["JWT_COOKIE_SECURE"] = True
  app.config["JWT_SECRET_KEY"] = "super-secret"
  app.config["JWT_COOKIE_CSRF_PROTECT"] = False
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

  app.app_context().push()
  return app


app = create_app()
db.init_app(app)

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
  return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
  flash("Your session has expired. Please log in again.")
  return redirect(url_for('login'))

def initialize_db():
  db.drop_all()
  db.create_all()
  bob = User('bob', 'bobpass')
  db.session.add(bob)
  db.session.commit()
  album = Album(user_id='1' , id='1', album_title='Album1', artist_name='Artist1', cover='https://weblabs.web.app/api/brainrot/1.webp')
  db.session.add(album)
  db.session.commit()
  album = Album(user_id='1' , id='1', album_title='Album2', artist_name='Artist2', cover='https://weblabs.web.app/api/brainrot/2.webp')
  db.session.add(album)
  db.session.commit()
  album = Album(user_id='1', id='1', album_title='Album3', artist_name='Artist3', cover='https://weblabs.web.app/api/brainrot/3.webp')
  db.session.add(album)
  db.session.commit()
  album = Album(user_id='1', id='1', album_title='Album4', artist_name='Artist4', cover='https://weblabs.web.app/api/brainrot/4.webp')
  db.session.add(album)
  db.session.commit()
  album = Album(user_id='1', id='1', album_title='Album5', artist_name='Artist5', cover='https://weblabs.web.app/api/brainrot/5.webp')
  db.session.add(album)
  db.session.commit()
  album = Album(user_id='1', id='1', album_title='Album6', artist_name='Artist6', cover='https://weblabs.web.app/api/brainrot/6.webp')
  db.session.add(album)
  db.session.commit()
  print('database intialized')


@app.route('/')
def login():
  return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_action():
  username = request.form.get('username')
  password = request.form.get('password')
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    response = redirect(url_for('home'))
    access_token = create_access_token(identity=user.id)
    set_access_cookies(response, access_token)
    return response
  else:
    flash('Invalid username or password')
    return redirect(url_for('login'))


@app.route('/app')
@jwt_required()
def home():
  return render_template('index.html')


@app.route('/logout', methods=['GET'])
@jwt_required()
def logout_action():
  flash('Logged Out')
  response = redirect(url_for('login_page'))
  unset_jwt_cookies(response)
  return response

@app.route('/createTrack', methods=['POST'])
@jwt_required()
def create_track_action():
  data = request.form
  current_user.add_track(data['track_title'])
  flash('Created')
  return redirect(url_for('tracks_page'))

@app.route('/deleteTrack/<id>', methods=["GET"])
@jwt_required()
def delete_track_action(id):
  res = current_user.delete_track(id)
  if res == None:
    flash('Invalid id or unauthorized')
  else:
    flash('Track Deleted')
  return redirect(url_for('tracks_page'))

@app.route('/')
@jwt_required()
def user_page():
  page = request.args.get('page', 1, type=int)
  q = request.args.get('q', default='', type=str)
  tracks = current_user.search_tracks(q, page)
  return render_template('index.html', tracks=tracks, page=page, q=q)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
