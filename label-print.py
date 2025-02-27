import sys
import sqlite3
import datetime
import csv
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QFormLayout, QDialog, QComboBox, QSpinBox, QSystemTrayIcon
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QIcon
import pyautogui

# Database Functions 
def create_database(db_name='automation.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_name TEXT,
            action_type TEXT,
            parameters TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_action(action_name, action_type, parameters):
    conn = sqlite3.connect('automation.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO actions (action_name, action_type, parameters, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (action_name, action_type, parameters, timestamp))
    conn.commit()
    conn.close()

def get_actions():
    conn = sqlite3.connect('automation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM actions ORDER BY id')
    actions = cursor.fetchall()
    conn.close()
    return actions

def update_action(action_id, action_name, action_type, parameters):
    conn = sqlite3.connect('automation.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute('''
        UPDATE actions
        SET action_name = ?, action_type = ?, parameters = ?, timestamp = ?
        WHERE id = ?
    ''', (action_name, action_type, parameters, timestamp, action_id))
    conn.commit()
    conn.close()

def delete_action(action_id):
    conn = sqlite3.connect('automation.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM actions WHERE id = ?', (action_id,))
    conn.commit()
    conn.close()

# CSV Reading
def read_target_ids(csv_file='target.csv'):
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            target_ids = [row[0] for row in reader]
        return target_ids
    except FileNotFoundError:
        print("Error: targets.csv not found.")
        return []

# Automation Logic (Updated with new actions)
def execute_action(action, target_id=None):
    action_type = action[2]
    params = action[3]
    try:
        if action_type == 'move':
            coords = params.replace('"', '').replace("'", "").split(',')
            x, y = map(int, coords)
            pyautogui.moveTo(x, y, duration=0.5)
        elif action_type == 'click':
            button = params.lower()
            pyautogui.click(button=button)
        elif action_type == 'double_click':
            button = params.lower()
            pyautogui.doubleClick(button=button)
        elif action_type == 'right_click':  # New action
            pyautogui.rightClick()
        elif action_type == 'drag':  # New action
            coords = params.replace('"', '').replace("'", "").split(',')
            x, y = map(int, coords)
            pyautogui.dragTo(x, y, duration=0.5)
        elif action_type == 'hotkey':
            keys = params.split(',')
            pyautogui.hotkey(*keys)
        elif action_type == 'type':
            text = params
            if target_id and '{target_id}' in text:
                text = text.replace('{target_id}', target_id)
            pyautogui.typewrite(text)
        elif action_type == 'wait':
            seconds = float(params)
            time.sleep(seconds)
    except Exception as e:
        print(f"Action '{action[1]}' failed: {e}")

def run_automation(loop_count=0):
    target_ids = read_target_ids()
    actions = get_actions()
    if not target_ids or not actions:
        print("No targets or actions to process.")
        return
    # effective_loops = len(target_ids) if loop_count == 0 else min(loop_count, len(target_ids))
    effective_loops = len(target_ids) if loop_count == 0 else loop_count
    for i in range(effective_loops):
        target_id = target_ids[i] if loop_count == 0 else i+1
        print(f"Processing target ID: {target_id}")
        for action in actions:
            execute_action(action, target_id)
            time.sleep(1.0)  # Default delay between actions

# Action Dialog (Updated with new actions)
class ActionDialog(QDialog):
    def __init__(self, parent=None, action=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Action")
        self.layout = QFormLayout(self)
        self.setFont(QFont("Arial", 16))  # Larger font

        self.action_name = QLineEdit()
        self.action_type = QComboBox()
        self.action_type.addItems(['move', 'click', 'double_click', 'right_click', 'drag', 'hotkey', 'type', 'wait'])
        self.parameters = QLineEdit()
        
        self.desc_label = QLabel(
            "Parameters:\n"
            "- move: 'x,y' (e.g., 100,200)\n"
            "- click: 'left' or 'right'\n"
            "- double_click: 'left' or 'right'\n"
            "- right_click: none (current position)\n"
            "- drag: 'x,y' (e.g., 300,400)\n"
            "- hotkey: keys (e.g., ctrl,c for copy)\n"
            "- type: text or '{target_id}'\n"
            "- wait: seconds (e.g., 2.5)"
        )
        self.desc_label.setFont(QFont("Arial", 12))

        if action:
            self.action_name.setText(action[1])
            self.action_type.setCurrentText(action[2])
            self.parameters.setText(action[3])
        
        self.layout.addRow("Action Name:", self.action_name)
        self.layout.addRow("Action Type:", self.action_type)
        self.layout.addRow("Parameters:", self.parameters)
        self.layout.addRow(self.desc_label)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        # Style
        self.setStyleSheet("""
            QLineEdit, QComboBox { font-size: 16px; padding: 5px; }
            QPushButton { font-size: 16px; padding: 8px; background-color: #4CAF50; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #45a049; }
        """)

    def get_data(self):
        params = self.parameters.text().strip().replace('"', '').replace("'", "")
        return (
            self.action_name.text(),
            self.action_type.currentText(),
            params
        )

# Main Window (Updated with tray and UI enhancements)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automation Tool")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.setFont(QFont("Arial", 16))  # Larger font
        
        # Mouse position label
        self.mouse_label = QLabel("Mouse Position: X: 0, Y: 0")
        self.layout.addWidget(self.mouse_label)
        
        # Action table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Type', 'Parameters', 'Timestamp'])
        self.table.horizontalHeader().setFont(QFont("Arial", 16))
        self.layout.addWidget(self.table)
        
        # Buttons
        self.add_button = QPushButton("Add Action")
        self.add_button.clicked.connect(self.add_action)
        self.layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Action")
        self.edit_button.clicked.connect(self.edit_action)
        self.layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Action")
        self.delete_button.clicked.connect(self.delete_action)
        self.layout.addWidget(self.delete_button)
        
        self.start_button = QPushButton("Start Automation")
        self.start_button.clicked.connect(self.start_automation)
        self.layout.addWidget(self.start_button)
        
        # Loop input
        self.loop_label = QLabel("Number of Loops (0 for all targets):")
        self.loop_input = QSpinBox()
        self.loop_input.setMinimum(0)
        self.layout.addWidget(self.loop_label)
        self.layout.addWidget(self.loop_input)
        
        # System tray
        self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("system"), self)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.restore_from_tray)
        
        # Timer for mouse position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(100)  # Update every 100ms
        
        create_database()
        self.load_actions()

        # Style the UI
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QLabel { font-size: 16px; }
            QTableWidget { font-size: 14px; }
            QPushButton { font-size: 16px; padding: 10px; background-color: #2196F3; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #1976D2; }
            QSpinBox { font-size: 16px; padding: 5px; }
        """)
        self.layout.setSpacing(15)

    def update_mouse_position(self):
        x, y = pyautogui.position()
        self.mouse_label.setText(f"Mouse Position: X: {x}, Y: {y}")
    
    def load_actions(self):
        actions = get_actions()
        self.table.setRowCount(len(actions))
        for row, action in enumerate(actions):
            for col, item in enumerate(action):
                table_item = QTableWidgetItem(str(item))
                table_item.setFont(QFont("Arial", 14))
                self.table.setItem(row, col, table_item)
    
    def add_action(self):
        dialog = ActionDialog(self)
        if dialog.exec():
            action_name, action_type, parameters = dialog.get_data()
            add_action(action_name, action_type, parameters)
            self.load_actions()
    
    def edit_action(self):
        selected = self.table.currentRow()
        if selected >= 0:
            action_id = int(self.table.item(selected, 0).text())
            action = get_actions()[selected]
            dialog = ActionDialog(self, action)
            if dialog.exec():
                action_name, action_type, parameters = dialog.get_data()
                update_action(action_id, action_name, action_type, parameters)
                self.load_actions()
    
    def delete_action(self):
        selected = self.table.currentRow()
        if selected >= 0:
            action_id = int(self.table.item(selected, 0).text())
            delete_action(action_id)
            self.load_actions()
    
    def start_automation(self):
        loop_count = self.loop_input.value()
        self.showMinimized()  # Minimize to tray
        run_automation(loop_count)
        self.tray_icon.showMessage("Automation", "Automation completed!", QSystemTrayIcon.Information, 2000)

    def restore_from_tray(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())