from docopt import docopt

# This doc is used to make the orchestrator callable by command line and gather easily all the given parameters
doc = """>>> ZEROBNL orchestrator command <<<
Usage:
    node.py (<name> <group>) [--cmd=CMD]
    node.py -h | --help
    node.py --version
Options
    -h --help   show this
    --version   show version
    --cmd       optional list of commands to run wrapper
"""


class Orch:
    """docstring for Orch"""
    def __init__(self, arg):
        self.arg = arg
