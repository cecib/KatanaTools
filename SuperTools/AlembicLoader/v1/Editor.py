from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)
from Katana import UI4


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

        # Mapping from geo or category name to Qt widgets
        # {name: [widgets]}
        self.__check_boxes = {}
        self.__combo_boxes_ver = {}
        self.__combo_boxes_cat = {}

    def __check_box_clicked(self, state, category):
        """Enable/disable nodes under category based on check box state

        :param state: (Qt.Checked) Object representing state
        :param category: (str) Active category
        """
        combo_box_cat = self.__combo_boxes_cat.get(category)
        active_geo_name = combo_box_cat.currentText()
        is_enabled = state == QtCore.Qt.Checked
        # Enable geo that is active in category combo box
        for geo_name in [
            combo_box_cat.itemText(i) for i in range(combo_box_cat.count())
        ]:
            if geo_name == active_geo_name and is_enabled:
                self.__node.enable_node(geo_name)
            else:
                self.__node.disable_node(geo_name)

    def __combo_box_category_changed(self, geo_name):
        """Update nodes based on active category

        :param geo_name: (str) Name of geometry
        """
        category = geo_name.split("_")[0]
        # Update versions in combo box with correct labels
        combo_box_ver = self.__combo_boxes_ver.get(category)
        if combo_box_ver:
            self.__update_combo_box_versions(category, geo_name)
        # Enable active geo and disable others in category
        check_box = self.__check_boxes.get(category)
        if not check_box.isChecked():
            return
        self.__node.enable_node(geo_name)
        for name in self.__node.get_category_values(category):
            if name != geo_name:
                self.__node.disable_node(name)

    def __combo_box_version_changed(self, version, category):
        """Update nodes based on active geometry version

        :param version: (str) Updated version value
        :param category: (str) Category being changed
        """
        geo_name = self.__combo_boxes_cat.get(category).currentText()
        if not version:
            return
        self.__node.update_version(
            int(version[1:]),
            geo_name,
        )

    def __load_button_clicked(self):
        """Trigger node to load alembics in current folder path parameter
        and set up UI widgets
        """
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

            # Update or create combo box widget to control category options
            combo_box_cat = self.__update_combo_box(
                category, self.__combo_boxes_cat, self.__combo_box_category_changed
            )
            combo_box_cat.addItem(geo_name)
            combo_box_cat.setCurrentText(geo_name)

            # Update or create combo box widget to control geo version
            self.__update_combo_box(
                category,
                self.__combo_boxes_ver,
                lambda version, name=category: self.__combo_box_version_changed(
                    version, name
                ),
            )
            self.__update_combo_box_versions(category, geo_name)

    def __update_combo_box(self, category, container, text_changed):
        """Update or create combo box inside given container based on
        provided category

        :param category: (str) The category name for combo boxes
        :param container: (dict) Contains all relevant combo boxes
        :param text_changed: (function) Triggered with text change
        :return: (QtWidgets.QComboBox) Updated or created widget
        """
        combo_box = container.get(category)
        if not combo_box:
            combo_box = QtWidgets.QComboBox(self)
            combo_box.currentTextChanged.connect(text_changed)
            self.main_layout.addWidget(combo_box)
            container.update({category: combo_box})
        return combo_box

    def __update_combo_box_versions(self, category, geo_name):
        """Update version combo box for category using active geo name

        :param category: (str) Category for current geometry
        :param geo_name: (str) Active geometry name
        """
        combo_box_ver = self.__combo_boxes_ver.get(category)
        combo_box_ver.clear()
        versions = self.__node.get_versions(geo_name).keys()
        for item in versions:
            combo_box_ver.addItem(self.VERSION_LABEL + str(item).zfill(3))
        combo_box_ver.setCurrentText(self.VERSION_LABEL + str(max(versions)).zfill(3))
