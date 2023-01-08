from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)
from Katana import UI4


class AlembicLoaderEditor(QtWidgets.QWidget):

    def __init__(self, parent, node):
        QtWidgets.QWidget.__init__(self, parent)

        self.__node = node

        # Create UI parameters
        location_parameter = self.__node.getParameter('location')
        folder_path_parameter = self.__node.getParameter('folderPath')

        create_parameter_policy = UI4.FormMaster.CreateParameterPolicy
        self.__location_parameter_policy = create_parameter_policy(
            None, location_parameter)

        self.__folder_path_parameter_policy = create_parameter_policy(
            None, folder_path_parameter)

        self.__add_button = UI4.Widgets.ToolbarButton(
            'Load Alembics', self,
            UI4.Util.IconManager.GetPixmap('Icons/editText16.png'),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap('Icons/editTextHilite16.png'))
        self.__add_button.clicked.connect(self.__add_button_clicked)

        # Create main UI widgets and layout
        widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        location_widget = widget_factory.buildWidget(
            self, self.__location_parameter_policy)
        folder_path_widget = widget_factory.buildWidget(
            self, self.__folder_path_parameter_policy)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(location_widget)
        self.main_layout.addWidget(folder_path_widget)
        self.main_layout.addWidget(self.__add_button)

        self.setLayout(self.main_layout)

    def __add_button_clicked(self):
        combo_boxes = {}
        check_boxes = {}

        nodes = self.__node.load_alembics(self.__folder_path_parameter_policy.getValue())
        for node in nodes:
            node_name = node.getName()
            geo_name = node_name[0:len(node_name)-5]

            check_box = check_boxes.get(geo_name)
            if not check_box:
                check_box = QtWidgets.QCheckBox(geo_name + " enabled", self)
                check_box.setChecked(True)
                check_box.stateChanged.connect(
                    lambda checked, val=node_name: self.__check_box_clicked(checked, val)
                )
                self.main_layout.addWidget(check_box)
                check_boxes.update({geo_name: check_box})

            combo_box = combo_boxes.get(geo_name)
            if not combo_box:
                combo_box = QtWidgets.QComboBox(self)
                self.main_layout.addWidget(combo_box)
                combo_boxes.update({geo_name: combo_box})
            combo_box.addItem(node.getName().split("_")[-1])

    def __check_box_clicked(self, state, node_name):
        if state == QtCore.Qt.Checked:
            self.__node.enable_node(node_name)
        else:
            self.__node.disable_node(node_name)
