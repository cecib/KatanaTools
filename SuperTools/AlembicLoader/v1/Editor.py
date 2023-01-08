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

        self.__load_button = UI4.Widgets.ToolbarButton(
            'Load Alembics', self,
            UI4.Util.IconManager.GetPixmap('Icons/editText16.png'),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap('Icons/editTextHilite16.png'))
        self.__load_button.clicked.connect(self.__load_button_clicked)

        # Create main UI widgets and layout
        widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        location_widget = widget_factory.buildWidget(
            self, self.__location_parameter_policy)
        folder_path_widget = widget_factory.buildWidget(
            self, self.__folder_path_parameter_policy)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(location_widget)
        self.main_layout.addWidget(folder_path_widget)
        self.main_layout.addWidget(self.__load_button)

        self.setLayout(self.main_layout)

        self.combo_boxes = {}
        self.check_boxes = {}
        self.geo_names = []

    def __load_button_clicked(self):
        nodes = self.__node.load_alembics(self.__folder_path_parameter_policy.getValue())
        for node in nodes:
            node_name = node.getName()
            geo_name = node_name[0:len(node_name)-5]
            self.geo_names.append(geo_name)

            check_box = self.check_boxes.get(geo_name)
            if not check_box:
                check_box = QtWidgets.QCheckBox(geo_name + " enabled", self)
                check_box.setChecked(True)
                check_box.stateChanged.connect(
                    lambda state, name=geo_name: self.__check_box_clicked(state, name)
                )
                self.main_layout.addWidget(check_box)
                self.check_boxes.update({geo_name: check_box})

            combo_box = self.combo_boxes.get(geo_name)
            if not combo_box:
                combo_box = QtWidgets.QComboBox(self)
                combo_box.currentTextChanged.connect(
                    lambda value, name=geo_name: self.__combobox_changed(value, name)
                )
                self.main_layout.addWidget(combo_box)
                self.combo_boxes.update({geo_name: combo_box})
            combo_box.addItem(node.getName().split("_")[-1])

        for geo_name in self.geo_names:
            latest_version = max(self.__node.get_versions(geo_name))
            combo_box = self.combo_boxes.get(geo_name)
            combo_box.setCurrentText("v00" + str(latest_version))

    def __check_box_clicked(self, state, geo_name):
        combo_box = self.combo_boxes.get(geo_name)
        node_name = geo_name + "_" + str(combo_box.currentText())
        if state == QtCore.Qt.Checked:
            self.__node.enable_node(node_name)
        else:
            self.__node.disable_node(node_name)

    def __combobox_changed(self, value, geo_name):
        curr_version = int(value[1:])
        versions = self.__node.get_versions(geo_name)
        node_name = geo_name + "_" + value
        is_checked = self.check_boxes.get(geo_name).isChecked()
        for version in versions:
            if curr_version == version and is_checked:
                self.__node.enable_node(node_name)
            else:
                self.__node.disable_node(geo_name + "_v00" + str(version))
