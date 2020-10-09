from human_tracker import HumanTracker
from constants import COLUMN_SAMPLE_POINTS_LIST, Direction, COLUMN, TIMEOUT_FOR_TRACKER, DEMARCATION_LINE
from logger import Logger
import cv2
from datetime import datetime
from human_validator import HumanValidator


class HumanTrackerHandler:
    human_tracking_dict = {}

    @classmethod
    def draw_id_centroid_on_output_frame(cls, frame, centroid, objectID):
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10)
                    , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4,
                   (0, 255, 0), -1)

    @classmethod
    def yield_a_human_tracker_object(cls, objects):

        for (objectID, centroid) in objects.items():
            # check to see if a trackable object exists for the current
            # object ID
            human_tracker_object = cls.human_tracking_dict.get(objectID, None)

            # if there is no existing trackable object, create one
            if not human_tracker_object:
                Logger.logger().debug("Creating a new speed tracker object with object id = {}.".format(objectID))
                human_tracker_object = HumanTracker(objectID, centroid)
                cls.human_tracking_dict[objectID] = human_tracker_object

            else:
                human_tracker_object.centroids.append(centroid)
            human_tracker_object.timestamp_list.append(datetime.now())
            yield human_tracker_object, objectID, centroid

    @classmethod
    def clear_object_from_speed_tracking_dict(cls, objectID):
        del (cls.human_tracking_dict[objectID])

    @classmethod
    def handle_the_case_where_grace_time_for_tracking_is_over(cls, now, human_tracker_object, keep_dict_items):
        """
        This method handles the case where the grace time (TIMEOUT_FOR_TRACKER) for the tracker object is over.
        :param now: timestamp
        :param human_tracker_object: Instance of type HumanTracker.
        :param keep_dict_items: Preserve dictionary items. (for debug purpose)
        :return:
        """
        if human_tracker_object.estimated and human_tracker_object.logged and not keep_dict_items:
            # Delete this object from speed tracking dict.
            Logger.logger().debug("Deleting objectId {} from the human_tracking_dict.".format(
                human_tracker_object.objectID))
            cls.clear_object_from_speed_tracking_dict(human_tracker_object.objectID)
        else:
            Logger.logger().debug("Computing direction for objectId {} because there are no recorded"
                                  " movements for this object in human_tracking_dict.".format(
                human_tracker_object.objectID))
            cls.compute_direction(human_tracker_object)
            human_tracker_object.estimated = True
        # Finally log it.
        Logger.logger().debug("Perform logging for objectId {} found the human_tracking_dict.".format(
            human_tracker_object.objectID))
        HumanValidator.validate_column_movement(human_tracker_object, now, None,
                                                human_tracker_object.objectID)

    @classmethod
    def compute_direction_for_dangling_object_ids(cls, keep_dict_items=False):
        """
        This method computes direction for dangling objects found in speed_tracking_dict.
        This can happen when the person was tracked only at a few sampling points (column traversal).
        :return:
        """
        for object_id, human_tracker_object in cls.human_tracking_dict.copy().items():
            now = datetime.now()
            duration = now - human_tracker_object.timestamp_list[-1]
            if duration.total_seconds() > TIMEOUT_FOR_TRACKER:
                cls.handle_the_case_where_grace_time_for_tracking_is_over(now, human_tracker_object, keep_dict_items)

    @classmethod
    def compute_direction(cls, trackable_object):
        """
        Compute the direction of the person movement.
        :param trackable_object: object
        :return:
        """
        direction = trackable_object.centroids[-1][COLUMN] - trackable_object.centroids[0][COLUMN]
        if direction > 0:
            trackable_object.direction = Direction.ENTER
        else:
            trackable_object.direction = Direction.EXIT

    @classmethod
    def record_movement(cls, trackable_object):
        if not trackable_object.estimated:
            cls.compute_direction(trackable_object)
