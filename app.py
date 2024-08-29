import json
import sys
import os
from PyQt6.QtCore import Qt, QSize, QTimer, QEvent, QCoreApplication, QDateTime
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QFont, QAction, QBrush, QColor, QPalette, QPen, QFontDatabase, QCursor, QStandardItem, QStandardItemModel, QImage, QPalette
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QMainWindow, QApplication, QDialog, QMenu, QMenuBar, QFileDialog, QLineEdit, QSpinBox, QFormLayout, QPushButton, QMessageBox, QDialogButtonBox, QWidget, QGridLayout, QInputDialog
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
        
        # Adding theme toggle
        view_menu = menu_bar.addMenu("View")
        theme_toggle = QAction("Toggle Dark Mode", self, checkable=True)
        theme_toggle.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(theme_toggle)
        
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
                # Initialize with 0 points and no profile picture
                self.students[name] = {'points': 0, 'profile_picture': None}
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
                if col >= 4:  # Adjust number of columns as needed
                    col = 0
                    row += 1
        else:
            # Show the no students message if there are no students
            self.no_students_label.show()

    def create_student_button(self, name, data):
        button = QPushButton()
        button.setFixedSize(180, 80)
        button.setFont(QFont("Arial", 10))
        button.clicked.connect(lambda: self.open_student_settings(name))

        points = data['points']
        profile_picture = data.get('profile_picture', '')
        
        # Use the default profile picture if none is set or file doesn't exist
        if not profile_picture or not os.path.exists(profile_picture):
            profile_picture = 'Res/default.png'  # Ensure this path is correct and the image exists
        
        # Set profile picture if available and make it circular
        if profile_picture and os.path.exists(profile_picture):
            pixmap = QPixmap(profile_picture).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon = QIcon(pixmap)
            button.setIcon(icon)
            button.setIconSize(pixmap.size())

        button.setText(f"{name}\nPoints: {points}")
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {'lightgreen' if points >= 0 else 'lightcoral'};
                color: {'black' if points >= 0 else 'white'};
                border: 1px solid black;
                text-align: center;
                padding: 5px;
                font-size: 10pt;
            }}
            QPushButton::icon {{
                margin-bottom: 10px;  /* Space between the icon and the text */
            }}
            """
        )

        # Add circular border to the icon using a QPixmap mask
        if profile_picture and os.path.exists(profile_picture):
            circular_pixmap = QPixmap(48, 48)
            circular_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(circular_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # Draw circular clip
            path = QPainterPath()
            path.addEllipse(0, 0, 48, 48)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            # Set the circular pixmap with a QIcon
            circular_icon = QIcon(circular_pixmap)
            button.setIcon(circular_icon)
            button.setIconSize(QSize(48, 48))

        return button
    
    def open_student_settings(self, name):
        # Open the student settings dialog
        dialog = StudentSettingsDialog(name, self.students)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_grid()

    def toggle_dark_mode(self, checked):
        if checked:
            apply_stylesheet(app, theme='dark_blue.xml')
        else:
            apply_stylesheet(app, theme='light_blue.xml')

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
    def __init__(self, name, students):
        super().__init__()
        self.setWindowTitle("Student Settings")
        self.students = students
        self.original_name = name

        # Dialog layout
        layout = QFormLayout(self)
        
        # Name input
        self.name_edit = QLineEdit(name)
        layout.addRow("Name:", self.name_edit)

        # Points input
        self.points_spin = QSpinBox()
        self.points_spin.setRange(-1000, 1000)
        self.points_spin.setValue(self.students[name]['points'])
        layout.addRow("Points:", self.points_spin)

        # Profile picture button
        self.profile_picture_button = QPushButton("Select Profile Picture")
        self.profile_picture_button.clicked.connect(self.select_profile_picture)
        layout.addRow("Profile Picture:", self.profile_picture_button)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def select_profile_picture(self):
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "", "Image Files (*.png *.jpg *.bmp);;All Files (*)", options=options
        )
        if file_name:
            self.students[self.original_name]['profile_picture'] = file_name

    def accept(self):
        new_name = self.name_edit.text().strip()
        new_points = self.points_spin.value()

        # Check if new name is valid and update student information
        if new_name:
            # Check if renaming is required
            if new_name != self.original_name:
                # Ensure no existing student has the new name
                if new_name in self.students:
                    QMessageBox.warning(self, "Warning", "Another student with this name already exists.")
                    return

                # Move data from original name to new name
                self.students[new_name] = self.students.pop(self.original_name)
                self.students[new_name]['points'] = new_points
            else:
                # If the name hasn't changed, just update the points
                self.students[self.original_name]['points'] = new_points

            # Ensure profile picture is kept if set
            if 'profile_picture' not in self.students[new_name]:
                self.students[new_name]['profile_picture'] = ''

        super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    window = HonorApp()
    window.show()
    sys.exit(app.exec())
