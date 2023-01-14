import os
import re

from Katana import NodegraphAPI


class AlembicLoaderNode(NodegraphAPI.SuperTool):

    ABC_PATH_PARAM = "abcAsset"
    NODE_PREFIX = "node_"
    REGEX_NAME = r"^(.*?)\_v\d{3}.abc"
    REGEX_VERSION = r"(v\d{3})"

    def __init__(self):
        # Categories corresponding to geometry name prefix
        # {category: [geo_names]}
        self.__categories = {}
        # Mapping from geometry name to version to path
        # {geo_name: {version_int: alembic_path}}
        self.__name_to_versions = {}

        self.hideNodegraphGroupControls()
        self.addOutputPort("output")
        self.getParameters().createChildString("location", "/root")
        self.getParameters().createChildString("folderPath", "")

        self.merge_node = NodegraphAPI.CreateNode("Merge", self)
        self.merge_pos = NodegraphAPI.GetNodePosition(self.merge_node)
        self.add_node_reference_param("node_merge", self.merge_node)
        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            self.merge_node.getOutputPortByIndex(0)
        )

    def add_node_reference_param(self, param_name, node):
        """Add name reference to given node for easy access

        :param param_name: (str) Node reference name
        :param node: (NodegraphAPI.GetNode) Object to update
        """
        param = self.getParameter(param_name)
        if not param:
            param = self.getParameters().createChildString(param_name, "")

        param.setExpression("getNode(%r).getNodeName()" % node.getName())

    def disable_node(self, node_name):
        """Disable node that matches name

        :param node_name: (str) Name of node
        """
        node = self.get_ref_node(node_name)
        if node:
            node.setBypassed(True)

    def enable_node(self, node_name):
        """Enable node that matches name

        :param node_name: (str) Name of node
        """
        node = self.get_ref_node(node_name)
        if node:
            node.setBypassed(False)

    def get_ref_node(self, node_name):
        """Get the scene node with the provided name

        :param node_name: Name of node to retrieve
        :return: (NodegraphAPI.GetNode|None) Matching node
        """
        p = self.getParameter(self.NODE_PREFIX + node_name)
        if not p:
            return None

        return NodegraphAPI.GetNode(p.getValue(0))

    def get_category_values(self, category):
        """Get all geometry names for given category

        :param category: Name of category to query
        :return: (list) Geometry names under category
        """
        return self.__categories.get(category, [])

    def get_versions(self, geo_name):
        """Get all versions for given geometry name

        :param geo_name: (str) Name of asset to get versions for
        :return: (list) Versions for geometry asset
        """
        return self.__name_to_versions.get(geo_name)

    def load_alembics(self, directory):
        """Create Alembic_In nodes for all files inside directory

        :param directory: (str) Path to alembic files
        :return: (list) Alembic_In nodes that were created
        """
        nodes = []
        for idx, filename in enumerate(os.listdir(directory)):
            if not filename.endswith(".abc"):
                continue

            fullpath = os.path.join(directory, filename)
            geo_name = re.match(self.REGEX_NAME, filename).groups()[0]
            version = re.split(self.REGEX_VERSION, filename)[1]

            # Store the main category for given geometry
            category = geo_name.split("_")[0]
            names_per_cat = self.__categories.get(category)
            if names_per_cat:
                names_per_cat.append(geo_name)
            else:
                self.__categories.update({category: [geo_name]})

            # Store all available versions for given geometry
            version_dict = self.__name_to_versions.get(geo_name)
            version_num = int(version[1:])
            if version_dict:
                version_dict.update({version_num: fullpath})
                continue

            self.__name_to_versions.update({geo_name: {version_num: fullpath}})
            node_id = len(self.__name_to_versions)

            # Create Alembic_In and update node parameters
            node = NodegraphAPI.CreateNode("Alembic_In", self)
            node.setName(geo_name)

            node.getParameter("name").setValue("/root/world/" + geo_name, 1.0)
            node.getParameter(self.ABC_PATH_PARAM).setValue(fullpath, 1.0)

            node.getOutputPortByIndex(0).connect(
                self.merge_node.addInputPort(str(node_id))
            )
            NodegraphAPI.SetNodePosition(
                node, (0, self.merge_pos[1] + 50 * (node_id + 1))
            )

            self.add_node_reference_param(self.NODE_PREFIX + geo_name, node)
            nodes.append(node)

        return nodes

    def update_version(self, version, geo_name):
        """Update version of the node with matching geometry name

        :param version: (int) Version to switch to
        :param geo_name: (str) Name of active geometry
        """
        version_dict = self.__name_to_versions.get(geo_name)
        node = self.get_ref_node(geo_name)
        if node and version_dict:
            node.getParameter(self.ABC_PATH_PARAM).setValue(
                version_dict.get(version), 1.0
            )
