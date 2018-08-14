from zerobnl.edit.interactions import GraphCreator
from zerobnl.deploy.compose import *


class Simulator:
    """

    """

    def __init__(self):
        self.edit = GraphCreator()

    def _deploy_files_and_folders(self):
        logger.info("Starting the deployment of the simulation...")
        orch_folder = create_sub_folder_in_temporary_folder(ORCH_FOLDER)

        # TODO: Adapt json files to new orchestrator
        dump_dict_to_json_in_folder(orch_folder, self.edit.interaction_graph, INTERACTION_GRAPH_FILE)
        dump_dict_to_json_in_folder(
            orch_folder, {"steps": self.edit.steps, "sequence": self.edit.sequence}, STEP_SEQUENCE_FILE
        )

        # add orch.py to orchestrator's sub-folder
        this_dir, _ = os.path.split(__file__)
        copy_files_to_folder(orch_folder, os.path.join(this_dir, "..", "core", "orch.py"))

        nodes = self.edit.nodes

        for node_name, node in nodes.iterrows():
            # Create the node's sub-folder
            node_folder = create_sub_folder_in_temporary_folder(node_name)

            # Create the node's init_values json file
            dump_dict_to_json_in_folder(node_folder, node["init_values"], INIT_VALUES_FILE)

            # TODO: Create needed attribute file from graph and meta-model
            # Create the node's attributes json file
            dump_dict_to_json_in_folder(node_folder, node["init_values"], ATTRIBUTE_FILE)

            # Copy additional files to the node's sub-folder
            copy_files_to_folder(node_folder, *node["files"])
