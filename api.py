from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
if '__main__' == __name__:
    # not required during music mining
    import AdviseEngine

app = Flask(__name__)
# relative path to sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

# tags are "many to many" linker table
tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
)

# Track model
class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(64))
    title = db.Column(db.String(64))
    url = db.Column(db.String(128))
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('tracks', lazy='dynamic'))
    def __init__(self, artist, title, url):
        self.artist = artist
        self.title = title
        self.url = url

# Tag model
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    def __init__(self, name):
        self.name = name

class MusicAdvise(Resource):
    def get(self, artist, title):
        advicer = AdviseEngine.AdviseEngine(db)
        advised_track = advicer.getAdvise(artist, title)
        if advised_track is not None:
            return {
                    'error_code': 0,
                    'error_text': '',
                    'artist':advised_track.artist,
                    'title':advised_track.title,
                    'url':advised_track.url
                   }
        else:
            return {
                'error_code': 1,
                'error_text': 'Track not found! Please check spelling for /artist/title'
            }

api.add_resource(MusicAdvise, '/<string:artist>/<string:title>')

if __name__ == '__main__':
    app.run(debug=True)