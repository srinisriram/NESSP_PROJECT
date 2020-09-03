# import the necessary packages

class HumanTracker:
    def __init__(self, objectID, centroid):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]

        # initialize a lists to store the timestamp and
        # position of the object at various points
        self.timestamp_list = []

        # initialize two booleans, (1) used to indicate if the
        # object's speed has already been estimated or not, and (2)
        # used to indicate if the object's speed has been logged or
        # not
        self.estimated = False
        self.logged = False

        # initialize the direction of the object
        self.direction = None
