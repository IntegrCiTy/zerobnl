import json
from zerobnl.kernel import Node


def test_node_zmq_connection():
    node = Node("NODE1", "GRP1", {"a": ["NODE2", "b"]}, ["b"], {"c": 0.5})
    assert node._sub.socket_type == 2
    assert node._sender.socket_type == 8


def test_node_input_map():
    node = Node("NODE1", "GRP1", {"a": ["NODE2", "b"]}, ["b"], {"c": 0.5})
    json_map = json.dumps({"a": ["NODE2", "b"]})
    assert node._inputs_map == json.loads(json_map)


def test_node_creation_logs(caplog):
    Node("NODE1", "GRP1", {"a": ["NODE2", "b"]}, ["b"], {"c": 0.5})
    for record in caplog.records:
        assert record.levelname in ["DEBUG", "INFO"]
