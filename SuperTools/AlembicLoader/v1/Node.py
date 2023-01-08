import os
import logging
import re

from Katana import (
    NodegraphAPI,
    AssetAPI,
)
from . import ScriptActions as SA

log = logging.getLogger('AlembicLoaderNode')

regex_name = r"^(.*?)\_v\d{3}.abc"
regex_version = r"(v\d{3})"


class AlembicLoaderNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()

        self.addOutputPort("output")

        self.getParameters().createChildString('location', '/root')
        self.getParameters().createChildString('folderPath', '')

    def addParameterHints(self, attrName, inputDict):
        inputDict.update(_ExtraHints.get(attrName, {}))

    def loadAlembics(self, rootdir):
        alembic_nodes = []
        for root, subdirs, files in os.walk(rootdir):
            for filename in files:

                if not filename.endswith(".abc"):
                    continue

                fullpath = root + os.sep + filename

                name = re.match(regex_name, filename).groups()[0]
                version = re.split(regex_version, filename)[1]

                node = NodegraphAPI.CreateNode("Alembic_In", NodegraphAPI.GetRootNode())
                node.setName(name)

                node.getParameter('name').setValue('/root/world/' + name, 1.0)
                node.getParameter('abcAsset').setValue(fullpath, 1.0)

                rootParam = node.getParameters()
                studioParams = rootParam.createChildGroup("studio")
                studioParams.createChildNumber("version", int(version[1:]))

                alembic_nodes.append(node)
        return alembic_nodes

_ExtraHints = {
    'ImageCoordinate.location': {
        'widget': 'newScenegraphLocation',
        'help':
            """
            The scene graph location to load alembics into.
            """,
    },
    'ImageCoordinate.folderPath': {
        'widget': 'assetIdInput',
        'help':
            """
            Location of alembics to load.
            """,
    },
}

