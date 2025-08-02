import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLineEdit, 
                            QScrollArea, QFrame, QLabel, QCheckBox, QComboBox)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QPoint, QEasingCurve, 
                         QParallelAnimationGroup, QThread, pyqtSignal, QTimer)
from PyQt6.QtGui import QFont, QPalette, QColor
from google import genai
from google.genai import types

class USBCommandWidget(QFrame):
    def __init__(self, command_data, usb_path, translations):
        super().__init__()
        self.command_data = command_data
        self.usb_path = usb_path
        self.translations = translations
        self.input_fields = {}
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 55, 72, 0.9);
                border-radius: 8px;
                border: 1px solid rgba(99, 102, 241, 0.3);
                margin: 5px;
                padding: 10px;
            }
            QTextEdit {
                background-color: rgba(30, 41, 59, 0.8);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        desc_label = QLabel(self.command_data.get('description', 'No description'))
        desc_label.setStyleSheet("color: #e2e8f0; font-size: 14px; font-weight: bold; margin-bottom: 8px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        inputs = self.command_data.get('inputs', [])
        if inputs:
            inputs_frame = QFrame()
            inputs_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 41, 59, 0.6);
                    border-radius: 6px;
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    padding: 10px;
                    margin: 5px 0px;
                }
            """)
            inputs_layout = QVBoxLayout(inputs_frame)
            
            for input_config in inputs:
                input_row = QHBoxLayout()
                
                label = QLabel(input_config.get('label', 'Input') + ":")
                label.setStyleSheet("color: #94a3b8; font-size: 12px; min-width: 100px;")
                
                input_field = QLineEdit()
                input_field.setText(input_config.get('default', ''))
                input_field.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(51, 65, 85, 0.8);
                        color: #f1f5f9;
                        border: 1px solid rgba(99, 102, 241, 0.3);
                        border-radius: 4px;
                        padding: 6px;
                        font-size: 12px;
                    }
                    QLineEdit:focus {
                        border-color: #6366f1;
                    }
                """)
                
                self.input_fields[input_config['name']] = input_field
                
                input_row.addWidget(label)
                input_row.addWidget(input_field, 1)
                inputs_layout.addLayout(input_row)
            
            layout.addWidget(inputs_frame)
        
        command_text = QTextEdit()
        command_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 41, 59, 0.8);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        command_text.setMaximumHeight(80)
        command_text.setReadOnly(True)
        self.command_display = command_text
        layout.addWidget(command_text)
        
        self.output_display = QTextEdit()
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(20, 20, 30, 0.9);
                color: #e2e8f0;
                border: 1px solid rgba(75, 85, 99, 0.3);
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.output_display.setMaximumHeight(100)
        self.output_display.setReadOnly(True)
        self.output_display.setPlaceholderText("Command output will appear here...")
        self.output_display.hide()
        layout.addWidget(self.output_display)
        
        for field in self.input_fields.values():
            field.textChanged.connect(self.update_command_display)
        
        self.update_command_display()
        
        button_layout = QHBoxLayout()
        
        execute_btn = QPushButton("Execute")
        execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        execute_btn.clicked.connect(self.execute_command)
        
        copy_btn = QPushButton("Copy")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        copy_btn.clicked.connect(self.copy_command)
        
        button_layout.addWidget(execute_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)

    def get_final_command(self):
        command = self.command_data.get('command', '')
        for placeholder, field in self.input_fields.items():
            value = field.text().strip()
            if not value:
                value = field.placeholderText()
            command = command.replace(f"{{{placeholder}}}", value)
        
        command = command.replace("{USB_PATH}", self.usb_path)
        return command

    def update_command_display(self):
        final_command = self.get_final_command()
        self.command_display.setPlainText(final_command)

    def execute_command(self):
        try:
            command = self.get_final_command()
            
            self.output_display.show()
            self.output_display.setPlainText("Executing...")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.stdout or result.stderr:
                output = ""
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                output += f"\nReturn code: {result.returncode}"
                self.output_display.setPlainText(output)
            else:
                if result.returncode == 0:
                    self.output_display.setPlainText("Executed successfully. (No output)")
                else:
                    self.output_display.setPlainText(f"Command failed with return code: {result.returncode}")
                    
        except subprocess.TimeoutExpired:
            self.output_display.setPlainText("Command timed out after 30 seconds.")
        except subprocess.CalledProcessError as e:
            self.output_display.setPlainText(f"Command failed: {e}")
        except Exception as e:
            self.output_display.setPlainText(f"Error executing command: {str(e)}")

    def copy_command(self):
        command = self.get_final_command()
        QApplication.clipboard().setText(command)

class USBGeminiWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, user_input, usb_path):
        super().__init__()
        self.user_input = user_input
        self.usb_path = usb_path

    def run(self):
        try:
            client = genai.Client(api_key="AIzaSyAZL6dmWDySSUf3wz84gglAIqS1obZcJFA")
            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=self.user_input)],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text=f"""You are an AI assistant that generates bash commands for managing USB devices on Arch Linux. The current USB is mounted at: {self.usb_path}

Your responses must follow this exact format:

For commands that need NO customization:
{{  
  "command": "the_bash_command_here",  
  "description": "Brief explanation of the command.",
  "inputs": []
}} 

For commands that need customization:
{{  
  "command": "the_bash_command_with_placeholders",  
  "description": "Brief explanation of the command.",
  "inputs": [
    {{"name": "placeholder_name", "label": "Display Label", "default": "default_value"}},
    {{"name": "another_placeholder", "label": "Another Label", "default": ""}}
  ]
}}

Always include {{USB_PATH}} in commands to reference the USB mount point. Examples:

1. User asks: "List all files"
   You reply:  
{{  
  "command": "ls -la {{USB_PATH}}",  
  "description": "Lists all files in the USB drive.",
  "inputs": []
}}  

2. User asks: "Count Python files"
   You reply:  
{{  
  "command": "find {{USB_PATH}} -type f -name '*.py' | wc -l",  
  "description": "Counts Python files in USB drive.",
  "inputs": []
}}

3. User asks: "Sort files by type"
   You reply:  
{{  
  "command": "mkdir -p {{USB_PATH}}/sorted/{{CATEGORY}} && mv {{USB_PATH}}/*.{{EXTENSION}} {{USB_PATH}}/sorted/{{CATEGORY}}/",  
  "description": "Sorts files by type into categorized folders.",
  "inputs": [
    {{"name": "CATEGORY", "label": "Category Name", "default": "documents"}},
    {{"name": "EXTENSION", "label": "File Extension", "default": "pdf"}}
  ]
}}"""),
                ],
            )
            
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
            
            self.response_ready.emit(response_text)
        except Exception as e:
            self.error_occurred.emit(str(e))

