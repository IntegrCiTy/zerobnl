import os
from zerobnl.core import Node


def test_zmq_connection():
    node = Node("NODE1", "GRP1", os.environ["ZMQ_SUB_ADDRESS"], os.environ["ZMQ_PUSH_ADDRESS"], {}, [])
