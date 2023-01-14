from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)
from Katana import UI4

# 1. Can you make camera_reference and camera_asset (and any other case where
#    the first word part of name separated by '_' are the same) mutually exclusive?
#    An artist would use one of them as an active camera.

# Do not repeat constants like "abcAsset"
# Fix comments, for example those in load_alembics don't flow/fit well


class AlembicLoaderEditor(QtWidgets.QWidget):

    VERSION_LABEL = "v"

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

        # Mapping from geo or category name to Qt widget
        # {name: widget}
        self.__check_boxes = {}
        self.__combo_boxes_ver = {}
        self.__combo_boxes_cat = {}

    def __check_box_clicked(self, state, category):
        combo_box_cat = self.__combo_boxes_cat.get(category)
        is_enabled = state == QtCore.Qt.Checked
        for x in [
            combo_box_cat.itemText(i) for i in range(combo_box_cat.count())
        ]:
            if is_enabled:
                self.__node.enable_node(x)
            else:
                self.__node.disable_node(x)

    def __combo_box_category_changed(self, y):
        category = y.split("_")[0]
        # Update versions in combo box with correct labels
        combo_box_ver = self.__combo_boxes_ver.get(category)
        if combo_box_ver:
            self.__update_combo_box_versions(category, y)
        # Enable active geo and disable others in category
        check_box = self.__check_boxes.get(category)
        if not check_box.isChecked():
            return
        self.__node.enable_node(y)
        for name in self.__node.get_category_values(category):
            if name != y:
                self.__node.disable_node(name)

    def __combo_box_version_changed(self, version, category):
        geo_name = self.__combo_boxes_cat.get(category).currentText()
        if not version:
            return
        self.__node.update_version(
            int(version[1:]),
            geo_name,
        )

    def __load_button_clicked(self):
        for node in self.__node.load_alembics(
            self.__folder_path_parameter_policy.getValue()
        ):
            geo_name = (
                node.getParameters().getChild("name").getValue(1.0).split("/")[-1]
            )
            category = geo_name.split("_")[0]

            # Add check box widget to enable/disable category
            check_box = self.__check_boxes.get(category)
            if not check_box:
                check_box = QtWidgets.QCheckBox(category, self)
                check_box.setChecked(True)
                check_box.stateChanged.connect(
                    lambda state, name=category: self.__check_box_clicked(state, name)
                )
                self.main_layout.addWidget(check_box)
                self.__check_boxes.update({category: check_box})

            # Add combo box widget to control category options
            combo_box_cat = self.__combo_boxes_cat.get(category)
            if not combo_box_cat:
                combo_box_cat = QtWidgets.QComboBox(self)
                combo_box_cat.currentTextChanged.connect(
                    self.__combo_box_category_changed
                )
                self.main_layout.addWidget(combo_box_cat)
                self.__combo_boxes_cat.update({category: combo_box_cat})
            combo_box_cat.addItem(geo_name)
            combo_box_cat.setCurrentText(geo_name)

            # Add combo box widget to control geo version
            combo_box_ver = self.__combo_boxes_ver.get(category)
            if not combo_box_ver:
                combo_box_ver = QtWidgets.QComboBox(self)
                combo_box_ver.currentTextChanged.connect(
                    lambda version, name=category: self.__combo_box_version_changed(
                        version, name
                    )
                )
                self.main_layout.addWidget(combo_box_ver)
                self.__combo_boxes_ver.update({category: combo_box_ver})

            # Add version options and set to latest
            self.__update_combo_box_versions(category, geo_name)

    def __update_combo_box_versions(self, category, geom_name):
        combo_box_ver = self.__combo_boxes_ver.get(category)
        combo_box_ver.clear()
        versions = self.__node.get_versions(geom_name).keys()
        for item in versions:
            combo_box_ver.addItem(self.VERSION_LABEL + str(item).zfill(3))
        combo_box_ver.setCurrentText(self.VERSION_LABEL + str(max(versions)).zfill(3))
