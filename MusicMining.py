import pylast
import time
from api import db
from api import Track
from api import Tag
db.create_all()

# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from http://www.last.fm/api/account for Last.fm
API_KEY = "1f9c7b6a84a0d3c76d5138e27a4029b9"
API_SECRET = "d41365d0671c5d738130456dc3c56a8e"

# authentication
username = "zab88"
password_hash = pylast.md5("")

network = pylast.LastFMNetwork(api_key = API_KEY, api_secret =
    API_SECRET, username = username, password_hash = password_hash)

# adding one track with tags (on user request)
def addSingleTrack(artist, title):
    # track_add = network.search_for_track(artist, title)
    track_add = network.get_track(artist, title)
    if track_add is None:
        return None
    r_track = Track(str(track_add.artist), str(track_add.title), track_add.get_url())
    tags = track_add.get_top_tags(10)
    for tag in tags:
        r_tag = Tag.query.filter_by(name=str(tag.item)).first()
        if r_tag is None:
            r_tag = Tag(str(tag.item))
        r_track.tags.append(r_tag)

    # why tags sometimes are empty ? I'm confused
    if len(tags) > 1:
        db.session.add(r_track)
        db.session.commit()
    else:
        print('tags not found ... ')
        return None
    return r_track

if '__main__' == __name__:
    top_tracks = network.get_top_tracks(100) # loading 100 initial top tracks
    for top_track in top_tracks:
        # object for ORM
        r_track = Track(str(top_track.item.artist), str(top_track.item.title), top_track.item.get_url())

        tags = top_track.item.get_top_tags(5)
        for tag in tags:
            r_tag = Tag.query.filter_by(name=str(tag.item)).first()
            if r_tag is None:
                r_tag = Tag(str(tag.item))
            # adding tags to tracks (many to many relation)
            r_track.tags.append(r_tag)
        db.session.add(r_track)
        db.session.commit()
        print('added ', top_track.item)
        time.sleep(1.5)