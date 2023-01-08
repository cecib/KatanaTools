import os
import re

from Katana import NodegraphAPI


class AlembicLoaderNode(NodegraphAPI.SuperTool):

    REGEX_NAME = r"^(.*?)\_v\d{3}.abc"
    REGEX_VERSION = r"(v\d{3})"

    def __init__(self):
        self.hideNodegraphGroupControls()

        self.addOutputPort("output")

        self.getParameters().createChildString('location', '/root')
        self.getParameters().createChildString('folderPath', r'C:\Users\Ceci\Documents\_jobs\spinvfx\katana_test_products\products')

        self.merge_node = NodegraphAPI.CreateNode('Merge', self)
        self.add_node_reference_param('node_merge', self.merge_node)

        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            self.merge_node.getOutputPortByIndex(0))

        self.__abc_nodes = {}    # {name:[1,2,5]}

    def get_latest_version(self, node_name):
        pass

    def add_node_reference_param(self, param_name, node):
        param = self.getParameter(param_name)   # 'node_' + node_name
        if not param:
            param = self.getParameters().createChildString(param_name, '')

        param.setExpression('getNode(%r).getNodeName()' % node.getName())

    def disable_node(self, node_name):
        node = self.get_ref_node(node_name)
        if node:
            node.setBypassed(True)

    def enable_node(self, node_name):
        node = self.get_ref_node(node_name)
        if node:
            node.setBypassed(False)

    def get_ref_node(self, node_name):
        p = self.getParameter('node_' + node_name)
        if not p:
            return None

        return NodegraphAPI.GetNode(p.getValue(0))

    def load_alembics(self, rootdir):
        alembic_nodes = []
        merge_pos = NodegraphAPI.GetNodePosition(self.merge_node)
        for root, subdirs, files in os.walk(rootdir):
            for idx, filename in enumerate(files):

                if not filename.endswith(".abc"):
                    continue

                fullpath = root + os.sep + filename

                name = re.match(AlembicLoaderNode.REGEX_NAME, filename).groups()[0]
                version = re.split(AlembicLoaderNode.REGEX_VERSION, filename)[1]

                node = NodegraphAPI.CreateNode("Alembic_In", self)
                node_name = name + "_" + str(version)
                node.setName(node_name)

                node.getParameter('name').setValue('/root/world/' + name, 1.0)
                node.getParameter('abcAsset').setValue(fullpath, 1.0)

                root_param = node.getParameters()
                studio_params = root_param.createChildGroup("studio")
                studio_params.createChildNumber("version", int(version[1:]))

                merge_port = self.merge_node.addInputPort(name)
                node.getOutputPortByIndex(0).connect(merge_port)
                NodegraphAPI.SetNodePosition(node, (0, merge_pos[1]+50*(idx+1)))

                version_value = int(version[1:])
                current_versions = self.__abc_nodes.get(name)
                if current_versions:
                    current_versions.append(version_value)
                else:                       # cube_geom
                    self.__abc_nodes.update({name: [version_value]})
                                                        # cube_geom_v0001
                self.add_node_reference_param('node_' + node_name, node)
                # node_cube_geom_v0001

                alembic_nodes.append(node)

        return alembic_nodes
