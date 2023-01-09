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
        self.getParameters().createChildString("folderPath", "")

        self.merge_node = NodegraphAPI.CreateNode("Merge", self)
        self.merge_pos = NodegraphAPI.GetNodePosition(self.merge_node)
        self.add_node_reference_param("node_merge", self.merge_node)
        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            self.merge_node.getOutputPortByIndex(0)
        )
        self.__name_to_versions = {}

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

    def get_versions(self, geo_name):
        return self.__name_to_versions.get(geo_name)

    def load_alembics(self, directory):
        for idx, filename in enumerate(os.listdir(directory)):
            if not filename.endswith(".abc"):
                continue

            geo_name = re.match(self.REGEX_NAME, filename).groups()[0]
            version = re.split(self.REGEX_VERSION, filename)[1]

            node = NodegraphAPI.CreateNode("Alembic_In", self)
            node_name = geo_name + "_" + str(version)
            node.setName(node_name)

            # Update Alembic_In node parameters
            node.getParameter("name").setValue("/root/world/" + geo_name, 1.0)
            node.getParameter("abcAsset").setValue(
                os.path.join(directory, filename), 1.0
            )
            studio_params = node.getParameters().createChildGroup("studio")
            studio_params.createChildNumber("geoName", geo_name)

            node.getOutputPortByIndex(0).connect(self.merge_node.addInputPort(geo_name))
            NodegraphAPI.SetNodePosition(node, (0, self.merge_pos[1] + 50 * (idx + 1)))

            # Store all available versions for given geometry
            version_num = int(version[1:])
            versions = self.__name_to_versions.get(geo_name)
            if versions:
                versions.append(version_num)
            else:
                self.__name_to_versions.update({geo_name: [version_num]})

            self.add_node_reference_param("node_" + node_name, node)
            yield node

    def update_version(self, curr_version, geo_name, is_enabled):
        name_prefix = geo_name + "_v"
        for version in self.__name_to_versions.get(geo_name):
            if curr_version == version and is_enabled:
                self.enable_node(name_prefix + str(curr_version).zfill(3))
            else:
                self.disable_node(name_prefix + str(version).zfill(3))
