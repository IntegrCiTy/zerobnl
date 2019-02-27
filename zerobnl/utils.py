import pickle

def save_to_redis(client, name, attr, opt, value, time):
    key = "{}||{}||{}".format(opt, name, attr)
    client.rpush(key, value)
    client.rpush(key + "||time", str(time))

def load_from_redis(client, name, attr, opt):
    key = "{}||{}||{}".format(opt, name, attr)
    values = client.lrange(key, 0, -1)
    stamps = client.lrange(key+"||time", 0, -1)
    return {i.decode("utf-8"): decode_pickle_float(val) for i, val in zip(values, stamps)}

def decode_pickle_float(value):
    try:
        return float(value.decode("utf-8"))
    except UnicodeDecodeError:
        return pickle.loads(value)

def encode_pickle_float(value):
    if isinstance(value, (int, float)):
        return float(value)
    else:
        return pickle.dumps(value)