class USBAgent(QMainWindow):
    def __init__(self, usb_path, usb_name):
        super().__init__()
        self.usb_path = usb_path
        self.usb_name = usb_name
        self.setup_ui()
        self.setup_animations()
        self.animate_in()

    def setup_ui(self):
        self.setWindowTitle(f"{self.usb_name} USB Agent")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 23, 42, 0.95),
                    stop:1 rgba(30, 41, 59, 0.95));
                border-radius: 15px;
                border: 2px solid rgba(99, 102, 241, 0.3);
            }
        """)
        
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"{self.usb_name} USB Agent")
        title_label.setStyleSheet("""
            color: #f1f5f9;
            font-size: 18px;
            font-weight: bold;
        """)
        
        self.quit_btn = QPushButton("×")
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.quit_btn.clicked.connect(self.animate_out)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.quit_btn)
        layout.addLayout(header_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(51, 65, 85, 0.5);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(99, 102, 241, 0.7);
                border-radius: 4px;
            }
        """)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(0)
        self.scroll_area.setMinimumHeight(0)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        
        layout.addWidget(self.scroll_area)
        
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("What would you like to do with this USB?")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(51, 65, 85, 0.8);
                color: #f1f5f9;
                border: 2px solid rgba(99, 102, 241, 0.5);
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #7c3aed);
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field, 4)
        input_layout.addWidget(self.send_btn, 1)
        layout.addLayout(input_layout)
        
        self.resize(500, 150)

    def setup_animations(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.pos_x = 20
        self.pos_y = 20
        
        self.move(self.pos_x, -self.height())

    def animate_in(self):
        self.anim_group = QParallelAnimationGroup()
        
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(500)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.pos_anim.setStartValue(QPoint(self.pos_x, -self.height()))
        self.pos_anim.setEndValue(QPoint(self.pos_x, self.pos_y))
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(500)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        
        self.anim_group.addAnimation(self.pos_anim)
        self.anim_group.addAnimation(self.opacity_anim)
        self.anim_group.start()

    def animate_out(self):
        self.anim_group = QParallelAnimationGroup()
        
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(500)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.InQuad)
        self.pos_anim.setEndValue(QPoint(self.pos_x, -self.height()))
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(500)
        self.opacity_anim.setEndValue(0)
        
        self.anim_group.addAnimation(self.pos_anim)
        self.anim_group.addAnimation(self.opacity_anim)
        self.anim_group.finished.connect(self.close)
        self.anim_group.start()

    def send_message(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Processing...")
        
        self.worker = USBGeminiWorker(user_input, self.usb_path)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, response):
        try:
            response = response.strip()
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                response = response[json_start:json_end]
            
            command_data = json.loads(response)
            self.add_command_widget(command_data)
        except json.JSONDecodeError:
            self.handle_error("Invalid response format from AI")
        except Exception as e:
            self.handle_error(f"Error processing response: {str(e)}")
        
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")

    def handle_error(self, error_message):
        error_data = {
            "command": "Error occurred",
            "description": f"Error: {error_message}"
        }
        self.add_command_widget(error_data)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")

    def add_command_widget(self, command_data):
        widget = USBCommandWidget(command_data, self.usb_path, {})
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, widget)
        
        if self.scroll_area.maximumHeight() == 0:
            self.expand_scroll_area()
        
        self.scroll_content.adjustSize()
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()))

    def expand_scroll_area(self):
        current_height = self.height()
        new_height = current_height + 300
        
        resize_anim = QPropertyAnimation(self, b"geometry")
        resize_anim.setDuration(300)
        resize_anim.setStartValue(self.geometry())
        resize_anim.setEndValue(self.geometry().adjusted(0, 0, 0, 300))
        resize_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        resize_anim.start()
        
        expand_anim = QPropertyAnimation(self.scroll_area, b"maximumHeight")
        expand_anim.setDuration(300)
        expand_anim.setStartValue(0)
        expand_anim.setEndValue(300)
        expand_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        min_height_anim = QPropertyAnimation(self.scroll_area, b"minimumHeight")
        min_height_anim.setDuration(300)
        min_height_anim.setStartValue(0)
        min_height_anim.setEndValue(300)
        min_height_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.expand_group = QParallelAnimationGroup()
        self.expand_group.addAnimation(resize_anim)
        self.expand_group.addAnimation(expand_anim)
        self.expand_group.addAnimation(min_height_anim)
        self.expand_group.start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python usb_agent.py <usb_path> <usb_name>")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    usb_path = sys.argv[1]
    usb_name = sys.argv[2]
    agent = USBAgent(usb_path, usb_name)
    agent.show()
    
    sys.exit(app.exec())