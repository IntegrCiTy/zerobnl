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
        matching_keys = [key for key in matching_keys if "time" not in key]
        for node, attr in [(k.split("||")[-2], k.split("||")[-1]) for k in matching_keys]:
            logger.info("Matching results: {} - {}".format(node, attr))

        raw_res = {key: load_from_redis_key(self.redis, key) for key in matching_keys}
        res = {}

        for key, value in raw_res.items():
            if type(value[1][0]) is pd.DataFrame:
                dfs = []
                for i, df in zip(value[0], value[1]):
                    df["time"] = i
                    dfs.append(df)
                mdf = pd.concat(dfs).reset_index()
                res[key] = mdf.set_index(['time', 'index'])
            else:
                res[key] = pd.Series(value[1], index=pd.to_datetime(value[0]))
        return res
