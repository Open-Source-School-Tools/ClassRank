import json
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
    QLabel, QMenuBar, QMessageBox, QDialog, QFormLayout, 
    QComboBox, QSpinBox, QDialogButtonBox, QGridLayout, QInputDialog, 
    QLineEdit, QFileDialog
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt
from qt_material import apply_stylesheet

class HonorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClassRank")
        self.setGeometry(100, 100, 800, 600)
        self.students = {}  # Dictionary to store student names and points

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Grid layout for student buttons
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)
        
        # Label for no students message
        self.no_students_label = QLabel("There aren't any students yet. You can add a student using the menu.")
        self.no_students_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.no_students_label)
        
        # Create menu bar
        self.create_menu()

        # Show the initial setup dialog
        self.show_initial_setup_dialog()

    def create_menu(self):
        # Creating a menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # Adding Add Student action
        add_student_action = QAction("Add Student...", self)
        add_student_action.triggered.connect(self.add_student_dialog)
        file_menu.addAction(add_student_action)

        # Adding Remove Student action
        remove_student_action = QAction("Remove Student...", self)
        remove_student_action.triggered.connect(self.remove_student_dialog)
        file_menu.addAction(remove_student_action)

        # Adding Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Adding the About action under Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_initial_setup_dialog(self):
        # Create a message box with custom buttons
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Welcome to ClassRank")
        message_box.setText("Do you want to create a new class or load an existing one?")
    
        # Add custom buttons
        create_new_button = message_box.addButton("Create New Class", QMessageBox.ButtonRole.AcceptRole)
        load_from_file_button = message_box.addButton("Load From File", QMessageBox.ButtonRole.RejectRole)
        
        message_box.setDefaultButton(create_new_button)
        
        # Show the message box and get the user's response
        message_box.exec()
        
        if message_box.clickedButton() == create_new_button:
            self.create_new_class()
        elif message_box.clickedButton() == load_from_file_button:
            self.load_class_from_file()

    def create_new_class(self):
        self.students = {}  # Initialize with an empty dictionary
        self.update_grid()

    def load_class_from_file(self):
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Class File", "", "ClassRank Points Info (*.hpi);;All Files (*)", options=options
        )

        if file_name:
            try:
                with open(file_name, 'r') as file:
                    self.students = json.load(file)
                self.update_grid()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {e}\nThe program will start with a new class.")

    def save_class_to_file(self):
        options = QFileDialog.Option.ShowDirsOnly
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Class File", "", "ClassRank Points Info (*.hpi);;All Files (*)", options=options
        )

        if file_name:
            if not file_name.endswith('.hpi'):
                file_name += '.hpi'

            try:
                with open(file_name, 'w') as file:
                    json.dump(self.students, file, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def show_about_dialog(self):
        # About dialog box
        about_text = (
            "<div style='display: flex; align-items: center;'>"
            "<img src='Res/logodarb.png' height='75' style='margin-right: 15px;'>"
            "<div>"
            "<h1 style='margin: 0; font-size: 24px; font-weight: bold;'>ClassRank</h1>"
            "<p>Version Dev</p>"
            "<p>This program allows you to add or remove points "
            "for students based on their performance.</p>"
            "<p>Created by DevelopCMD (https://github.com/DevelopCMD)</p>"
            "<p>Part of the Open Source School Tools Collection</p>"
            "<p>This program is licensed under the GNU-GPL license.</p>"
            "<div style='display: flex; align-items: center; margin-top: 20px;'>"
            "<img src='Res/qt.png' height='50' style='margin-right: 10px;'>"
            "<p>Made with <b>Qt</b></p>"
            "<p>This program uses PyQt6. "
            "Qt and the Qt logo are trademarks of The Qt Company Ltd.</p>"
            "</div>"
            "</div>"
            "</div>"
            "</div>"
		)
        QMessageBox.about(self, "About ClassRank", about_text)

    def add_student_dialog(self):
        name, ok = QInputDialog.getText(self, "Add Student", "Enter student name:")
        if ok and name.strip():
            if name in self.students:
                QMessageBox.warning(self, "Warning", "Student already exists.")
            else:
                self.students[name] = 0  # Initialize points to 0
                self.update_grid()

    def remove_student_dialog(self):
        if not self.students:
            QMessageBox.warning(self, "Warning", "No students to remove.")
            return
        
        # Create a dialog to select a student to remove
        student_names = list(self.students.keys())
        name, ok = QInputDialog.getItem(self, "Remove Student", "Select a student to remove:", student_names, editable=False)
        if ok and name in self.students:
            del self.students[name]
            self.update_grid()

    def update_grid(self):
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        if self.students:
            # Hide the no students message if there are students
            self.no_students_label.hide()
            
            # Populate grid with student buttons
            row, col = 0, 0
            for name, points in self.students.items():
                student_button = self.create_student_button(name, points)
                self.grid_layout.addWidget(student_button, row, col)
                col += 1
                if col >= 3:  # Adjust number of columns as needed
                    col = 0
                    row += 1
        else:
            # Show the no students message if there are no students
            self.no_students_label.show()

    def create_student_button(self, name, points):
        button = QPushButton(f"{name}\nPoints: {points}")
        button.setFixedSize(150, 100)
        button.setFont(QFont("Arial", 10))
        button.clicked.connect(lambda: self.open_student_settings(name))

        # Set button color based on points
        if points >= 0:
            button.setStyleSheet("background-color: lightgreen; border: 1px solid black; color: black")
        else:
            button.setStyleSheet("background-color: lightcoral; border: 1px solid black; color: red")
        
        return button

    def open_student_settings(self, name):
        # Open the student settings dialog
        dialog = StudentSettingsDialog(name, self.students)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_grid()

    def closeEvent(self, event):
        # Prompt user to save data before closing
        reply = QMessageBox.question(
            self, 'Save Data', 'Do you want to save your class data before exiting?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.save_class_to_file()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()

class StudentSettingsDialog(QDialog):
    def __init__(self, student_name, students):
        super().__init__()
        self.setWindowTitle(f"Settings for {student_name}")
        self.students = students
        self.original_name = student_name

        # Layout
        layout = QFormLayout(self)

        # Name input
        self.name_input = QLineEdit(student_name)
        layout.addRow("Student Name:", self.name_input)

        # Points input
        self.points_input = QSpinBox()
        self.points_input.setRange(-100, 100)
        self.points_input.setValue(students[student_name])
        layout.addRow("Points:", self.points_input)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_changes)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept_changes(self):
        new_name = self.name_input.text().strip()
        new_points = self.points_input.value()

        # Update student information
        if new_name and new_name != self.original_name:
            if new_name in self.students:
                QMessageBox.warning(self, "Warning", "Another student with this name already exists.")
                return
            del self.students[self.original_name]
            self.students[new_name] = new_points
        else:
            self.students[self.original_name] = new_points
        
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    window = HonorApp()
    window.show()
    sys.exit(app.exec())
