import os
import subprocess


def test_execute_node_help_return_help():
    full_cmd = "python {} -h".format(os.path.join("zerobnl", "core", "node.py"))
    stdout = subprocess.check_output(full_cmd, shell=True)
    assert ">>> ZEROBNL node wrapper command <<<" in stdout.decode("utf-8")


def test_execute_node_without_map_and_outputs():
    full_cmd = "python {} NODE1 GRP1 {} {}".format(
        os.path.join("zerobnl", "core", "node.py"),
        os.environ["ZMQ_SUB_ADDRESS"],
        os.environ["ZMQ_PUSH_ADDRESS"],
    )
    stdout = subprocess.check_output(full_cmd, shell=True)
    assert stdout.decode("utf-8") is ""


def test_execute_node():
    full_cmd = "python {} NODE1 GRP1 {} {} {} {}".format(
        os.path.join("zerobnl", "core", "node.py"),
        os.environ["ZMQ_SUB_ADDRESS"],
        os.environ["ZMQ_PUSH_ADDRESS"],
        {"a": ("NODE2", "b")},
        ["b", "c"]
    )
    stdout = subprocess.check_output(full_cmd, shell=True)
    assert stdout.decode("utf-8") is ""
