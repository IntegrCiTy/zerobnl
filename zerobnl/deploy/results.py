import pandas as pd
import redis

from zerobnl.logs import logger
from zerobnl.config import *


class SimResultsGetter:
    """
    Class gathering methods allowing the collection of results
    """

    def __init__(self):
        self.redis = None

    def connect_to_results_db(self):
        """
        Instantiate connection with Redis DB

        :return: nothing :)
        """
        self.redis = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)
        logger.info("Connected to Redis DB")

    @property
    def list_of_available_results(self):
        """
        :return: a pandas.DataFrame() describing the available results by nodes
        """
        keys = [k.decode("utf-8") for k in self.redis.keys() if "time" not in str(k)]
        return pd.DataFrame([k.split("||") for k in keys], columns=["IN/OUT", "Node", "Attribute"])

    def get_results_by_pattern(self, pattern):
        """
        Allow to get results from a given name pattern

        :param pattern: the pattern used to query the Redis DB
        :return: a dict mapping results name with pandas.Series() of values
        """
        matching_keys = [key.decode("utf-8") for key in self.redis.keys(pattern)]
        for node, attr in [(k.split("||")[-2], k.split("||")[-1]) for k in matching_keys if "time" not in k]:
            logger.info("Matching results: {} - {}".format(node, attr))

        list_of_value = sorted([key for key in matching_keys if "time" not in key])
        list_of_index = sorted([key for key in matching_keys if "time" in key])

        res = {}

        for (key_v, key_t) in zip(list_of_value, list_of_index):
            value = list(map(float, self.redis.lrange(key_v, 0, -1)))
            index = [b.decode("utf-8") for b in self.redis.lrange(key_t, 0, -1)]

            index = pd.to_datetime(index)

            res[key_v] = pd.Series(value, index=index)

        return res
