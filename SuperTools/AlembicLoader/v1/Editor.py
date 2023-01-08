from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)

from Katana import UI4
from . import ScriptActions

class AlembicLoaderEditor(QtWidgets.QWidget):

    def __init__(self, parent, node):
        QtWidgets.QWidget.__init__(self, parent)

        self.__node = node

        # Create UI parameters
        locationParameter = self.__node.getParameter('location')
        folderPathParameter = self.__node.getParameter('folderPath')

        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy
        self.__locationParameterPolicy = CreateParameterPolicy(
            None, locationParameter)

        self.__folderPathParameterPolicy = CreateParameterPolicy(
            None, folderPathParameter)

        self.__addButton = UI4.Widgets.ToolbarButton(
            'Load Alembics', self,
            UI4.Util.IconManager.GetPixmap('Icons/editText16.png'),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap('Icons/editTextHilite16.png'))
        self.__addButton.clicked.connect(self.__addButtonClicked)

        # Create UI widgets and layout
        WidgetFactory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        locationWidget = WidgetFactory.buildWidget(
            self, self.__locationParameterPolicy)
        folderPathWidget = WidgetFactory.buildWidget(
            self, self.__folderPathParameterPolicy)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(locationWidget)
        self.mainLayout.addWidget(folderPathWidget)
        self.mainLayout.addWidget(self.__addButton)

        self.setLayout(self.mainLayout)

    def __addButtonClicked(self):
        nodes = self.__node.loadAlembics(self.__folderPathParameterPolicy.getValue())
        for node in nodes:
            checkbox = QtWidgets.QCheckBox(node.getName() + " enabled", self)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda checked, val=node: self.__checkBoxClicked(checked, val)
            )
            self.mainLayout.addWidget(checkbox)

    def __checkBoxClicked(self, state, node):
        if state == QtCore.Qt.Checked:
            node.setBypassed(False)
        else:
            node.setBypassed(True)
