from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

  def __init__(self, username, password):
    self.username= username
    self.set_password(password)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)
  
  def add_track(self, track_title):
    new_track = Track(track_title=track_title)
    new_track.user_id = self.id
    self.tracks.append(new_track)
    db.session.add(self)
    db.session.commit()
    return new_track

  def delete_track(self, track_id):
    track = Track.query.filter_by(id=track_id, user_id=self.id).first()
    if track:
      db.session.delete(track)
      db.session.commit()
      return True
    return None
  
  def search_tracks(self, q, page): 
    matching_tracks = None
  
    if q!="" :
      matching_tracks = Track.query.join(User).filter(
        db.or_(User.id.ilike(f'%{q}%'), Track.track_title.ilike(f'%{q}%'), Track.id.ilike(f'%{q}%'))
      )
    else:
      matching_tracks = Track.query
      
    return matching_tracks.paginate(page=page, per_page=10)
  
class Track(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  track_title = db.Column(db.String(120), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class TrackAlbum(db.Model):
  __tablename__ = 'track_album'
  id = db.Column(db.Integer, primary_key=True)
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
  album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)


class Album(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  album_title = db.Column(db.String(120), primary_key=True)
  artist_name = db.Column(db.String(120), nullable=False)
  cover = db.Column(db.String(120), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  user = db.relationship('User', backref=db.backref('albums', lazy='joined'))
  tracks = db.relationship('Track', secondary='track_album', backref=db.backref('albums', lazy=True))


