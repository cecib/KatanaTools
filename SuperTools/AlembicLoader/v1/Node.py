import os
import logging
import re

from Katana import (
    NodegraphAPI,
    AssetAPI,
)
from . import ScriptActions

log = logging.getLogger('AlembicLoaderNode')

regex_name = r"^(.*?)\_v\d{3}.abc"
regex_version = r"(v\d{3})"
location = r'C:\Users\Ceci\Documents\_jobs\spinvfx\katana_test_products\products'

#this class should have all katana and nodegraphAPI stuff
#

class AlembicLoaderNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()

        self.addOutputPort("output")

        self.getParameters().createChildString('location', '/root')
        self.getParameters().createChildString('folderPath', location)

        self.mergeNode = NodegraphAPI.CreateNode('Merge', self)
        ScriptActions.AddNodeReferenceParam(self, 'node_merge', self.mergeNode)

        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            self.mergeNode.getOutputPortByIndex(0))

        self.__abcNodes = {}    # {name:[1,2,5]}

    def reloadAlembic(self):
        pass


    def loadAlembics(self, rootdir):
        alembic_nodes = []
        mergePos = NodegraphAPI.GetNodePosition(self.mergeNode)
        for root, subdirs, files in os.walk(rootdir):
            for idx, filename in enumerate(files):

                if not filename.endswith(".abc"):
                    continue

                fullpath = root + os.sep + filename

                name = re.match(regex_name, filename).groups()[0]
                version = re.split(regex_version, filename)[1]

                node = NodegraphAPI.CreateNode("Alembic_In", self)
                node.setName(name+str(int(version[1:])))

                node.getParameter('name').setValue('/root/world/' + name, 1.0)
                node.getParameter('abcAsset').setValue(fullpath, 1.0)

                rootParam = node.getParameters()
                studioParams = rootParam.createChildGroup("studio")
                studioParams.createChildNumber("version", int(version[1:]))

                mergePort = self.mergeNode.addInputPort(name)
                node.getOutputPortByIndex(0).connect(mergePort)
                NodegraphAPI.SetNodePosition(node, (0, mergePos[1]+50*(idx+1)))

                currentVersions = self.__abcNodes.get(name)
                if currentVersions:
                    currentVersions.append(int(version[1:]))
                else:
                    self.__abcNodes.update({name: [int(version[1:])]})

                alembic_nodes.append(node)

        return alembic_nodes
