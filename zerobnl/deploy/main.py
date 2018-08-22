from time import time

from zerobnl.edit import GraphCreator
from zerobnl.deploy import SimResultsGetter
from zerobnl.deploy.compose import *


class Simulator:
    """

    """

    def __init__(self):
        self.edit = GraphCreator()
        self.results = SimResultsGetter()

    def _deploy_files_and_folders(self):
        logger.info("Starting the simulation's deployment...")
        orch_folder = create_sub_folder_in_temporary_folder(ORCH_FOLDER)

        dump_dict_to_json_in_folder(orch_folder, self.edit.group_sequence, SEQUENCE_FILE)
        dump_dict_to_json_in_folder(orch_folder, self.edit.steps, STEPS_FILE)

        # add orch.py to orchestrator's sub-folder
        this_dir, _ = os.path.split(__file__)
        copy_files_to_folder(orch_folder, os.path.join(this_dir, "..", "core", "orch.py"))

        copy_files_to_folder(orch_folder, os.path.join(this_dir, "..", "..", "Dockerfiles", "Dockerfile"))

        logger.debug("ORCH sub-folder is ready")

        nodes = self.edit.nodes

        for node_name, node in nodes.iterrows():
            # Create the node's sub-folder
            node_folder = create_sub_folder_in_temporary_folder(node_name)

            if node["dockerfile"]:
                copy_files_to_folder(node_folder, node["dockerfile"])

            # Create the node's init_values json file -> {"attr": value}
            dump_dict_to_json_in_folder(node_folder, node["init_values"], INIT_VALUES_FILE)

            # Create the node's attributes json file -> {"a": ["NODE", "b"]}
            attr_to_set = {
                l["set_attr"]: [l["get_node"], l["get_attr"]]
                for _, l in self.edit.links.iterrows()
                if l["set_node"] == node_name
            }

            attr_data = {"to_set": attr_to_set, "to_get": node["to_get"]}
            dump_dict_to_json_in_folder(node_folder, attr_data, ATTRIBUTE_FILE)

            # Copy additional files to the node's sub-folder
            copy_files_to_folder(node_folder, node["wrapper"], *node["files"])
        logger.debug("Nodes sub-folder are ready")

    def run_simulation(self):
        clean_temp_folder()
        self._deploy_files_and_folders()

        run_redis()

        groups_to_compose = {
            grp: [
                (node, os.path.basename(self.edit.nodes.loc[node, "wrapper"])) for node in nodes
                if not self.edit.nodes.loc[node]["is_local"]
            ]
            for grp, nodes in self.edit.groups.items()
        }

        os.environ["ZMQ_SUB_ADDRESS"] = "tcp://{}:{}".format(DOCKER_HOST, port_pub_sub)
        os.environ["ZMQ_PUSH_ADDRESS"] = "tcp://{}:{}".format(DOCKER_HOST, port_push_pull)

        for grp, nodes in self.edit.groups.items():
            for node_name in nodes:
                if self.edit.nodes.loc[node_name]["is_local"]:
                    node = self.edit.nodes.loc[node_name]
                    logger.info("{} TO RUN LOCALLY:".format(node_name))
                    logger.info("> {} {} {}".format(
                        os.path.join(TEMP_FOLDER, node_name.lower(), os.path.basename(node["wrapper"])),
                        node_name,
                        grp
                    ))

        create_yaml_docker_compose(groups_to_compose)
        logger.debug("docker-compose.yaml file created, ready to launch simulation")
        logger.info("Starting simulation...")
        start = time()
        run_docker_compose()
        stop = time() - start
        logger.info("Simulation finished in {} min and {} sec".format(int(stop // 60), int(round(stop % 60, 0))))
