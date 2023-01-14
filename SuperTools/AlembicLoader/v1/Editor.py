from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)
from Katana import UI4

# 1. Can you make camera_reference and camera_asset (and any other case where
#    the first word part of name separated by '_' are the same) mutually exclusive?
#    An artist would use one of them as an active camera.


class AlembicLoaderEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        QtWidgets.QWidget.__init__(self, parent)

        self.__node = node

        # Create UI parameters
        location_parameter = self.__node.getParameter("location")
        folder_path_parameter = self.__node.getParameter("folderPath")

        create_parameter_policy = UI4.FormMaster.CreateParameterPolicy
        self.__location_parameter_policy = create_parameter_policy(
            None, location_parameter
        )
        self.__folder_path_parameter_policy = create_parameter_policy(
            None, folder_path_parameter
        )

        # Create UI widgets and layout
        widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        location_widget = widget_factory.buildWidget(
            self, self.__location_parameter_policy
        )
        folder_path_widget = widget_factory.buildWidget(
            self, self.__folder_path_parameter_policy
        )
        self.__load_button = UI4.Widgets.ToolbarButton(
            "Load Alembics",
            self,
            UI4.Util.IconManager.GetPixmap("Icons/editText16.png"),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap("Icons/editTextHilite16.png"),
        )
        self.__load_button.clicked.connect(self.__load_button_clicked)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(location_widget)
        self.main_layout.addWidget(folder_path_widget)
        self.main_layout.addWidget(self.__load_button)

        self.setLayout(self.main_layout)

        self.__combo_boxes = {}
        self.__check_boxes = {}

    def __load_button_clicked(self):
        for node in self.__node.load_alembics(
            self.__folder_path_parameter_policy.getValue()
        ):
            geo_name = (
                node.getParameters().getChild("name").getValue(1.0).split("/")[-1]
            )

            # Add check box widget to enable/disable geo
            check_box = self.__check_boxes.get(geo_name)
            if not check_box:
                check_box = QtWidgets.QCheckBox(geo_name + " enabled", self)
                check_box.setChecked(True)
                check_box.stateChanged.connect(
                    lambda state, name=geo_name: self.__check_box_clicked(state, name)
                )
                self.main_layout.addWidget(check_box)
                self.__check_boxes.update({geo_name: check_box})

            # Add combo box widget to control geo version
            combo_box = self.__combo_boxes.get(geo_name)
            if not combo_box:
                combo_box = QtWidgets.QComboBox(self)
                combo_box.currentTextChanged.connect(
                    lambda version, name=geo_name: self.__combo_box_changed(
                        version, name
                    )
                )
                self.main_layout.addWidget(combo_box)
                self.__combo_boxes.update({geo_name: combo_box})

            # Add version options and set to latest
            versions = self.__node.get_versions(geo_name).keys()
            for item in versions:
                combo_box.addItem("v" + str(item).zfill(3))
            combo_box.setCurrentText("v" + str(max(versions)).zfill(3))

    def __check_box_clicked(self, state, geo_name):
        combo_box = self.__combo_boxes.get(geo_name)
        if combo_box is None:
            return
        if state == QtCore.Qt.Checked:
            self.__node.enable_node(geo_name)
        else:
            self.__node.disable_node(geo_name)

    def __combo_box_changed(self, version, geo_name):
        self.__node.update_version(
            int(version[1:]),
            geo_name,
        )
