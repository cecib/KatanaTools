from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)

from Katana import UI4
from . import ScriptActions as SA

class AlembicLoaderEditor(QtWidgets.QWidget):

    def __init__(self, parent, node):
        """
        Initializes an instance of the class.
        """
        QtWidgets.QWidget.__init__(self, parent)

        self.__node = node

        # Get the SuperTool's parameters
        locationParameter = self.__node.getParameter('location')
        folderPathParameter = self.__node.getParameter('folderPath')

        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy
        self.__locationParameterPolicy = CreateParameterPolicy(
            None, locationParameter)

        self.__folderPathParameterPolicy = CreateParameterPolicy(
            None, folderPathParameter)
        self.__folderPathParameterPolicy.addCallback(
            self.folderPathParameterChangedCallback)

        self.__addButton = UI4.Widgets.ToolbarButton(
            'Load Alembics', self,
            UI4.Util.IconManager.GetPixmap('Icons/editText16.png'),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap('Icons/editTextHilite16.png'))
        self.__addButton.clicked.connect(self.__addButtonClicked)

        #######################################################################
        # Create UI widgets from the parameter policies to display the values
        # contained in the parameter.
        #######################################################################
        WidgetFactory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        locationWidget = WidgetFactory.buildWidget(
            self, self.__locationParameterPolicy)
        folderPathWidget = WidgetFactory.buildWidget(
            self, self.__folderPathParameterPolicy)

        # Create a layout and add the parameter editing widgets to it
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(locationWidget)
        mainLayout.addWidget(folderPathWidget)
        mainLayout.addWidget(self.__addButton)

        # Apply the layout to the widget
        self.setLayout(mainLayout)

    def __addButtonClicked(self):
        nodes = self.__node.loadAlembics(self.__folderPathParameterPolicy.getValue())

    def folderPathParameterChangedCallback(self, *args, **kwds):
        # Update our custom widget to display the new image
        folderPath = self.__folderPathParameterPolicy.getValue()
        print(folderPath)
