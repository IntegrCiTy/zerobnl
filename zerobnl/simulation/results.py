import redis
import pandas as pd

from zerobnl.config import *
from zerobnl.logs import logger
from zerobnl.utils import decode_pickle_float, load_from_redis_key

from zerobnl.simulation import CoSimDeploy


class CoSimResults(CoSimDeploy):
    def __init__(self):
        super().__init__()
        self.redis = None

    def connect_to_results_db(self):
        self.redis = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)

    def get_list_of_available_results(self):
        keys = [k.decode("utf-8") for k in self.redis.keys() if "time" not in str(k)]
        return pd.DataFrame([k.split("||") for k in keys], columns=["IN/OUT", "Node", "Attribute"])

    def get_results_by_pattern(self, pattern):
        """
        Allow to get results from a given name pattern
        :param pattern: the pattern used to query the Redis DB
        :return: a dict mapping results name with pandas.Series() of values or dict of df if stored value are df
        """
        matching_keys = [key.decode("utf-8") for key in self.redis.keys(pattern)]
        logger.debug("KEYS: {}".format(matching_keys))
        matching_keys = [key for key in matching_keys if "time" not in key]
        for node, attr in [(k.split("||")[-2], k.split("||")[-1]) for k in matching_keys]:
            logger.info("Matching results: {} - {}".format(node, attr))

        res = {key: load_from_redis_key(self.redis, key) for key in matching_keys}

        for key, value in res.items():
            if type(value[values.keys()[0]]) is float:
                value.keys
        #     index = pd.to_datetime(index)
        #
        #     # TODO: adapt to df
        #     res[key_v] = pd.Series(value, index=index)

        return res
