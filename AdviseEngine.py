from api import Tag, Track
from scipy import spatial
from MusicMining import addSingleTrack

class AdviseEngine:
    def __init__(self, db):
        self.db = db
        self.debug = True

    def getAdvise(self, artist, title):
        # check if track exists
        track_in = Track.query.filter_by(artist=artist, title=title).first()
        # try to get track from radio API
        if track_in is None:
            # upload track info if does not exist
            track_in = addSingleTrack(artist, title)
            # no such track :(
            if track_in is None:
                return None

        # get user favorite tags
        user_tags = ['rock', 'electronic', 'seen live', 'alternative', 'indie', 'pop', 'metal', 'jazz']

        # create feature vector and features matrix
        self.getFeaturesList()
        self.getFeaturesMatrix()
        self.applyUserTags(user_tags)
        # visualization for feature matrix
        if self.debug:
            print(self.features_matrix)

        # looking for nearest by cosine similarity
        best_distance = 2
        best_id = None
        for key, value in self.features_matrix.items():
            # omitting current track
            if key == track_in.id:
                continue
            current_distance = spatial.distance.cosine(self.features_matrix[track_in.id], value)
            if current_distance < best_distance:
                best_distance = current_distance
                best_id = key
        # best distance shown
        if self.debug:
            print(best_distance)

        return Track.query.get(best_id)

    # get features
    def getFeaturesList(self):
        features = Tag.query.with_entities(Tag.name).order_by(Tag.id).all()
        self.features = list(map(lambda x: x[0], features))  # removing tuples
        return self.features

    # get all tracks with precalculated feature vectors
    def getFeaturesMatrix(self):
        self.features_matrix = dict()
        for tr in Track.query.all():
            tr_id = tr.id
            tr_feature = [0] * len(self.features)
            for t in tr.tags:
                 tr_feature[self.features.index(t.name)] = 1
            self.features_matrix[tr_id] = tr_feature
        return self.features_matrix

    # set additional weight for user tags
    def applyUserTags(self, user_tags):
        more_weight_indexes = []
        for u_tag in user_tags:
            if u_tag in self.features:
                more_weight_indexes.append(self.features.index(u_tag))
        # set user tags weight twice bigger
        for w in more_weight_indexes:
            for key, val in self.features_matrix.items():
                val[w] = val[w]*2