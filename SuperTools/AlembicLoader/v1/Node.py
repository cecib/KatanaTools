import os
import re

from Katana import NodegraphAPI


class AlembicLoaderNode(NodegraphAPI.SuperTool):

    REGEX_NAME = r"^(.*?)\_v\d{3}.abc"
    REGEX_VERSION = r"(v\d{3})"

    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addOutputPort("output")

        self.getParameters().createChildString("location", "/root")
        self.getParameters().createChildString(
            "folderPath",
            "C:/Users/Ceci/Documents/_jobs/spinvfx/katana_test_products/products/",
        )

        self.merge_node = NodegraphAPI.CreateNode("Merge", self)
        self.merge_pos = NodegraphAPI.GetNodePosition(self.merge_node)
        self.add_node_reference_param("node_merge", self.merge_node)
        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            self.merge_node.getOutputPortByIndex(0)
        )
        # Mapping from geometry name to version to path
        # {geo_name: {version_int: alembic_path}}
        self.__name_to_versions = {}
        # Categories corresponding to 1st part of geometry name
        # {category: [geo_names]}
        self.__categories = {}

    def add_node_reference_param(self, param_name, node):
        param = self.getParameter(param_name)
        if not param:
            param = self.getParameters().createChildString(param_name, "")

        param.setExpression("getNode(%r).getNodeName()" % node.getName())

    def disable_node(self, node_name):
        node = self.get_ref_node(node_name)
        if node:
            node.setBypassed(True)

    def enable_node(self, node_name):
        node = self.get_ref_node(node_name)
        if node:
            node.setBypassed(False)

    def get_ref_node(self, node_name):
        p = self.getParameter("node_" + node_name)
        if not p:
            return None

        return NodegraphAPI.GetNode(p.getValue(0))

    def get_categories(self):
        return self.__categories

    def get_versions(self, geo_name):
        return self.__name_to_versions.get(geo_name)

    def load_alembics(self, directory):
        nodes = []
        for idx, filename in enumerate(os.listdir(directory)):
            if not filename.endswith(".abc"):
                continue

            fullpath = os.path.join(directory, filename)
            geo_name = re.match(self.REGEX_NAME, filename).groups()[0]
            version = re.split(self.REGEX_VERSION, filename)[1]

            # Store all available versions for given geometry
            version_dict = self.__name_to_versions.get(geo_name)
            version_num = int(version[1:])
            if version_dict:
                version_dict.update({version_num: fullpath})
                continue

            self.__name_to_versions.update({geo_name: {version_num: fullpath}})
            self.__categories.add(geo_name.split("_"[0]))
            node_id = len(self.__name_to_versions)

            # Create Alembic_In and update node parameters
            node = NodegraphAPI.CreateNode("Alembic_In", self)
            node.setName(geo_name)

            node.getParameter("name").setValue("/root/world/" + geo_name, 1.0)
            node.getParameter("abcAsset").setValue(fullpath, 1.0)

            node.getOutputPortByIndex(0).connect(
                self.merge_node.addInputPort(str(node_id))
            )
            NodegraphAPI.SetNodePosition(
                node, (0, self.merge_pos[1] + 50 * (node_id + 1))
            )

            self.add_node_reference_param("node_" + geo_name, node)
            nodes.append(node)

        return nodes

    def update_version(self, version, geo_name):
        version_dict = self.__name_to_versions.get(geo_name)
        node = self.get_ref_node(geo_name)
        if not node or not version_dict:
            return
        node.getParameter("abcAsset").setValue(version_dict.get(version), 1.0)
