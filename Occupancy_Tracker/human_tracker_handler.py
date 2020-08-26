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
            yield human_tracker_object, objectID, centroid

    @classmethod
    def update_column_index_movement(cls, frame, human_tracked_object, objectID, centroid, ts):
        cls.record_movement(human_tracked_object, centroid, ts)
        # store the trackable object in our dictionary
        cls.human_tracking_dict[objectID] = human_tracked_object
        cls.draw_id_centroid_on_output_frame(frame, centroid, objectID)

    @classmethod
    def clear_object_from_speed_tracking_dict(cls, objectID):
        del (cls.human_tracking_dict[objectID])

    @classmethod
    def handle_zero_time_stamp_list(cls, human_tracker_object):
        """
        This method is invoked when there is no timestamp recorded for this tracker.
        In this case, this method initially computes the current time and stores it in empty_recorded_timestamp.
        Since the grace period (TIMEOUT_FOR_TRACKER) is already over, this method deletes the tracker object
        from the speed_tracking_dict.
        :param human_tracker_object: Instance of type HumanTracker.
        :return:
        """
        if human_tracker_object.empty_recorded_timestamp:
            now = datetime.now()
            duration = now - human_tracker_object.empty_recorded_timestamp
            if duration.total_seconds() > TIMEOUT_FOR_TRACKER:
                Logger.logger().debug("Deleting objectId {} for empty timestamp "
                                     "from the human_tracking_dict.".format(
                                     human_tracker_object.objectID))
                cls.clear_object_from_speed_tracking_dict(human_tracker_object.objectID)
        else:
            human_tracker_object.empty_recorded_timestamp = datetime.now()

    @classmethod
    def handle_the_case_where_grace_time_for_tracking_is_over(cls, now, human_tracker_object,
                                                              send_receive_message_instance):
        """
        This method handles the case where the grace time (TIMEOUT_FOR_TRACKER) for the tracker object is over.
        :param now: timestamp
        :param human_tracker_object: Instance of type HumanTracker.
        :param send_receive_message_instance: Instance of type SendReceiveMessages
        :return:
        """
        if human_tracker_object.estimated and human_tracker_object.logged:
            # Delete this object from speed tracking dict.
            Logger.logger().debug("Deleting objectId {} from the human_tracking_dict.".format(
                human_tracker_object.objectID))
            cls.clear_object_from_speed_tracking_dict(human_tracker_object.objectID)
        else:
            Logger.logger().debug("Computing direction for objectId {} because there are no recorded"
                                 " movements for this object in human_tracking_dict.".format(
                human_tracker_object.objectID))
            cls.compute_direction(0, human_tracker_object.current_index - 1, human_tracker_object)
            human_tracker_object.estimated = True
        # Finally log it.
        Logger.logger().debug("Perform logging for objectId {} found the human_tracking_dict.".format(
            human_tracker_object.objectID))
        HumanValidator.validate_column_movement(human_tracker_object, now, None,
                                                human_tracker_object.objectID,
                                                send_receive_message_instance)

    @classmethod
    def compute_direction_for_dangling_object_ids(cls, send_receive_message_instance):
        """
        This method computes direction for dangling objects found in speed_tracking_dict.
        This can happen when the person was tracked only at a few sampling points (column traversal).
        :param send_receive_message_instance: Instance of type SendReceiveMessages
        :return:
        """
        for object_id, human_tracker_object in cls.human_tracking_dict.copy().items():
            if len(human_tracker_object.timestamp_list) == 0:
                cls.handle_zero_time_stamp_list(human_tracker_object)
                return
            now = datetime.now()
            duration = now - human_tracker_object.timestamp_list[-1]
            if duration.total_seconds() > TIMEOUT_FOR_TRACKER:
                cls.handle_the_case_where_grace_time_for_tracking_is_over(now, human_tracker_object,
                                                                          send_receive_message_instance)

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
            Logger.logger().debug("Found a case where there is only one entry in the tracker position list.")
            if trackable_object.position_list[end] <= DEMARCATION_LINE:
                Logger.logger().info("Since {} is less than or equal to {}, assuming that the person is entering".
                                     format(trackable_object.position_list[end], DEMARCATION_LINE))
                trackable_object.direction = Direction.ENTER
            else:
                Logger.logger().info("Since {} is greater than {}, assuming that the person is exiting".format(
                    trackable_object.position_list[end], DEMARCATION_LINE))
                trackable_object.direction = Direction.EXIT

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
