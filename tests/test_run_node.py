from zerobnl.core import Node

def test_node_zmq_connection():
    node = Node("NODE1", "GRP1", {"a": ["NODE2", "b"]}, ["b"], {"c": 0.5})
    assert node._sub.socket_type == 2
    assert node._sender.socket_type == 8


def test_node_creation_logs(caplog):
    Node("NODE1", "GRP1", {"a": ["NODE2", "b"]}, ["b"], {"c": 0.5})
    for record in caplog.records:
        assert record.levelname in ["DEBUG", "INFO"]


