import os
import subprocess


def test_execute_node_help_return_help():
    this_dir, _ = os.path.split(__file__)
    full_cmd = "python {} -h".format(os.path.join(this_dir, "..", "zerobnl", "core", "node.py"))
    stdout = subprocess.check_output(full_cmd, shell=True)
    assert ">>> ZEROBNL node wrapper command <<<" in stdout.decode("utf-8")


def test_execute_node():
    this_dir, _ = os.path.split(__file__)
    full_cmd = "python {} {} {}".format(os.path.join(this_dir, "..", "zerobnl", "core", "node.py"), "NODE0", "GRP1")
    # stdout = subprocess.check_output(full_cmd, shell=True, timeout=1)
    # assert ">>> ZEROBNL node wrapper command <<<" in stdout.decode("utf-8")
