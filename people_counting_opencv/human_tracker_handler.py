from human_tracker import HumanTracker
from constants import COLUMN_SAMPLE_POINTS_LIST, Direction, COLUMN, TIMEOUT_FOR_TRACKER
from logger import Logger
import cv2
from datetime import datetime


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
                Logger.logger().info("Creating a new speed tracker object with object id = {}.".format(objectID))
                human_tracker_object = HumanTracker(objectID, centroid)
                cls.human_tracking_dict[objectID] = human_tracker_object
                if len(cls.human_tracking_dict) > 100:
                    cls.human_tracking_dict.clear()
            else:
                human_tracker_object.centroids.append(centroid)
            yield human_tracker_object, objectID, centroid

    @classmethod
    def update_column_index_movement(cls, frame, human_tracked_object, objectID, centroid, ts):
        cls.record_movement(human_tracked_object, centroid, ts)
        # store the trackable object in our dictionary
        cls.human_tracking_dict[objectID] = human_tracked_object
        cls.draw_id_centroid_on_output_frame(frame, centroid, objectID)
        cls.compute_direction_for_dangling_object_ids()

    @classmethod
    def clear_object_from_speed_tracking_dict(cls, objectID):
        del (cls.human_tracking_dict[objectID])

    @classmethod
    def compute_direction_for_dangling_object_ids(cls):
        for object_id, human_tracker_object in cls.human_tracking_dict.items():
            if human_tracker_object.estimated or len(human_tracker_object.timestamp_list) <= 1:
                continue
            now = datetime.now()
            duration = now - human_tracker_object.timestamp_list[-1]
            if duration.total_seconds() > TIMEOUT_FOR_TRACKER:
                cls.compute_direction(0, human_tracker_object.current_index - 1, human_tracker_object)
                human_tracker_object.estimated = True

    @classmethod
    def record_column_traversed_index(cls, trackable_object, centroid, ts):
        if trackable_object.current_index == -1:
            # initialize it for the first time to 0.
            trackable_object.current_index = 0
        elif trackable_object.current_index == len(COLUMN_SAMPLE_POINTS_LIST):
            error_str = "Unable to find an empty slot in the trackable_object timestamp."
            Logger.logger().error(error_str)
            raise ValueError

        if centroid[COLUMN] > COLUMN_SAMPLE_POINTS_LIST[trackable_object.current_index]:
            Logger.logger().debug("Recording timestamp and centroid at column {}".format(
                COLUMN_SAMPLE_POINTS_LIST[trackable_object.current_index]))
            trackable_object.timestamp_list.append(ts)
            trackable_object.position_list.append(centroid[COLUMN])
            trackable_object.current_index += 1

    @classmethod
    def compute_direction(cls, start, end, trackable_object):
        """
        Compute the direction of the person movement.
        If the diff between the position list (end - start) is +ve then the person entered into the
        building else the person exited the building.
        :param start: int
        :param end: int
        :param trackable_object: object
        :return:
        """
        Logger.logger().debug("position_list={}".format(trackable_object.position_list))
        d = trackable_object.position_list[end] - trackable_object.position_list[start]
        if d == 0:
            Logger.logger().debug("Invalid position for column traversal found.")
            return

        if d > 0:
            trackable_object.direction = Direction.ENTER
        else:
            trackable_object.direction = Direction.EXIT

    @classmethod
    def record_movement(cls, trackable_object, centroid, ts):
        if not trackable_object.estimated:
            cls.record_column_traversed_index(trackable_object, centroid, ts)
            # check to see if the person has gone past the last sampling point and
            # set the estimated to True.
            if trackable_object.current_index == len(COLUMN_SAMPLE_POINTS_LIST):
                cls.compute_direction(0, trackable_object.current_index - 1, trackable_object)
                trackable_object.estimated = True
