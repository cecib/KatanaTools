# AlembicLoader

Add the directory containing the alembics to the "folderPath" parameter and click on the arrow to load the geometry. Once loaded, the supertool UI will be updated with the parameters to control which assets are enabled and the versions that are used for each.

The AlembicLoaderEditor class (Editor.py) handles everything related to the UI, while 
the AlembicLoaderNode class (Node.py) takes care of the internal logic of the SuperTool,
such as enabling/disabling loaded geometry and switching between versions. This division 
between UI and internal logic is fundamental to any scalable tool.i

