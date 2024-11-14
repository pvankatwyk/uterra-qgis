import time
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QDialog, QMessageBox
from qgis.core import QgsProject, QgsMapLayer, QgsMapLayerProxyModel, QgsWkbTypes
from qgis.PyQt.QtWidgets import QProgressDialog
from qgis.PyQt.QtCore import Qt
import os
from .permits import get_permit_summary

from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsApplication

import os

class GenerateReportTask(QgsTask):
    def __init__(self, description, line_path, cities_path, counties_path, padus_path, rail_path, output_path, api_key, use_llm):
        super().__init__(description)
        self.line_path = line_path
        self.cities_path = cities_path
        self.counties_path = counties_path
        self.padus_path = padus_path
        self.rail_path = rail_path
        self.output_path = output_path
        self.api_key = api_key
        self.use_llm = use_llm
        self.error_message = None

    def run(self):
        """Runs the main task logic in a background thread."""
        time.sleep(1)
        from .permits import get_permit_summary  # Import here to avoid GUI blocking
        try:
            # Generate the permit summary report
            get_permit_summary(
                line_path=self.line_path,
                cities_path=self.cities_path,
                counties_path=self.counties_path,
                padus_path=self.padus_path,
                rail_path=self.rail_path,
                output_path=self.output_path,
                api_key=self.api_key,
                use_llm=self.use_llm
            )
            return True  # Indicate success
        except Exception as e:
            self.error_message = str(e)
            QgsMessageLog.logMessage(f"Error generating report: {e}", "UTerra", Qgis.Critical)
            return False  # Indicate failure

    def finished(self, result):
        """Called when the task completes."""
        print("Task finished")
        if result:
            QMessageBox.information(None, "Success", f"Permit report generated successfully at {self.output_path}")
        else:
            QMessageBox.critical(None, "Error", f"Failed to generate report: {self.error_message}")

    def cancel(self):
        """Called if the task is canceled."""
        print("Task canceled")
        super().cancel()
        QgsMessageLog.logMessage("Generate report task was canceled", "UTerra", Qgis.Warning)
        print("Task canceled")

class Uterra:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        # Define the icon path
        icon_path = os.path.join(os.path.dirname(__file__), "uterra_icon.ico")
        icon = QIcon(icon_path)

        # Add toolbar button and menu item with the icon
        self.action = QAction(icon, "Generate Permit Report", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Uterra Permitting Tool", self.action)

    def unload(self):
        # Remove toolbar icon and menu item
        self.iface.removeToolBarIcon(self.action)
        self.action = None

    def run(self):
        print("Task started")
        if not self.dialog:
            # Load the .ui file
            ui_file = os.path.join(os.path.dirname(__file__), "uterra_plugin.ui")
            self.dialog = uic.loadUi(ui_file)

            # Set filters on the QgsMapLayerComboBox widgets to only show vector layers
            self.dialog.select_line_maplayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
            self.dialog.select_cities_maplayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
            self.dialog.select_counties_maplayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
            self.dialog.select_padus_maplayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
            self.dialog.select_railway_maplayer_2.setFilters(QgsMapLayerProxyModel.VectorLayer)
            
            

            # Set geometry type filters
            # Only show line layers for select_line_maplayer and select_railway_maplayer_2
            self.dialog.select_line_maplayer.setFilters(QgsMapLayerProxyModel.LineLayer)
            self.dialog.select_railway_maplayer_2.setFilters(QgsMapLayerProxyModel.LineLayer)
            
            # Only show polygon layers for select_cities_maplayer, select_counties_maplayer, and select_padus_maplayer
            self.dialog.select_cities_maplayer.setFilters(QgsMapLayerProxyModel.PolygonLayer)
            self.dialog.select_counties_maplayer.setFilters(QgsMapLayerProxyModel.PolygonLayer)
            self.dialog.select_padus_maplayer.setFilters(QgsMapLayerProxyModel.PolygonLayer)


            # Allow empty (None) option for each QgsMapLayerComboBox
            # self.dialog.select_line_maplayer.setAllowEmptyLayer(True)
            self.dialog.select_cities_maplayer.setAllowEmptyLayer(True)
            self.dialog.select_counties_maplayer.setAllowEmptyLayer(True)
            self.dialog.select_padus_maplayer.setAllowEmptyLayer(True)
            self.dialog.select_railway_maplayer_2.setAllowEmptyLayer(True)
            
            # self.dialog.select_line_maplayer.setCurrentIndex(-1)
            self.dialog.select_cities_maplayer.setCurrentIndex(-1)
            self.dialog.select_counties_maplayer.setCurrentIndex(-1)
            self.dialog.select_padus_maplayer.setCurrentIndex(-1)
            self.dialog.select_railway_maplayer_2.setCurrentIndex(-1)

            # Connect the Browse button to open directory dialog
            self.dialog.directoryPathBrowse.clicked.connect(self.select_output_directory)

            # Connect the Generate Report button to start report generation
            self.dialog.generate_report_button.clicked.connect(self.generate_report)

        self.dialog.show()

    def select_output_directory(self):
        """Open a directory selection dialog and set the selected path in the QLineEdit."""
        directory = QFileDialog.getExistingDirectory(self.dialog, "Select Output Directory")
        if directory:
            self.dialog.directoryPathEdit.setText(directory)

    def generate_report(self):
        print("Using LLM: ", self.dialog.llm_checkbox.isChecked())
        # Gather user inputs
        line_layer = self.dialog.select_line_maplayer.currentLayer()
        cities_layer = self.dialog.select_cities_maplayer.currentLayer()
        counties_layer = self.dialog.select_counties_maplayer.currentLayer()
        padus_layer = self.dialog.select_padus_maplayer.currentLayer()
        rail_layer = self.dialog.select_railway_maplayer_2.currentLayer()
        output_path = self.dialog.directoryPathEdit.text()
        api_key = self.dialog.apikey_input.text()
        use_llm = self.dialog.llm_checkbox.isChecked()

        # Validate inputs
        if not output_path:
            QMessageBox.warning(self.dialog, "Input Required", "Please select an output directory.")
            return
        if not line_layer:
            QMessageBox.warning(self.dialog, "Input Required", "Please select a line layer.")
            return
        if not any([cities_layer, counties_layer, padus_layer, rail_layer]):
            QMessageBox.warning(self.dialog, "Input Required", "Please select at least one other layer.")
            return
        if not api_key and use_llm:
            QMessageBox.warning(self.dialog, "Input Required", "Please enter an OpenAI API key to use LLM.")
            return
        
        # Prepare file paths for each layer
        line_path = line_layer.dataProvider().dataSourceUri() if line_layer else ""
        cities_path = cities_layer.dataProvider().dataSourceUri() if cities_layer else ""
        counties_path = counties_layer.dataProvider().dataSourceUri() if counties_layer else ""
        padus_path = padus_layer.dataProvider().dataSourceUri() if padus_layer else ""
        rail_path = rail_layer.dataProvider().dataSourceUri() if rail_layer else ""

        # Create and start the task
        task = GenerateReportTask(
            "Generating Permit Report to " + output_path,
            line_path,
            cities_path,
            counties_path,
            padus_path,
            rail_path,
            os.path.join(output_path, "permit_report.md"),
            api_key,
            use_llm
        )
        print("Adding task to task manager")
        QgsApplication.taskManager().addTask(task)
        
        # Check the task state after a short delay
        for _ in range(5):
            time.sleep(0.5)  # Wait for half a second
            if task.isActive():
                print("Task is now active")
                break
            elif task.isCanceled():
                print("Task was canceled")
                break
            else:
                print("Task is still not active, checking again...")