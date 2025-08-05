import sys
import json
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLineEdit, 
                            QScrollArea, QFrame, QLabel, QCheckBox, QComboBox,
                            QDialog, QDialogButtonBox, QFormLayout, QGroupBox)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QPoint, QEasingCurve, 
                         QParallelAnimationGroup, QThread, pyqtSignal, QTimer)
from PyQt6.QtGui import QFont, QPalette, QColor
from google import genai
from google.genai import types

class Translations:
    def __init__(self):
        self.translations = {
            'English': {
                'title': 'Arch Agent',
                'placeholder': 'What can I do for you?',
                'send': 'Send',
                'processing': 'Processing...',
                'execute': 'Execute',
                'copy': 'Copy',
                'settings': 'Settings',
                'agent_settings': 'Agent Settings',
                'full_agent_mode': 'Full Agent Mode',
                'danger_warning': '⚠️ Not recommended - gives AI full control, automatically executes commands without permission',
                'confirm_dangerous': 'Confirm dangerous commands (sudo, rm, etc.)',
                'interface_settings': 'Interface Settings',
                'language': 'Language:',
                'theme': 'Theme:',
                'auto_scroll': 'Auto-scroll to new commands',
                'dangerous_command': 'Dangerous Command',
                'dangerous_command_text': 'This command might be dangerous:\n{}\n\nDo you want to continue?',
                'no_description': 'No description',
                'executing': 'Executing...',
                'executed_successfully': 'Executed successfully. (No output)',
                'command_failed': 'Command failed with return code: {}',
                'timeout': 'Command timed out after 30 seconds.',
                'error_executing': 'Error executing command: {}',
                'invalid_response': 'Invalid response format from AI',
                'error_processing': 'Error processing response: {}',
                'error_occurred': 'Error occurred',
                'output_placeholder': 'Command output will appear here...'
            },
            'Turkish': {
                'title': 'Arch Agent',
                'placeholder': 'Sizin için ne yapabilirim?',
                'send': 'Gönder',
                'processing': 'İşleniyor...',
                'execute': 'Çalıştır',
                'copy': 'Kopyala',
                'settings': 'Ayarlar',
                'agent_settings': 'Agent Ayarları',
                'full_agent_mode': 'Tam Agent Modu',
                'danger_warning': '⚠️ Önerilmez - AI\'ya tam kontrol verir, komutları izinsiz otomatik çalıştırır',
                'confirm_dangerous': 'Tehlikeli komutları onayla (sudo, rm, vb.)',
                'interface_settings': 'Arayüz Ayarları',
                'language': 'Dil:',
                'theme': 'Tema:',
                'auto_scroll': 'Yeni komutlara otomatik kaydır',
                'dangerous_command': 'Tehlikeli Komut',
                'dangerous_command_text': 'Bu komut tehlikeli olabilir:\n{}\n\nDevam etmek istiyor musunuz?',
                'no_description': 'Açıklama yok',
                'executing': 'Çalıştırılıyor...',
                'executed_successfully': 'Başarıyla çalıştırıldı. (Çıktı yok)',
                'command_failed': 'Komut başarısız, dönüş kodu: {}',
                'timeout': 'Komut 30 saniye sonra zaman aşımına uğradı.',
                'error_executing': 'Komut çalıştırma hatası: {}',
                'invalid_response': 'AI\'dan geçersiz yanıt formatı',
                'error_processing': 'Yanıt işleme hatası: {}',
                'error_occurred': 'Hata oluştu',
                'output_placeholder': 'Komut çıktısı burada görünecek...'
            },
            'Spanish': {
                'title': 'Arch Agent',
                'placeholder': '¿Qué puedo hacer por ti?',
                'send': 'Enviar',
                'processing': 'Procesando...',
                'execute': 'Ejecutar',
                'copy': 'Copiar',
                'settings': 'Configuración',
                'agent_settings': 'Configuración del Agente',
                'full_agent_mode': 'Modo Agente Completo',
                'danger_warning': '⚠️ No recomendado - da control total a la IA, ejecuta comandos automáticamente sin permiso',
                'confirm_dangerous': 'Confirmar comandos peligrosos (sudo, rm, etc.)',
                'interface_settings': 'Configuración de Interfaz',
                'language': 'Idioma:',
                'theme': 'Tema:',
                'auto_scroll': 'Desplazamiento automático a nuevos comandos',
                'dangerous_command': 'Comando Peligroso',
                'dangerous_command_text': 'Este comando podría ser peligroso:\n{}\n\n¿Quieres continuar?',
                'no_description': 'Sin descripción',
                'executing': 'Ejecutando...',
                'executed_successfully': 'Ejecutado exitosamente. (Sin salida)',
                'command_failed': 'Comando falló con código de retorno: {}',
                'timeout': 'Comando agotó tiempo de espera después de 30 segundos.',
                'error_executing': 'Error ejecutando comando: {}',
                'invalid_response': 'Formato de respuesta inválido de la IA',
                'error_processing': 'Error procesando respuesta: {}',
                'error_occurred': 'Ocurrió un error',
                'output_placeholder': 'La salida del comando aparecerá aquí...'
            },
            'French': {
                'title': 'Arch Agent',
                'placeholder': 'Que puis-je faire pour vous?',
                'send': 'Envoyer',
                'processing': 'Traitement...',
                'execute': 'Exécuter',
                'copy': 'Copier',
                'settings': 'Paramètres',
                'agent_settings': 'Paramètres de l\'Agent',
                'full_agent_mode': 'Mode Agent Complet',
                'danger_warning': '⚠️ Non recommandé - donne le contrôle total à l\'IA, exécute automatiquement les commandes sans permission',
                'confirm_dangerous': 'Confirmer les commandes dangereuses (sudo, rm, etc.)',
                'interface_settings': 'Paramètres d\'Interface',
                'language': 'Langue:',
                'theme': 'Thème:',
                'auto_scroll': 'Défilement automatique vers les nouvelles commandes',
                'dangerous_command': 'Commande Dangereuse',
                'dangerous_command_text': 'Cette commande pourrait être dangereuse:\n{}\n\nVoulez-vous continuer?',
                'no_description': 'Aucune description',
                'executing': 'Exécution...',
                'executed_successfully': 'Exécuté avec succès. (Aucune sortie)',
                'command_failed': 'Commande échouée avec le code de retour: {}',
                'timeout': 'Commande expirée après 30 secondes.',
                'error_executing': 'Erreur d\'exécution de commande: {}',
                'invalid_response': 'Format de réponse invalide de l\'IA',
                'error_processing': 'Erreur de traitement de la réponse: {}',
                'error_occurred': 'Une erreur s\'est produite',
                'output_placeholder': 'La sortie de la commande apparaîtra ici...'
            },
            'German': {
                'title': 'Arch Agent',
                'placeholder': 'Was kann ich für Sie tun?',
                'send': 'Senden',
                'processing': 'Verarbeitung...',
                'execute': 'Ausführen',
                'copy': 'Kopieren',
                'settings': 'Einstellungen',
                'agent_settings': 'Agent-Einstellungen',
                'full_agent_mode': 'Vollständiger Agent-Modus',
                'danger_warning': '⚠️ Nicht empfohlen - gibt der KI volle Kontrolle, führt Befehle automatisch ohne Erlaubnis aus',
                'confirm_dangerous': 'Gefährliche Befehle bestätigen (sudo, rm, etc.)',
                'interface_settings': 'Benutzeroberflächen-Einstellungen',
                'language': 'Sprache:',
                'theme': 'Design:',
                'auto_scroll': 'Automatisch zu neuen Befehlen scrollen',
                'dangerous_command': 'Gefährlicher Befehl',
                'dangerous_command_text': 'Dieser Befehl könnte gefährlich sein:\n{}\n\nMöchten Sie fortfahren?',
                'no_description': 'Keine Beschreibung',
                'executing': 'Ausführung...',
                'executed_successfully': 'Erfolgreich ausgeführt. (Keine Ausgabe)',
                'command_failed': 'Befehl fehlgeschlagen mit Rückgabecode: {}',
                'timeout': 'Befehl nach 30 Sekunden abgelaufen.',
                'error_executing': 'Fehler beim Ausführen des Befehls: {}',
                'invalid_response': 'Ungültiges Antwortformat von der KI',
                'error_processing': 'Fehler bei der Antwortverarbeitung: {}',
                'error_occurred': 'Ein Fehler ist aufgetreten',
                'output_placeholder': 'Befehlsausgabe wird hier angezeigt...'
            },
            'Russian': {
                'title': 'Arch Agent',
                'placeholder': 'Что я могу для вас сделать?',
                'send': 'Отправить',
                'processing': 'Обработка...',
                'execute': 'Выполнить',
                'copy': 'Копировать',
                'settings': 'Настройки',
                'agent_settings': 'Настройки Агента',
                'full_agent_mode': 'Полный Режим Агента',
                'danger_warning': '⚠️ Не рекомендуется - дает ИИ полный контроль, автоматически выполняет команды без разрешения',
                'confirm_dangerous': 'Подтверждать опасные команды (sudo, rm, и т.д.)',
                'interface_settings': 'Настройки Интерфейса',
                'language': 'Язык:',
                'theme': 'Тема:',
                'auto_scroll': 'Автопрокрутка к новым командам',
                'dangerous_command': 'Опасная Команда',
                'dangerous_command_text': 'Эта команда может быть опасной:\n{}\n\nХотите продолжить?',
                'no_description': 'Нет описания',
                'executing': 'Выполнение...',
                'executed_successfully': 'Успешно выполнено. (Нет вывода)',
                'command_failed': 'Команда завершилась с кодом возврата: {}',
                'timeout': 'Команда превысила время ожидания через 30 секунд.',
                'error_executing': 'Ошибка выполнения команды: {}',
                'invalid_response': 'Неверный формат ответа от ИИ',
                'error_processing': 'Ошибка обработки ответа: {}',
                'error_occurred': 'Произошла ошибка',
                'output_placeholder': 'Вывод команды появится здесь...'
            },
            'Chinese': {
                'title': 'Arch Agent',
                'placeholder': '我能为您做什么？',
                'send': '发送',
                'processing': '处理中...',
                'execute': '执行',
                'copy': '复制',
                'settings': '设置',
                'agent_settings': '代理设置',
                'full_agent_mode': '完整代理模式',
                'danger_warning': '⚠️ 不推荐 - 给AI完全控制权，无需许可自动执行命令',
                'confirm_dangerous': '确认危险命令 (sudo, rm, 等)',
                'interface_settings': '界面设置',
                'language': '语言:',
                'theme': '主题:',
                'auto_scroll': '自动滚动到新命令',
                'dangerous_command': '危险命令',
                'dangerous_command_text': '此命令可能很危险:\n{}\n\n您想继续吗？',
                'no_description': '无描述',
                'executing': '执行中...',
                'executed_successfully': '执行成功。（无输出）',
                'command_failed': '命令失败，返回码: {}',
                'timeout': '命令在30秒后超时。',
                'error_executing': '执行命令错误: {}',
                'invalid_response': 'AI响应格式无效',
                'error_processing': '处理响应错误: {}',
                'error_occurred': '发生错误',
                'output_placeholder': '命令输出将在此显示...'
            }
        }
    
    def get(self, language, key):
        return self.translations.get(language, self.translations['English']).get(key, key)

