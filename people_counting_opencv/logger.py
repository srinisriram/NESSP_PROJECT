import logging


class Logger(object):
    __logger = None
    __ch = None

    @classmethod
    def set_log_level(cls, level=logging.INFO):
        if not cls.__logger:
            # create logger
            cls.__logger = logging.getLogger('people_counter')
            print("setting logging level to {}.".format(level))
            cls.__logger.setLevel(level)

            # create console handler
            cls.__ch = logging.StreamHandler()
            cls.__ch.setLevel(level)

            # create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(filename)s - %(lineno)d %(levelname)s - %(message)s')

            # add formatter to ch
            cls.__ch.setFormatter(formatter)

            # add ch to logger
            cls.__logger.addHandler(cls.__ch)

    @classmethod
    def logger(cls):
        if not cls.__logger:
            cls.set_log_level()
        return cls.__logger
