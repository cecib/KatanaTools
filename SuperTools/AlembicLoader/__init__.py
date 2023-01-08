import Katana
from . import v1 as AlembicLoader

if AlembicLoader:
    PluginRegistry = [
        ("SuperTool", 2, "AlembicLoader", (AlembicLoader.AlembicLoaderNode,
                                           AlembicLoader.GetEditor)),
    ]