class ThemeManager:
    @staticmethod
    def get_dark_theme():
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 23, 42, 0.95),
                    stop:1 rgba(30, 41, 59, 0.95));
                border-radius: 15px;
                border: 2px solid rgba(99, 102, 241, 0.3);
            }
        """
    
    @staticmethod
    def get_light_theme():
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 250, 252, 0.95),
                    stop:1 rgba(226, 232, 240, 0.95));
                border-radius: 15px;
                border: 2px solid rgba(99, 102, 241, 0.3);
            }
        """
    
    @staticmethod
    def get_dialog_style(is_dark=True):
        if is_dark:
            return """
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(15, 23, 42, 0.95),
                        stop:1 rgba(30, 41, 59, 0.95));
                    color: #f1f5f9;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid rgba(99, 102, 241, 0.3);
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #6366f1;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QCheckBox {
                    color: #e2e8f0;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #64748b;
                    border-radius: 3px;
                    background-color: rgba(51, 65, 85, 0.8);
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #6366f1;
                    border-radius: 3px;
                    background-color: #6366f1;
                }
                QComboBox {
                    background-color: rgba(51, 65, 85, 0.8);
                    color: #f1f5f9;
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    border-radius: 4px;
                    padding: 6px;
                    min-width: 150px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 8px solid #94a3b8;
                }
                QLabel {
                    color: #94a3b8;
                }
            """
        else:
            return """
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(248, 250, 252, 0.95),
                        stop:1 rgba(226, 232, 240, 0.95));
                    color: #1e293b;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid rgba(99, 102, 241, 0.3);
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #6366f1;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QCheckBox {
                    color: #334155;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #64748b;
                    border-radius: 3px;
                    background-color: rgba(241, 245, 249, 0.8);
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #6366f1;
                    border-radius: 3px;
                    background-color: #6366f1;
                }
                QComboBox {
                    background-color: rgba(241, 245, 249, 0.8);
                    color: #1e293b;
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    border-radius: 4px;
                    padding: 6px;
                    min-width: 150px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 8px solid #64748b;
                }
                QLabel {
                    color: #64748b;
                }
            """

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        self.default_settings = {
            'full_agent_mode': False,
            'language': 'English',
            'auto_scroll': True,
            'confirm_dangerous_commands': True,
            'theme': 'Dark'
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    return {**self.default_settings, **loaded}
            return self.default_settings.copy()
        except:
            return self.default_settings.copy()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
    
    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

class SettingsDialog(QDialog):
    def __init__(self, settings_manager, translations, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.translations = translations
        self.setup_ui()
        
    def setup_ui(self):
        lang = self.settings_manager.get('language')
        self.setWindowTitle(self.translations.get(lang, 'settings'))
        self.setModal(True)
        
        is_dark = self.settings_manager.get('theme') in ['Dark', 'Auto']
        self.setStyleSheet(ThemeManager.get_dialog_style(is_dark))
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        agent_group = QGroupBox(self.translations.get(lang, 'agent_settings'))
        agent_layout = QVBoxLayout(agent_group)
        
        self.full_agent_cb = QCheckBox(self.translations.get(lang, 'full_agent_mode'))
        self.full_agent_cb.setChecked(self.settings_manager.get('full_agent_mode'))
        agent_layout.addWidget(self.full_agent_cb)
        
        danger_label = QLabel(self.translations.get(lang, 'danger_warning'))
        danger_label.setStyleSheet("color: #fbbf24; font-size: 11px; margin-left: 23px;")
        danger_label.setWordWrap(True)
        agent_layout.addWidget(danger_label)
        
        self.confirm_dangerous_cb = QCheckBox(self.translations.get(lang, 'confirm_dangerous'))
        self.confirm_dangerous_cb.setChecked(self.settings_manager.get('confirm_dangerous_commands'))
        agent_layout.addWidget(self.confirm_dangerous_cb)
        
        layout.addWidget(agent_group)
        
        ui_group = QGroupBox(self.translations.get(lang, 'interface_settings'))
        ui_layout = QFormLayout(ui_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(['English', 'Turkish', 'Spanish', 'French', 'German', 'Russian', 'Chinese'])
        self.language_combo.setCurrentText(self.settings_manager.get('language'))
        ui_layout.addRow(self.translations.get(lang, 'language'), self.language_combo)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light', 'Auto'])
        self.theme_combo.setCurrentText(self.settings_manager.get('theme'))
        ui_layout.addRow(self.translations.get(lang, 'theme'), self.theme_combo)
        
        self.auto_scroll_cb = QCheckBox(self.translations.get(lang, 'auto_scroll'))
        self.auto_scroll_cb.setChecked(self.settings_manager.get('auto_scroll'))
        ui_layout.addRow("", self.auto_scroll_cb)
        
        layout.addWidget(ui_group)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.resize(400, 300)
    
    def accept(self):
        self.settings_manager.set('full_agent_mode', self.full_agent_cb.isChecked())
        self.settings_manager.set('language', self.language_combo.currentText())
        self.settings_manager.set('theme', self.theme_combo.currentText())
        self.settings_manager.set('auto_scroll', self.auto_scroll_cb.isChecked())
        self.settings_manager.set('confirm_dangerous_commands', self.confirm_dangerous_cb.isChecked())
        super().accept()

class GeminiWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, user_input, language='English'):
        super().__init__()
        self.user_input = user_input
        self.language = language

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
            
            language_instruction = f"Respond in {self.language}. " if self.language != 'English' else ""
            
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text=f"""{language_instruction}You are an AI assistant that generates bash commands for Arch Linux (e.g., package management with `pacman`). Your responses must follow this exact format:

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

Examples:
1. User asks: "Install Python and pip."  
   You reply:  
{{  
  "command": "sudo pacman -S python python-pip",  
  "description": "Installs Python and pip.",
  "inputs": []
}}  

2. User asks: "Create a directory"  
   You reply:  
{{  
  "command": "mkdir {{DIRECTORY_NAME}}",  
  "description": "Creates a new directory.",
  "inputs": [
    {{"name": "DIRECTORY_NAME", "label": "Directory Name", "default": "new_folder"}}
  ]
}}

3. User asks: "Install a package"  
   You reply:  
{{  
  "command": "sudo pacman -S {{PACKAGE_NAME}}",  
  "description": "Installs the specified package.",
  "inputs": [
    {{"name": "PACKAGE_NAME", "label": "Package Name", "default": ""}}
  ]
}}

4. User asks: "Create user with home directory"  
   You reply:  
{{  
  "command": "sudo useradd -m -s {{SHELL}} {{USERNAME}}",  
  "description": "Creates a new user with home directory.",
  "inputs": [
    {{"name": "USERNAME", "label": "Username", "default": "newuser"}},
    {{"name": "SHELL", "label": "Default Shell", "default": "/bin/bash"}}
  ]
}}

Use placeholders in {{PLACEHOLDER_NAME}} format. Only add inputs array when the command genuinely needs customization."""),
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

class CommandWidget(QFrame):
    def __init__(self, command_data, settings_manager, translations):
        super().__init__()
        self.command_data = command_data
        self.settings_manager = settings_manager
        self.translations = translations
        self.input_fields = {}
        self.setup_ui()

    def get_theme_styles(self):
        is_dark = self.settings_manager.get('theme') in ['Dark', 'Auto']
        if is_dark:
            return {
                'frame': """
                    QFrame {
                        background-color: rgba(45, 55, 72, 0.9);
                        border-radius: 8px;
                        border: 1px solid rgba(99, 102, 241, 0.3);
                        margin: 5px;
                        padding: 10px;
                    }
                """,
                'desc_label': """
                    color: #e2e8f0;
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                """,
                'inputs_frame': """
                    QFrame {
                        background-color: rgba(30, 41, 59, 0.6);
                        border-radius: 6px;
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        padding: 10px;
                        margin: 5px 0px;
                    }
                """,
                'input_label': """
                    color: #94a3b8;
                    font-size: 12px;
                    min-width: 100px;
                """,
                'input_field': """
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
                """,
                'command_text': """
                    QTextEdit {
                        background-color: rgba(30, 41, 59, 0.8);
                        color: #10b981;
                        border: 1px solid rgba(16, 185, 129, 0.3);
                        border-radius: 4px;
                        padding: 8px;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                    }
                """,
                'output_display': """
                    QTextEdit {
                        background-color: rgba(20, 20, 30, 0.9);
                        color: #e2e8f0;
                        border: 1px solid rgba(75, 85, 99, 0.3);
                        border-radius: 4px;
                        padding: 8px;
                        font-family: 'Courier New', monospace;
                        font-size: 11px;
                    }
                """
            }
        else:
            return {
                'frame': """
                    QFrame {
                        background-color: rgba(241, 245, 249, 0.9);
                        border-radius: 8px;
                        border: 1px solid rgba(99, 102, 241, 0.3);
                        margin: 5px;
                        padding: 10px;
                    }
                """,
                'desc_label': """
                    color: #1e293b;
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                """,
                'inputs_frame': """
                    QFrame {
                        background-color: rgba(226, 232, 240, 0.6);
                        border-radius: 6px;
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        padding: 10px;
                        margin: 5px 0px;
                    }
                """,
                'input_label': """
                    color: #64748b;
                    font-size: 12px;
                    min-width: 100px;
                """,
                'input_field': """
                    QLineEdit {
                        background-color: rgba(248, 250, 252, 0.8);
                        color: #1e293b;
                        border: 1px solid rgba(99, 102, 241, 0.3);
                        border-radius: 4px;
                        padding: 6px;
                        font-size: 12px;
                    }
                    QLineEdit:focus {
                        border-color: #6366f1;
                    }
                """,
                'command_text': """
                    QTextEdit {
                        background-color: rgba(226, 232, 240, 0.8);
                        color: #059669;
                        border: 1px solid rgba(16, 185, 129, 0.3);
                        border-radius: 4px;
                        padding: 8px;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                    }
                """,
                'output_display': """
                    QTextEdit {
                        background-color: rgba(248, 250, 252, 0.9);
                        color: #334155;
                        border: 1px solid rgba(75, 85, 99, 0.3);
                        border-radius: 4px;
                        padding: 8px;
                        font-family: 'Courier New', monospace;
                        font-size: 11px;
                    }
                """
            }

    def setup_ui(self):
        lang = self.settings_manager.get('language')
        styles = self.get_theme_styles()
        
        self.setStyleSheet(styles['frame'])
        
        layout = QVBoxLayout(self)
        
        desc_label = QLabel(self.command_data.get('description', self.translations.get(lang, 'no_description')))
        desc_label.setStyleSheet(styles['desc_label'])
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        inputs = self.command_data.get('inputs', [])
        if inputs:
            inputs_frame = QFrame()
            inputs_frame.setStyleSheet(styles['inputs_frame'])
            inputs_layout = QVBoxLayout(inputs_frame)
            
            for input_config in inputs:
                input_row = QHBoxLayout()
                
                label = QLabel(input_config.get('label', 'Input') + ":")
                label.setStyleSheet(styles['input_label'])
                
                input_field = QLineEdit()
                input_field.setText(input_config.get('default', ''))
                input_field.setStyleSheet(styles['input_field'])
                
                self.input_fields[input_config['name']] = input_field
                
                input_row.addWidget(label)
                input_row.addWidget(input_field, 1)
                inputs_layout.addLayout(input_row)
            
            layout.addWidget(inputs_frame)
        
        command_text = QTextEdit()
        command_text.setStyleSheet(styles['command_text'])
        command_text.setMaximumHeight(80)
        command_text.setReadOnly(True)
        self.command_display = command_text
        layout.addWidget(command_text)
        
        self.output_display = QTextEdit()
        self.output_display.setStyleSheet(styles['output_display'])
        self.output_display.setMaximumHeight(100)
        self.output_display.setReadOnly(True)
        self.output_display.setPlaceholderText(self.translations.get(lang, 'output_placeholder'))
        self.output_display.hide()
        layout.addWidget(self.output_display)
        
        for field in self.input_fields.values():
            field.textChanged.connect(self.update_command_display)
        
        self.update_command_display()
        
        button_layout = QHBoxLayout()
        
        execute_btn = QPushButton(self.translations.get(lang, 'execute'))
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
        
        copy_btn = QPushButton(self.translations.get(lang, 'copy'))
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
        
        if self.settings_manager.get('full_agent_mode'):
            QTimer.singleShot(100, self.execute_command)

    def get_final_command(self):
        command = self.command_data.get('command', '')
        for placeholder, field in self.input_fields.items():
            value = field.text().strip()
            if not value:
                value = field.placeholderText()
            command = command.replace(f"{{{placeholder}}}", value)
        return command

    def update_command_display(self):
        final_command = self.get_final_command()
        self.command_display.setPlainText(final_command)

    def is_dangerous_command(self, command):
        dangerous_patterns = ['sudo', 'rm', 'dd if=', 'mkfs', 'fdisk', 'parted', 'systemctl stop', 'systemctl disable', 'chmod 777', 'chown -R']
        return any(pattern in command.lower() for pattern in dangerous_patterns)

    def execute_command(self):
        try:
            command = self.get_final_command()
            lang = self.settings_manager.get('language')
            
            if self.settings_manager.get('confirm_dangerous_commands') and self.is_dangerous_command(command):
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self, 
                    self.translations.get(lang, 'dangerous_command'), 
                    self.translations.get(lang, 'dangerous_command_text').format(command),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.output_display.show()
            self.output_display.setPlainText(self.translations.get(lang, 'executing'))
            
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
                    self.output_display.setPlainText(self.translations.get(lang, 'executed_successfully'))
                else:
                    self.output_display.setPlainText(self.translations.get(lang, 'command_failed').format(result.returncode))
                    
        except subprocess.TimeoutExpired:
            self.output_display.setPlainText(self.translations.get(lang, 'timeout'))
        except subprocess.CalledProcessError as e:
            self.output_display.setPlainText(f"Command failed: {e}")
        except Exception as e:
            self.output_display.setPlainText(self.translations.get(lang, 'error_executing').format(str(e)))

    def copy_command(self):
        command = self.get_final_command()
        QApplication.clipboard().setText(command)

class ArchChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.translations = Translations()
        self.setup_ui()
        self.setup_animations()
        self.animate_in()

    def get_main_theme_style(self):
        theme = self.settings_manager.get('theme')
        if theme == 'Light':
            return ThemeManager.get_light_theme()
        else:
            return ThemeManager.get_dark_theme()

    def get_input_styles(self):
        is_dark = self.settings_manager.get('theme') in ['Dark', 'Auto']
        if is_dark:
            return {
                'input_field': """
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
                """,
                'title_color': '#f1f5f9',
                'scroll_area': """
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
                """
            }
        else:
            return {
                'input_field': """
                    QLineEdit {
                        background-color: rgba(248, 250, 252, 0.8);
                        color: #1e293b;
                        border: 2px solid rgba(99, 102, 241, 0.5);
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                    }
                    QLineEdit:focus {
                        border-color: #6366f1;
                    }
                """,
                'title_color': '#1e293b',
                'scroll_area': """
                    QScrollArea {
                        border: none;
                        background-color: transparent;
                    }
                    QScrollBar:vertical {
                        background-color: rgba(203, 213, 225, 0.5);
                        width: 8px;
                        border-radius: 4px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: rgba(99, 102, 241, 0.7);
                        border-radius: 4px;
                    }
                """
            }

    def setup_ui(self):
        lang = self.settings_manager.get('language')
        self.setWindowTitle(self.translations.get(lang, 'title'))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet(self.get_main_theme_style())
        
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.translations.get(lang, 'title'))
        styles = self.get_input_styles()
        title_label.setStyleSheet(f"""
            color: {styles['title_color']};
            font-size: 18px;
            font-weight: bold;
        """)
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
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
                background-color: #4f46e5;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        
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
        header_layout.addWidget(self.settings_btn)
        header_layout.addWidget(self.quit_btn)
        layout.addLayout(header_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet(styles['scroll_area'])
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
        self.input_field.setPlaceholderText(self.translations.get(lang, 'placeholder'))
        self.input_field.setStyleSheet(styles['input_field'])
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton(self.translations.get(lang, 'send'))
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
        
        self.resize(600, 150)

    def refresh_ui(self):
        lang = self.settings_manager.get('language')
        self.setWindowTitle(self.translations.get(lang, 'title'))
        
        self.main_widget.setStyleSheet(self.get_main_theme_style())
        
        styles = self.get_input_styles()
        self.input_field.setStyleSheet(styles['input_field'])
        self.input_field.setPlaceholderText(self.translations.get(lang, 'placeholder'))
        
        self.scroll_area.setStyleSheet(styles['scroll_area'])
        
        self.send_btn.setText(self.translations.get(lang, 'send'))
        
        title_label = self.findChild(QLabel)
        if title_label:
            title_label.setText(self.translations.get(lang, 'title'))
            title_label.setStyleSheet(f"""
                color: {styles['title_color']};
                font-size: 18px;
                font-weight: bold;
            """)

    def open_settings(self):
        dialog = SettingsDialog(self.settings_manager, self.translations, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_ui()

    def extract_json_from_response(self, response):
        response = response.strip()
        
        if response.startswith('```json') and response.endswith('```'):
            response = response[7:-3].strip()
        elif response.startswith('```') and response.endswith('```'):
            response = response[3:-3].strip()
        
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            response = response[json_start:json_end]
        
        return response

    def setup_animations(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.center_x = (screen_geometry.width() - self.width()) // 2
        self.center_y = (screen_geometry.height() - self.height()) // 2
        self.bottom_y = screen_geometry.height()
        
        self.move(self.center_x, self.bottom_y)

    def animate_in(self):
        self.anim_group = QParallelAnimationGroup()
        
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(800)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.pos_anim.setStartValue(QPoint(self.center_x, self.bottom_y))
        self.pos_anim.setEndValue(QPoint(self.center_x, self.center_y))
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(600)
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
        self.pos_anim.setEndValue(QPoint(self.center_x, self.bottom_y))
        
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
        
        lang = self.settings_manager.get('language')
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        self.send_btn.setText(self.translations.get(lang, 'processing'))
        
        self.worker = GeminiWorker(user_input, self.settings_manager.get('language'))
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, response):
        print("=== RAW AI RESPONSE ===")
        print(response)
        print("=== END RAW RESPONSE ===")
        
        lang = self.settings_manager.get('language')
        
        try:
            cleaned_response = self.extract_json_from_response(response)
            command_data = json.loads(cleaned_response)
            self.add_command_widget(command_data)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Cleaned response was: {cleaned_response}")
            self.handle_error(self.translations.get(lang, 'invalid_response'))
        except Exception as e:
            print(f"Other error: {e}")
            self.handle_error(self.translations.get(lang, 'error_processing').format(str(e)))
        
        self.send_btn.setEnabled(True)
        self.send_btn.setText(self.translations.get(lang, 'send'))

    def handle_error(self, error_message):
        lang = self.settings_manager.get('language')
        error_data = {
            "command": self.translations.get(lang, 'error_occurred'),
            "description": f"Error: {error_message}"
        }
        self.add_command_widget(error_data)
        self.send_btn.setEnabled(True)
        self.send_btn.setText(self.translations.get(lang, 'send'))

    def add_command_widget(self, command_data):
        widget = CommandWidget(command_data, self.settings_manager, self.translations)
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, widget)
        
        if self.scroll_area.maximumHeight() == 0:
            self.expand_scroll_area()
        
        self.scroll_content.adjustSize()
        
        if self.settings_manager.get('auto_scroll'):
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
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    bot = ArchChatBot()
    bot.show()
    
    sys.exit(app.exec())
