import sys
import os
import json
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QAction, QDialog, QPushButton, QHBoxLayout, QComboBox, QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QSplitter, QRadioButton, QButtonGroup, QSpinBox, QGroupBox, QFormLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QHBoxLayout

class Translator:
    """
    Handles application translations using JSON language files.
    Loads available languages from the lang directory and provides translation lookup.
    """
    def __init__(self, lang_dir=None, default_lang='en'):
        """
        Initialize the Translator.
        :param lang_dir: Directory containing language JSON files.
        :param default_lang: Default language code.
        """
        if lang_dir is None:
            # Absolute path to the lang folder inside frontend
            base_dir = os.path.dirname(os.path.abspath(__file__))
            lang_dir = os.path.join(base_dir, 'lang')
        self.lang_dir = lang_dir
        self.translations = {}
        self.current_lang = default_lang
        self.load_languages()
        self.set_language(default_lang)

    def load_languages(self):
        """
        Load available languages from the language directory.
        """
        self.available_langs = []
        if not os.path.exists(self.lang_dir):
            os.makedirs(self.lang_dir)
        for fname in os.listdir(self.lang_dir):
            if fname.endswith('.json'):
                lang = fname[:-5]
                self.available_langs.append(lang)

    def set_language(self, lang):
        """
        Set the current language and load its translations.
        :param lang: Language code to set.
        """
        try:
            with open(os.path.join(self.lang_dir, f'{lang}.json'), encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_lang = lang
        except Exception:
            self.translations = {}
            self.current_lang = lang

    def t(self, key):
        """
        Translate a key using the current language.
        :param key: The translation key.
        :return: Translated string or the key if not found.
        """
        return self.translations.get(key, key)

class RemoteControlTab(QWidget):
    """
    Tab for remote control of instruments.
    """
    def __init__(self):
        """
        Initialize the remote control tab with a label.
        """
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel('Remote control of instruments')  # Translated at runtime
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_translation(self, translator):
        """
        Update the label text according to the current language.
        :param translator: Translator instance.
        """
        self.label.setText(translator.t('remote_control'))

class SettingsDialog(QDialog):
    """
    Dialog for application settings (theme, language, advanced naming).
    Singleton pattern is used to ensure only one instance exists.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingsDialog, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    def __init__(self, parent=None, translator=None):
        """
        Initialize the settings dialog with theme, language, and naming options.
        :param parent: Parent widget.
        :param translator: Translator instance.
        """
        if self._initialized:
            return
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.t('settings'))
        self.setModal(True)
        layout = QVBoxLayout()
        # Dark theme toggle
        dark_layout = QHBoxLayout()
        self.dark_theme_switch = QCheckBox(self.translator.t('enable_dark_theme'))
        self.dark_theme_switch.stateChanged.connect(self.toggle_dark_theme)
        dark_layout.addWidget(self.dark_theme_switch)
        layout.addLayout(dark_layout)
        # Language dropdown
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel(self.translator.t('language')+':')
        self.lang_combo = QComboBox()
        # Reload languages from the correct path
        lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.translator.lang_dir)
        self.translator.lang_dir = lang_dir
        self.translator.load_languages()
        self.lang_combo.clear()
        self.lang_combo.addItems(self.translator.available_langs)
        self.lang_combo.setCurrentText(self.translator.current_lang)
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        # Advanced naming settings
        self.naming_group = QVBoxLayout()
        self.adv_naming_checkbox = QCheckBox(self.translator.t('enable_advanced_naming'))
        self.adv_naming_checkbox.stateChanged.connect(self.toggle_advanced_naming)
        self.naming_group.addWidget(self.adv_naming_checkbox)
        # File type toggles
        self.inst_toggle = QCheckBox(self.translator.t('advanced_naming_inst'))
        self.eff_toggle = QCheckBox(self.translator.t('advanced_naming_eff'))
        self.was_toggle = QCheckBox(self.translator.t('advanced_naming_was'))
        self.naming_group.addWidget(self.inst_toggle)
        self.naming_group.addWidget(self.eff_toggle)
        self.naming_group.addWidget(self.was_toggle)
        layout.addLayout(self.naming_group)
        # Apply button
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton(self.translator.t('apply'))
        self.apply_btn.clicked.connect(self.apply_settings)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self._initialized = True
        self.load_settings()
        self.toggle_advanced_naming(self.adv_naming_checkbox.isChecked())

    def toggle_dark_theme(self, state):
        """
        Enable or disable dark theme.
        :param state: Qt.Checked or Qt.Unchecked
        """
        if state == Qt.Checked:
            self.parent().set_dark_theme()
        else:
            self.parent().setStyleSheet("")
        self.save_settings()

    def toggle_advanced_naming(self, state):
        """
        Enable or disable advanced naming toggles.
        :param state: Qt.Checked or Qt.Unchecked
        """
        enabled = state == Qt.Checked
        self.inst_toggle.setEnabled(enabled)
        self.eff_toggle.setEnabled(enabled)
        self.was_toggle.setEnabled(enabled)
        self.save_settings()

    def change_language(self, lang):
        """
        Change the application language and update translations.
        :param lang: Language code.
        """
        self.translator.set_language(lang)
        self.lang_label.setText(self.translator.t('language')+':')
        self.parent().update_translations()
        self.save_settings()
        self.close()

    def save_settings(self):
        """
        Save current settings to QSettings.
        """
        settings = QSettings('LabAutomation', 'App')
        settings.setValue('language', self.translator.current_lang)
        settings.setValue('dark_theme', self.dark_theme_switch.isChecked())
        settings.setValue('advanced_naming', self.adv_naming_checkbox.isChecked())
        settings.setValue('advanced_naming_inst', self.inst_toggle.isChecked())
        settings.setValue('advanced_naming_eff', self.eff_toggle.isChecked())
        settings.setValue('advanced_naming_was', self.was_toggle.isChecked())

    def load_settings(self):
        """
        Load settings from QSettings and update UI accordingly.
        """
        settings = QSettings('LabAutomation', 'App')
        lang = settings.value('language', self.translator.current_lang)
        dark = settings.value('dark_theme', False, type=bool)
        adv_naming = settings.value('advanced_naming', False, type=bool)
        adv_inst = settings.value('advanced_naming_inst', False, type=bool)
        adv_eff = settings.value('advanced_naming_eff', False, type=bool)
        adv_was = settings.value('advanced_naming_was', False, type=bool)
        self.lang_combo.setCurrentText(lang)
        self.dark_theme_switch.setChecked(dark)
        self.adv_naming_checkbox.setChecked(adv_naming)
        self.inst_toggle.setChecked(adv_inst)
        self.eff_toggle.setChecked(adv_eff)
        self.was_toggle.setChecked(adv_was)
        self.toggle_advanced_naming(adv_naming)

    def apply_settings(self):
        """
        Apply and save settings, update main window, and close the dialog.
        """
        self.save_settings()
        self.parent().load_settings()
        self.parent().update_translations()
        self.close()

class MainWindow(QMainWindow):
    """
    Main application window. Handles project management, file operations, and main UI.
    """
    def __init__(self):
        """
        Initialize the main window, load app info, and set up UI components.
        """
        # Load app info from JSON
        appinfo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'appinfo.json')
        with open(appinfo_path, encoding='utf-8') as f:
            self.appinfo = json.load(f)
        self.translator = Translator()
        super().__init__()
        self.setWindowTitle(self.appinfo.get('app_name', 'Lab Automation'))
        self.tabs = QTabWidget()
        self.remote_tab = RemoteControlTab()
        self.tabs.addTab(self.remote_tab, self.translator.t('remote_control'))
        self.project_files_list = QListWidget()
        # Layout: tabs on the left, file list on the right
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.project_files_list, 1)
        main_layout.addWidget(self.tabs, 3)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.current_project_dir = None
        self.current_project_data = None
        self.init_menu()
        self.settings_dialog = SettingsDialog(self, self.translator)
        self.load_settings()
        self.update_translations()
        self.project_files_list.itemDoubleClicked.connect(self.edit_project_file)
        # Always start maximized/fullscreen
        self.showMaximized()

    def init_menu(self):
        """
        Initialize the menubar and its menus/actions.
        """
        menubar = self.menuBar()
        menubar.clear()
        # Project menu
        project_menu = menubar.addMenu(self.translator.t('project'))
        new_project_action = QAction(self.translator.t('create_new_project'), self)
        new_project_action.triggered.connect(self.create_new_project)
        project_menu.addAction(new_project_action)
        open_project_action = QAction(self.translator.t('open_project'), self)
        open_project_action.triggered.connect(self.open_project)
        project_menu.addAction(open_project_action)
        add_file_action = QAction(self.translator.t('add_file'), self)
        add_file_action.triggered.connect(self.add_project_file)
        project_menu.addAction(add_file_action)
        # New entry: add existing file
        add_existing_action = QAction(self.translator.t('add_existing_file'), self)
        add_existing_action.triggered.connect(self.add_existing_file)
        project_menu.addAction(add_existing_action)
        # Settings menu
        settings_menu = menubar.addMenu(self.translator.t('settings'))
        settings_action = QAction(self.translator.t('open_settings'), self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        db_action = QAction(self.translator.t('database_settings'), self)
        db_action.triggered.connect(self.open_db_settings)
        settings_menu.addAction(db_action)
        # Help menu
        help_menu = menubar.addMenu(self.translator.t('help'))
        info_action = QAction(self.translator.t('about_software'), self)
        info_action.triggered.connect(self.show_software_info)
        help_menu.addAction(info_action)

    def show_software_info(self):
        """
        Show information about the software in a message box.
        """
        from PyQt5.QtWidgets import QMessageBox
        info = self.appinfo
        text = f"<b>{info.get('app_name','')}</b><br>Version: {info.get('version','')}<br>Author: {info.get('author','')}<br>"
        repo = info.get('repository','')
        if repo:
            text += f"<br><a href='{repo}'>Repository</a>"
        msg = QMessageBox(self)
        msg.setWindowTitle(self.translator.t('about_software'))
        msg.setTextFormat(Qt.RichText)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def create_new_project(self):
        """
        Create a new project: select folder, enter project name, and create .json and .inst files.
        """
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
        import datetime
        dir_path = QFileDialog.getExistingDirectory(self, self.translator.t('select_project_folder'))
        if dir_path:
            project_name, ok = QInputDialog.getText(self, self.translator.t('project'), self.translator.t('enter_project_name'))
            if not ok or not project_name.strip():
                return
            import uuid
            project_id = str(uuid.uuid4())
            now = datetime.datetime.now().isoformat()
            # Load naming settings
            settings = QSettings('LabAutomation', 'App')
            adv_naming = settings.value('advanced_naming', False, type=bool)
            adv_inst = settings.value('advanced_naming_inst', False, type=bool)
            # .inst file name = project name
            inst_base = project_name.strip()
            if adv_naming and adv_inst:
                inst_file = f"{inst_base}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.inst"
            else:
                inst_file = f"{inst_base}.inst"
            # .json file name = project name
            json_file = f"{inst_base}.json"
            project_data = {
                "project_id": project_id,
                "created_at": now,
                "last_opened": now,
                "project_name": project_name.strip(),
                "eff_files": [],
                "inst_file": inst_file,
                "was_files": []
            }
            project_file = os.path.join(dir_path, json_file)
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            inst_data = {"instruments": []}
            inst_path = os.path.join(dir_path, inst_file)
            with open(inst_path, 'w', encoding='utf-8') as f:
                json.dump(inst_data, f, indent=2)
            self.current_project_dir = dir_path
            self.current_project_data = project_data
            self.refresh_project_files()
            QMessageBox.information(self, self.translator.t('project'), self.translator.t('project_created')+f'\n{dir_path}')
            # Ask if add file now
            reply = QMessageBox.question(self, self.translator.t('add_file'), self.translator.t('add_file_now'), QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.add_project_file()

    def open_project(self):
        """
        Open an existing project: select .json file and load its data.
        """
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        file_path, _ = QFileDialog.getOpenFileName(self, self.translator.t('open_project'), '', 'Project Files (*.json)')
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                self.current_project_dir = os.path.dirname(file_path)
                self.current_project_data = project_data
                self.refresh_project_files()
                QMessageBox.information(self, self.translator.t('project'), self.translator.t('project_opened')+f'\n{project_data.get("project_name", "")}')
            except Exception as e:
                QMessageBox.warning(self, self.translator.t('project'), str(e))

    def refresh_project_files(self):
        """
        Refresh the list of project files displayed in the UI.
        """
        self.project_files_list.clear()
        if not self.current_project_dir or not self.current_project_data:
            return
        # Project files list
        files = []
        files.append(self.current_project_data.get('inst_file'))
        files += self.current_project_data.get('eff_files', [])
        files += self.current_project_data.get('was_files', [])
        for f in files:
            if f:
                item = QListWidgetItem(f)
                self.project_files_list.addItem(item)

    def add_project_file(self):
        """
        Add a new project file (.eff or .was) using the AddFileDialog.
        """
        dlg = AddFileDialog(self, self.translator)
        if dlg.exec_() == QDialog.Accepted:
            if self.current_project_data and self.current_project_dir:
                file_type = dlg.type_combo.currentData()
                file_name = dlg.name_edit.text().strip()
                import datetime
                now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                # Load naming settings
                settings = QSettings('LabAutomation', 'App')
                adv_naming = settings.value('advanced_naming', False, type=bool)
                adv_eff = settings.value('advanced_naming_eff', False, type=bool)
                adv_was = settings.value('advanced_naming_was', False, type=bool)
                new_file = None
                if file_type == '.eff':
                    if adv_naming and adv_eff:
                        eff_file = f"{file_name}_{now}.eff"
                    else:
                        eff_file = f"{file_name}.eff"
                    eff_data = {"type": "efficiency", "data": {}}
                    with open(os.path.join(self.current_project_dir, eff_file), 'w', encoding='utf-8') as f:
                        json.dump(eff_data, f, indent=2)
                    if eff_file not in self.current_project_data['eff_files']:
                        self.current_project_data['eff_files'].append(eff_file)
                    new_file = eff_file
                elif file_type == '.was':
                    if adv_naming and adv_was:
                        was_file = f"{file_name}_{now}.was"
                    else:
                        was_file = f"{file_name}.was"
                    was_data = {"type": "oscilloscope_settings", "settings": {}}
                    with open(os.path.join(self.current_project_dir, was_file), 'w', encoding='utf-8') as f:
                        json.dump(was_data, f, indent=2)
                    if was_file not in self.current_project_data['was_files']:
                        self.current_project_data['was_files'].append(was_file)
                    new_file = was_file
                # Save project update
                # Search for the project json file by project name
                json_file = f"{self.current_project_data['project_name']}.json"
                json_path = os.path.join(self.current_project_dir, json_file)
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_project_data, f, indent=2)
                self.refresh_project_files()

    def add_existing_file(self):
        """
        Add an existing file (.eff or .was) to the project from the file system.
        """
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        if not self.current_project_dir or not self.current_project_data:
            QMessageBox.warning(self, self.translator.t('project'), self.translator.t('no_project_open'))
            return
        file_path, _ = QFileDialog.getOpenFileName(self, self.translator.t('add_existing_file'), self.current_project_dir, 'Eff (*.eff);;Was (*.was)')
        if not file_path:
            return
        fname = os.path.basename(file_path)
        if fname.endswith('.eff'):
            if fname not in self.current_project_data['eff_files']:
                self.current_project_data['eff_files'].append(fname)
        elif fname.endswith('.was'):
            if fname not in self.current_project_data['was_files']:
                self.current_project_data['was_files'].append(fname)
        else:
            QMessageBox.warning(self, self.translator.t('add_existing_file'), self.translator.t('file_type_not_allowed'))
            return
        # Update project json file
        project_file = [f for f in os.listdir(self.current_project_dir) if f.endswith('.json') and self.current_project_data['project_id'] in open(os.path.join(self.current_project_dir, f), encoding='utf-8').read()]
        if project_file:
            with open(os.path.join(self.current_project_dir, project_file[0]), 'w', encoding='utf-8') as f:
                json.dump(self.current_project_data, f, indent=2)
        self.refresh_project_files()

    def open_settings(self):
        """
        Open the settings dialog to configure application preferences.
        """
        self.settings_dialog.load_settings()
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def open_db_settings(self):
        """
        Open the database settings dialog to configure database connection parameters.
        """
        dlg = DatabaseDialog(self, self.translator)
        dlg.exec_()

    def set_dark_theme(self):
        """
        Set the application to dark theme using a predefined stylesheet.
        """
        dark_stylesheet = """
            QWidget { background-color: #232629; color: #f0f0f0; }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background: #232629; color: #f0f0f0; }
            QMenuBar { background-color: #232629; color: #f0f0f0; }
            QMenu { background-color: #232629; color: #f0f0f0; }
            QPushButton { background-color: #444; color: #f0f0f0; border: 1px solid #666; }
        """
        self.setStyleSheet(dark_stylesheet)
        settings = QSettings('LabAutomation', 'App')
        settings.setValue('dark_theme', True)

    def load_settings(self):
        """
        Load settings from QSettings and apply them to the application.
        """
        settings = QSettings('LabAutomation', 'App')
        lang = settings.value('language', self.translator.current_lang)
        dark = settings.value('dark_theme', False, type=bool)
        adv_naming = settings.value('advanced_naming', False, type=bool)
        adv_inst = settings.value('advanced_naming_inst', False, type=bool)
        adv_eff = settings.value('advanced_naming_eff', False, type=bool)
        adv_was = settings.value('advanced_naming_was', False, type=bool)
        self.translator.set_language(lang)
        if dark:
            self.set_dark_theme()
        self.naming_settings = {
            'advanced_naming': adv_naming,
            'advanced_naming_inst': adv_inst,
            'advanced_naming_eff': adv_eff,
            'advanced_naming_was': adv_was
        }

    def update_translations(self):
        """
        Update the UI texts and menus according to the current language.
        """
        self.setWindowTitle(self.appinfo.get('app_name', 'Lab Automation'))
        self.tabs.setTabText(0, self.translator.t('remote_control'))
        self.init_menu()
        self.remote_tab.update_translation(self.translator)

    def edit_project_file(self, item):
        """
        Open a configuration dialog for the selected file based on its type (.eff, .was, .inst).
        :param item: QListWidgetItem clicked.
        """
        if not self.current_project_dir:
            return
        fname = item.text()
        file_path = os.path.join(self.current_project_dir, fname)
        if fname.endswith('.eff'):
            dlg = EffFileDialog(file_path, self.translator, self)
            dlg.exec_()
        elif fname.endswith('.was'):
            dlg = WasFileDialog(file_path, self.translator, self)
            dlg.exec_()
        elif fname.endswith('.inst'):
            dlg = InstFileDialog(file_path, self.translator, self)
            dlg.exec_()
        # (Other types can be added in the future)

class DatabaseDialog(QDialog):
    """
    Dialog for configuring database connection settings.
    """
    def __init__(self, parent=None, translator=None):
        """
        Initialize the database settings dialog with input fields for host, port, user, password, and database name.
        :param parent: Parent widget.
        :param translator: Translator instance.
        """
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.t('database_settings'))
        self.setModal(True)
        layout = QVBoxLayout()
        from PyQt5.QtWidgets import QLineEdit, QFormLayout
        form = QFormLayout()
        self.host = QLineEdit()
        self.port = QLineEdit()
        self.user = QLineEdit()
        self.password = QLineEdit()
        self.dbname = QLineEdit()
        form.addRow(self.translator.t('db_host'), self.host)
        form.addRow(self.translator.t('db_port'), self.port)
        form.addRow(self.translator.t('db_user'), self.user)
        form.addRow(self.translator.t('db_password'), self.password)
        form.addRow(self.translator.t('db_name'), self.dbname)
        layout.addLayout(form)
        save_btn = QPushButton(self.translator.t('save'))
        save_btn.clicked.connect(self.save_db_settings)
        layout.addWidget(save_btn)
        self.setLayout(layout)
        self.load_db_settings()

    def save_db_settings(self):
        """
        Save the database settings to QSettings and close the dialog.
        """
        settings = QSettings('LabAutomation', 'App')
        settings.setValue('db_host', self.host.text())
        settings.setValue('db_port', self.port.text())
        settings.setValue('db_user', self.user.text())
        settings.setValue('db_password', self.password.text())
        settings.setValue('db_name', self.dbname.text())
        self.accept()

    def load_db_settings(self):
        """
        Load database settings from QSettings and populate the input fields.
        """
        settings = QSettings('LabAutomation', 'App')
        self.host.setText(settings.value('db_host', 'localhost'))
        self.port.setText(settings.value('db_port', '9090'))
        self.user.setText(settings.value('db_user', ''))
        self.password.setText(settings.value('db_password', ''))
        self.dbname.setText(settings.value('db_name', 'prometheus'))

class AddFileDialog(QDialog):
    """
    Dialog for adding a new file (.eff or .was) to the project.
    """
    def __init__(self, parent=None, translator=None, naming_settings=None):
        """
        Initialize the add file dialog with file type and name input fields.
        :param parent: Parent widget.
        :param translator: Translator instance.
        :param naming_settings: Naming settings for the project.
        """
        super().__init__(parent)
        self.translator = translator
        self.naming_settings = naming_settings or {'custom_naming': False, 'eff_naming': False, 'was_naming': False, 'inst_naming': False}
        self.setWindowTitle(self.translator.t('add_file'))
        self.setModal(True)
        layout = QVBoxLayout()
        from PyQt5.QtWidgets import QComboBox, QLineEdit, QLabel
        self.type_combo = QComboBox()
        self.type_combo.addItem(self.translator.t('efficiency_settings'), '.eff')
        self.type_combo.addItem(self.translator.t('oscilloscope_settings'), '.was')
        self.name_edit = QLineEdit()
        layout.addWidget(QLabel(self.translator.t('file_type')))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel(self.translator.t('file_name')))
        layout.addWidget(self.name_edit)
        add_btn = QPushButton(self.translator.t('add'))
        add_btn.clicked.connect(self.accept)
        layout.addWidget(add_btn)
        self.setLayout(layout)

    def create_file(self):
        """
        Create a new file (.eff or .was) in the selected project folder with default content.
        """
        import datetime
        import uuid
        file_type = self.type_combo.currentText()
        file_name = self.name_edit.text().strip()
        if not file_name:
            return
        dir_path = QFileDialog.getExistingDirectory(self, self.translator.t('select_project_folder'))
        if not dir_path:
            return
        project_id = file_name if file_type == '.was' else str(uuid.uuid4())
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if file_type == '.eff':
            eff_file = os.path.join(dir_path, f"{project_id}_{now}.eff")
            eff_data = {"type": "efficiency", "data": {}}
            with open(eff_file, 'w', encoding='utf-8') as f:
                json.dump(eff_data, f, indent=2)
        elif file_type == '.was':
            was_file = os.path.join(dir_path, f"{project_id}_{now}.was")
            was_data = {"type": "oscilloscope_settings", "settings": {}}
            with open(was_file, 'w', encoding='utf-8') as f:
                json.dump(was_data, f, indent=2)
        self.accept()

class EffFileDialog(QDialog):
    """
    Dialog for editing a .eff (efficiency) file.
    """
    def __init__(self, file_path, translator, parent=None):
        """
        Initialize the dialog and load the .eff file data.
        :param file_path: Path to the .eff file.
        :param translator: Translator instance.
        :param parent: Parent widget.
        """
        super().__init__(parent)
        self.translator = translator
        self.file_path = file_path
        self.setWindowTitle(self.translator.t('edit_eff_file'))
        self.setModal(True)
        import PyQt5.QtWidgets as QtW
        # Main horizontal layout: left parameters, right JSON editor
        main_layout = QtW.QHBoxLayout()
        # --- Left section: Vin Sweep parameters ---
        left_layout = QtW.QVBoxLayout()
        group_vin = QtW.QGroupBox(self.translator.t('vin_sweep'))
        form_vin = QtW.QFormLayout()
        # Input mode: list of values or range
        self.mode_group = QtW.QButtonGroup(self)
        self.list_radio = QtW.QRadioButton(self.translator.t('vin_list_mode'))
        self.range_radio = QtW.QRadioButton(self.translator.t('vin_range_mode'))
        self.mode_group.addButton(self.list_radio)
        self.mode_group.addButton(self.range_radio)
        self.list_radio.setChecked(True)
        form_vin.addRow(self.list_radio)
        # Field for list of Vin values
        self.vin_list_edit = QtW.QLineEdit()
        self.vin_list_edit.setPlaceholderText(self.translator.t('vin_list_placeholder'))
        form_vin.addRow(self.vin_list_edit)
        # Field for Vin range (start, stop, n points)
        form_vin.addRow(self.range_radio)
        self.vin_start_edit = QtW.QLineEdit()
        self.vin_start_edit.setPlaceholderText(self.translator.t('vin_start_placeholder'))
        self.vin_stop_edit = QtW.QLineEdit()
        self.vin_stop_edit.setPlaceholderText(self.translator.t('vin_stop_placeholder'))
        self.vin_points_spin = QtW.QSpinBox()
        self.vin_points_spin.setMinimum(2)
        self.vin_points_spin.setMaximum(1000)
        self.vin_points_spin.setValue(5)
        range_row_vin = QtW.QHBoxLayout()
        range_row_vin.addWidget(self.vin_start_edit)
        range_row_vin.addWidget(self.vin_stop_edit)
        range_row_vin.addWidget(QtW.QLabel(self.translator.t('vin_points_label')))
        range_row_vin.addWidget(self.vin_points_spin)
        form_vin.addRow(range_row_vin)
        group_vin.setLayout(form_vin)
        left_layout.addWidget(group_vin)
        # --- Iout Sweep section ---
        group_iout = QtW.QGroupBox(self.translator.t('iout_sweep'))
        form_iout = QtW.QFormLayout()
        self.iout_mode_group = QtW.QButtonGroup(self)
        self.iout_list_radio = QtW.QRadioButton(self.translator.t('iout_list_mode'))
        self.iout_range_radio = QtW.QRadioButton(self.translator.t('iout_range_mode'))
        self.iout_mode_group.addButton(self.iout_list_radio)
        self.iout_mode_group.addButton(self.iout_range_radio)
        self.iout_list_radio.setChecked(True)
        form_iout.addRow(self.iout_list_radio)
        # Field for list of Iout values
        self.iout_list_edit = QtW.QLineEdit()
        self.iout_list_edit.setPlaceholderText(self.translator.t('iout_list_placeholder'))
        form_iout.addRow(self.iout_list_edit)
        # Field for Iout range (start, stop, n points)
        form_iout.addRow(self.iout_range_radio)
        self.iout_start_edit = QtW.QLineEdit()
        self.iout_start_edit.setPlaceholderText(self.translator.t('iout_start_placeholder'))
        self.iout_stop_edit = QtW.QLineEdit()
        self.iout_stop_edit.setPlaceholderText(self.translator.t('iout_stop_placeholder'))
        self.iout_points_spin = QtW.QSpinBox()
        self.iout_points_spin.setMinimum(2)
        self.iout_points_spin.setMaximum(1000)
        self.iout_points_spin.setValue(5)
        range_row_iout = QtW.QHBoxLayout()
        range_row_iout.addWidget(self.iout_start_edit)
        range_row_iout.addWidget(self.iout_stop_edit)
        range_row_iout.addWidget(QtW.QLabel(self.translator.t('iout_points_label')))
        range_row_iout.addWidget(self.iout_points_spin)
        form_iout.addRow(range_row_iout)
        group_iout.setLayout(form_iout)
        left_layout.addWidget(group_iout)
        # Button to apply parameters to JSON
        self.apply_params_btn = QtW.QPushButton(self.translator.t('apply_to_data'))
        self.apply_params_btn.clicked.connect(self.apply_params_to_json)
        left_layout.addWidget(self.apply_params_btn)
        left_layout.addStretch()
        # --- Right section: JSON editor ---
        right_layout = QtW.QVBoxLayout()
        self.data_edit = QtW.QTextEdit()
        # Load the .eff file content
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.data_edit.setText(json.dumps(self.data, indent=2))
        except Exception as e:
            self.data = {"type": "efficiency", "data": {}}
            self.data_edit.setText(json.dumps(self.data, indent=2))
        right_layout.addWidget(QtW.QLabel(self.translator.t('efficiency_data')))
        right_layout.addWidget(self.data_edit)
        # Button to save changes
        save_btn = QtW.QPushButton(self.translator.t('save'))
        save_btn.clicked.connect(self.save_changes)
        right_layout.addWidget(save_btn)
        # --- Combine layouts ---
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)
        # Prefill parameters on the left if present in JSON
        self.populate_params_from_json()
        # Sync parameters if JSON is manually modified
        self.data_edit.textChanged.connect(self.sync_params_from_json)

    def populate_params_from_json(self):
        """
        Popola i campi del form a sinistra leggendo i dati dal JSON (se presenti).
        """
        vin = self.data.get('data', {}).get('Vin loop', None)
        if isinstance(vin, list):
            self.list_radio.setChecked(True)
            self.vin_list_edit.setText(','.join(str(v) for v in vin))
        elif isinstance(vin, dict):
            self.range_radio.setChecked(True)
            self.vin_start_edit.setText(str(vin.get('start', '')))
            self.vin_stop_edit.setText(str(vin.get('stop', '')))
            self.vin_points_spin.setValue(int(vin.get('points', 5)))
        iout = self.data.get('data', {}).get('Iout loop', None)
        if isinstance(iout, list):
            self.iout_list_radio.setChecked(True)
            self.iout_list_edit.setText(','.join(str(i) for i in iout))
        elif isinstance(iout, dict):
            self.iout_range_radio.setChecked(True)
            self.iout_start_edit.setText(str(iout.get('start', '')))
            self.iout_stop_edit.setText(str(iout.get('stop', '')))
            self.iout_points_spin.setValue(int(iout.get('points', 5)))

    def apply_params_to_json(self):
        """
        Aggiorna il JSON a destra in base ai parametri inseriti a sinistra.
        Se è selezionata la modalità lista, salva una lista di float.
        Se è selezionata la modalità range, salva un dizionario con start, stop, points.
        """
        if self.list_radio.isChecked():
            try:
                vin_list = [float(x.strip()) for x in self.vin_list_edit.text().split(',') if x.strip()]
                self.data['data']['Vin loop'] = vin_list
            except Exception:
                pass
        elif self.range_radio.isChecked():
            try:
                start = float(self.vin_start_edit.text())
                stop = float(self.vin_stop_edit.text())
                points = int(self.vin_points_spin.value())
                self.data['data']['Vin loop'] = {'start': start, 'stop': stop, 'points': points}
            except Exception:
                pass
        if self.iout_list_radio.isChecked():
            try:
                iout_list = [float(x.strip()) for x in self.iout_list_edit.text().split(',') if x.strip()]
                self.data['data']['Iout loop'] = iout_list
            except Exception:
                pass
        elif self.iout_range_radio.isChecked():
            try:
                start = float(self.iout_start_edit.text())
                stop = float(self.iout_stop_edit.text())
                points = int(self.iout_points_spin.value())
                self.data['data']['Iout loop'] = {'start': start, 'stop': stop, 'points': points}
            except Exception:
                pass
        self.data_edit.setText(json.dumps(self.data, indent=2))

    def sync_params_from_json(self):
        """
        Aggiorna i parametri a sinistra se il JSON viene modificato manualmente.
        """
        try:
            self.data = json.loads(self.data_edit.toPlainText())
            self.populate_params_from_json()
        except Exception:
            pass

    def save_changes(self):
        """
        Salva i dati modificati nel file .eff.
        Mostra un messaggio di errore se il salvataggio fallisce.
        """
        try:
            data = json.loads(self.data_edit.toPlainText())
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.accept()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.translator.t('error'), str(e))

class WasFileDialog(QDialog):
    """
    Dialog per la modifica di un file .was (oscilloscope settings), con modulo a sinistra per tempo/div e volt/div e editor JSON a destra.
    """
    def __init__(self, file_path, translator, parent=None):
        """
        Inizializza la finestra di dialogo per la modifica di un file .was.
        :param file_path: Percorso del file .was da modificare.
        :param translator: Istanza del traduttore per la localizzazione.
        :param parent: Widget genitore.
        """
        super().__init__(parent)
        from PyQt5.QtWidgets import QLineEdit, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
        self.translator = translator
        self.file_path = file_path
        self.setWindowTitle(self.translator.t('edit_was_file'))
        self.setModal(True)
        # Layout principale orizzontale: sinistra parametri, destra JSON
        main_layout = QHBoxLayout()
        # --- Sezione sinistra: parametri tempo/div e volt/div ---
        left_layout = QVBoxLayout()
        form = QFormLayout()
        # Campo per tempo/div (accetta anche notazione 100k, 1n1, ecc.)
        self.time_div_edit = QLineEdit()
        self.time_div_edit.setPlaceholderText(self.translator.t('time_div_placeholder'))
        form.addRow(self.translator.t('time_div_label'), self.time_div_edit)
        # Campo per volt/div
        self.volt_div_edit = QLineEdit()
        self.volt_div_edit.setPlaceholderText(self.translator.t('volt_div_placeholder'))
        form.addRow(self.translator.t('volt_div_label'), self.volt_div_edit)
        left_layout.addLayout(form)
        # Pulsante per applicare i parametri al JSON
        self.apply_params_btn = QPushButton(self.translator.t('apply_to_data'))
        self.apply_params_btn.clicked.connect(self.apply_params_to_json)
        left_layout.addWidget(self.apply_params_btn)
        left_layout.addStretch()
        # --- Sezione destra: editor JSON ---
        right_layout = QVBoxLayout()
        self.data_edit = QTextEdit()
        # Carica il contenuto del file .was
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.data_edit.setText(json.dumps(self.data, indent=2))
        except Exception as e:
            self.data = {"type": "oscilloscope_settings", "settings": {}}
            self.data_edit.setText(json.dumps(self.data, indent=2))
        right_layout.addWidget(QLabel(self.translator.t('oscilloscope_settings_data')))
        right_layout.addWidget(self.data_edit)
        # Pulsante per salvare le modifiche
        save_btn = QPushButton(self.translator.t('save'))
        save_btn.clicked.connect(self.save_changes)
        right_layout.addWidget(save_btn)
        # --- Unione layout ---
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)
        # Precompila i parametri a sinistra se già presenti nel JSON
        self.populate_params_from_json()
        # Sincronizza i parametri se il JSON viene modificato manualmente
        self.data_edit.textChanged.connect(self.sync_params_from_json)

    def parse_time(self, s):
        """
        Converte una stringa tipo '100k', '1n1', '0.001' in float secondi.
        Accetta anche notazione con suffissi k, m, u, n, p.
        """
        s = s.strip().lower().replace(',', '.')
        try:
            if 'k' in s:
                return float(s.replace('k','')) * 1e3
            if 'm' in s:
                return float(s.replace('m','')) * 1e-3
            if 'u' in s:
                return float(s.replace('u','')) * 1e-6
            if 'n' in s:
                return float(s.replace('n','')) * 1e-9
            if 'p' in s:
                return float(s.replace('p','')) * 1e-12
            if '1n1' in s:
                return 1e-9
            return float(s)
        except Exception:
            return None

    def populate_params_from_json(self):
        """
        Popola i campi del form a sinistra leggendo i dati dal JSON (se presenti).
        """
        settings = self.data.get('settings', {})
        tdiv = settings.get('time_per_div', '')
        vdiv = settings.get('volt_per_div', '')
        if tdiv:
            self.time_div_edit.setText(str(tdiv))
        if vdiv:
            self.volt_div_edit.setText(str(vdiv))

    def apply_params_to_json(self):
        """
        Aggiorna il JSON a destra in base ai parametri inseriti a sinistra.
        Converte i valori e aggiorna il dizionario settings.
        """
        tdiv = self.parse_time(self.time_div_edit.text())
        try:
            vdiv = float(self.volt_div_edit.text().replace(',', '.'))
        except Exception:
            vdiv = None
        if tdiv is not None and vdiv is not None:
            self.data['settings']['time_per_div'] = tdiv
            self.data['settings']['volt_per_div'] = vdiv
            self.data_edit.setText(json.dumps(self.data, indent=2))

    def sync_params_from_json(self):
        """
        Aggiorna i parametri a sinistra se il JSON viene modificato manualmente.
        """
        try:
            self.data = json.loads(self.data_edit.toPlainText())
            self.populate_params_from_json()
        except Exception:
            pass

    def save_changes(self):
        """
        Salva i dati modificati nel file .was.
        Mostra un messaggio di errore se il salvataggio fallisce.
        """
        try:
            data = json.loads(self.data_edit.toPlainText())
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.accept()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.translator.t('error'), str(e))

class InstFileDialog(QDialog):
    """
    Dialog per la modifica di un file .inst (strumenti).
    Permette di aggiungere strumenti dalla libreria instruments_lib.json con dettagli istanza.
    Selezione strumento: tipo → serie → modello.
    """
    def __init__(self, file_path, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.file_path = file_path
        self.setWindowTitle(self.translator.t('edit_inst_file'))
        self.setModal(True)
        layout = QVBoxLayout()
        from PyQt5.QtWidgets import QLabel, QTextEdit, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QComboBox, QLineEdit, QFormLayout, QDialogButtonBox
        # Carica dati file .inst
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.inst_data = json.load(f)
        except Exception:
            self.inst_data = {"instruments": []}
        # Carica libreria strumenti
        self.instrument_library = self.load_instrument_library()
        # Lista strumenti già aggiunti
        layout.addWidget(QLabel(self.translator.t('added_instruments') if hasattr(self.translator, 't') else 'Strumenti aggiunti'))
        self.instruments_list_widget = QListWidget()
        self.refresh_instruments_list()
        layout.addWidget(self.instruments_list_widget)
        remove_btn = QPushButton(self.translator.t('remove_selected') if hasattr(self.translator, 't') else 'Rimuovi selezionato')
        remove_btn.clicked.connect(self.remove_selected_instrument)
        layout.addWidget(remove_btn)
        # --- Form per aggiunta nuovo strumento ---
        layout.addWidget(QLabel(self.translator.t('add_new_instrument') if hasattr(self.translator, 't') else 'Aggiungi nuovo strumento'))
        form = QFormLayout()
        self.instance_name_edit = QLineEdit()
        form.addRow(self.translator.t('instance_name') if hasattr(self.translator, 't') else 'Nome istanza', self.instance_name_edit)
        # Menu tipo strumento
        self.type_combo = QComboBox()
        self.type_map = {
            'power_supplies': 'Alimentatore',
            'dataloggers': 'Datalogger',
            'oscilloscopes': 'Oscilloscopio'
        }
        for k, v in self.type_map.items():
            self.type_combo.addItem(v, k)
        self.type_combo.currentIndexChanged.connect(self.update_series_combo)
        form.addRow(self.translator.t('instrument_type') if hasattr(self.translator, 't') else 'Tipo strumento', self.type_combo)
        # Menu serie
        self.series_combo = QComboBox()
        self.series_combo.currentIndexChanged.connect(self.update_model_combo)
        form.addRow(self.translator.t('series') if hasattr(self.translator, 't') else 'Serie', self.series_combo)
        # Menu modello
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.update_connection_types)
        form.addRow(self.translator.t('model') if hasattr(self.translator, 't') else 'Modello', self.model_combo)
        # Tipo connessione
        self.connection_type_combo = QComboBox()
        form.addRow(self.translator.t('connection_type') if hasattr(self.translator, 't') else 'Tipo connessione', self.connection_type_combo)
        # Sostituisco QLineEdit con QPushButton e QLabel (readonly)
        self.visa_address_btn = QPushButton(self.translator.t('compose_visa_address'))
        self.visa_address_btn.clicked.connect(self.open_visa_address_dialog)
        self.visa_address_label = QLabel('')
        self.visa_address_label.setStyleSheet('background:#eee; border:1px solid #ccc; padding:2px;')
        form.addRow(self.translator.t('visa_address'), self.visa_address_btn)
        form.addRow(self.translator.t('composed_address'), self.visa_address_label)
        # Canali
        self.channels_widget = QListWidget()
        form.addRow(self.translator.t('channel_assignments') if hasattr(self.translator, 't') else 'Assegnazione canali', self.channels_widget)
        self.model_combo.currentIndexChanged.connect(self.update_channels_widget)
        layout.addLayout(form)
        add_btn = QPushButton(self.translator.t('add_instrument') if hasattr(self.translator, 't') else 'Aggiungi strumento')
        add_btn.clicked.connect(self.add_instrument_to_inst)
        layout.addWidget(add_btn)
        # --- Fine form ---
        # Editor JSON raw (opzionale, solo per debug)
        self.data_edit = QTextEdit()
        self.data_edit.setText(json.dumps(self.inst_data, indent=2))
        layout.addWidget(QLabel(self.translator.t('raw_json') if hasattr(self.translator, 't') else 'JSON grezzo'))
        layout.addWidget(self.data_edit)
        save_btn = QPushButton(self.translator.t('save'))
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)
        self.setLayout(layout)
        self.update_series_combo()

    def load_instrument_library(self):
        lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Instruments_LIB', 'instruments_lib.json')
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                return json.load(f)['instrument_library']
        except Exception:
            return {}

    def refresh_instruments_list(self):
        self.instruments_list_widget.clear()
        for inst in self.inst_data.get('instruments', []):
            instance_name = inst.get('instance_name', '')
            generic_id = inst.get('instrument_generic_id', '')
            # Ricerca tipo, serie, modello dalla libreria
            type_label = series_label = model_label = ''
            for type_key, type_list in self.instrument_library.items():
                for serie in type_list:
                    for model in serie.get('models', []):
                        if model.get('id') == generic_id:
                            # Trova le label localizzate
                            type_label = self.type_map.get(type_key, type_key)
                            series_label = serie.get('series_name', serie.get('series_id', ''))
                            model_label = model.get('name', model.get('id', ''))
            label = f"{instance_name} ({type_label}, {series_label}, {model_label})"
            self.instruments_list_widget.addItem(label)

    def remove_selected_instrument(self):
        row = self.instruments_list_widget.currentRow()
        if row >= 0:
            del self.inst_data['instruments'][row]
            self.refresh_instruments_list()
            self.data_edit.setText(json.dumps(self.inst_data, indent=2))
            self.save_changes(auto=True)

    def update_series_combo(self):
        self.series_combo.clear()
        type_key = self.type_combo.currentData()
        series_list = self.instrument_library.get(type_key, [])
        for serie in series_list:
            label = serie.get('series_name', serie.get('series_id', ''))
            self.series_combo.addItem(label, serie)
        self.update_model_combo()

    def update_model_combo(self):
        self.model_combo.clear()
        serie = self.series_combo.currentData()
        if not serie:
            return
        for model in serie.get('models', []):
            label = model.get('name', model.get('id', ''))
            self.model_combo.addItem(label, model)
        self.update_connection_types()
        self.update_channels_widget()

    def update_connection_types(self):
        self.connection_type_combo.clear()
        model = self.model_combo.currentData()
        if not model:
            return
        conn_types = model.get('interface', {}).get('supported_connection_types', [])
        for c in conn_types:
            self.connection_type_combo.addItem(c['type'], c)
        if conn_types:
            self.visa_address_btn.setEnabled(True)
            self.visa_address_label.setEnabled(True)
            self.visa_address_btn.setText(self.translator.t('compose_visa_address'))
            self.visa_address_label.setText('')
            self.visa_address_label.setStyleSheet('background:#fff; border:1px solid #ccc; padding:2px;')
        else:
            self.visa_address_btn.setEnabled(False)
            self.visa_address_label.setEnabled(False)
            self.visa_address_label.setText('N/A')
            self.visa_address_label.setStyleSheet('background:#eee; border:1px solid #ccc; padding:2px;')

    def update_channels_widget(self):
        self.channels_widget.clear()
        model = self.model_combo.currentData()
        type_key = self.type_combo.currentData()
        if not model:
            return
        if type_key == 'power_supplies':
            channels = model.get('capabilities', {}).get('channels', [])
            for ch in channels:
                self.channels_widget.addItem(f"{ch.get('label','')} [{ch.get('channel_id','')}] (nome canale personalizzabile)")
        elif type_key == 'dataloggers':
            n = model.get('capabilities', {}).get('channels', 0)
            for i in range(1, n+1):
                self.channels_widget.addItem(f"Segnale {i} (numero canale personalizzabile)")
        elif type_key == 'oscilloscopes':
            channels = model.get('capabilities', {}).get('channels', [])
            for ch in channels:
                self.channels_widget.addItem(f"{ch.get('label','')} [{ch.get('channel_id','')}] (nome segnale personalizzabile)")

    def open_visa_address_dialog(self):
        conn_type = self.connection_type_combo.currentData()
        dlg = VisaAddressDialog(self, self.translator, conn_type)
        if dlg.exec_() == QDialog.Accepted:
            self.visa_address_label.setText(dlg.address)

    def add_instrument_to_inst(self):
        type_key = self.type_combo.currentData()
        serie = self.series_combo.currentData()
        model = self.model_combo.currentData()
        if not model:
            return
        instance_name = self.instance_name_edit.text().strip()
        if not instance_name:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Errore', 'Inserire un nome istanza')
            return
        conn_type = self.connection_type_combo.currentData()
        visa_addr = self.visa_address_label.text().strip()
        channel_assignments = []
        for i in range(self.channels_widget.count()):
            ch_item = self.channels_widget.item(i).text()
            from PyQt5.QtWidgets import QInputDialog
            if type_key == 'dataloggers':
                signal_name, ok = QInputDialog.getText(self, 'Assegna segnale', f'Nome segnale per {ch_item}:')
                if not ok:
                    continue
                channel_number, ok = QInputDialog.getText(self, 'Numero canale', f'Numero canale per {signal_name}:')
                if not ok:
                    continue
                channel_assignments.append({"signal_name": signal_name, "channel_number": channel_number})
            else:
                signal_name, ok = QInputDialog.getText(self, 'Assegna canale', f'Nome segnale/canale per {ch_item}:')
                if not ok:
                    continue
                if '[' in ch_item and ']' in ch_item:
                    channel_id = ch_item.split('[')[-1].split(']')[0]
                else:
                    channel_id = f"CH{i+1}"
                channel_assignments.append({"channel_name" if type_key=="power_supplies" else "signal_name": signal_name, "channel_id": channel_id})
        new_instr = {
            "instance_name": instance_name,
            "instrument_generic_id": model.get('id'),
            "actual_connection_type": conn_type['type'] if conn_type else '',
            "actual_visa_address": visa_addr,
            "channel_assignments": channel_assignments
        }
        self.inst_data.setdefault('instruments', []).append(new_instr)
        self.refresh_instruments_list()
        self.data_edit.setText(json.dumps(self.inst_data, indent=2))
        self.save_changes(auto=True)

    def save_changes(self, auto=False):
        try:
            if auto:
                data = self.inst_data
            else:
                data = json.loads(self.data_edit.toPlainText())
                self.inst_data = data
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            if not auto:
                self.accept()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.translator.t('error'), str(e))

class VisaAddressDialog(QDialog):
    """
    Dialog per la composizione parametrica dell'indirizzo VISA.
    Mostra i campi necessari in base al tipo di interfaccia selezionato.
    """
    def __init__(self, parent, translator, conn_type):
        super().__init__(parent)
        self.translator = translator
        self.conn_type = conn_type  # dict con info tipo connessione
        self.setWindowTitle(self.translator.t('compose_visa_address'))
        self.setModal(True)
        self.address = ''
        layout = QVBoxLayout()
        self.fields = {}
        form = QFormLayout()
        t = conn_type['type'].lower() if conn_type else ''
        # LXI (TCP/IP)
        if t in ['lxi', 'tcpip', 'ethernet']:
            self.ip_edit = QLineEdit()
            self.port_edit = QLineEdit()
            self.port_edit.setText('5025')
            form.addRow(self.translator.t('ip_address'), self.ip_edit)
            form.addRow(self.translator.t('port'), self.port_edit)
            self.fields = {'ip': self.ip_edit, 'port': self.port_edit}
        # GPIB
        elif t == 'gpib':
            self.gpib_board = QLineEdit()
            self.gpib_board.setText('0')
            self.gpib_addr = QLineEdit()
            form.addRow(self.translator.t('gpib_board'), self.gpib_board)
            form.addRow(self.translator.t('gpib_address'), self.gpib_addr)
            self.fields = {'board': self.gpib_board, 'address': self.gpib_addr}
        # USB
        elif t == 'usb':
            self.usb_serial = QLineEdit()
            form.addRow(self.translator.t('usb_serial'), self.usb_serial)
            self.fields = {'serial': self.usb_serial}
        # RS232
        elif t in ['rs232', 'serial']:
            self.com_port = QLineEdit()
            self.baudrate = QLineEdit()
            self.baudrate.setText('9600')
            form.addRow(self.translator.t('com_port'), self.com_port)
            form.addRow(self.translator.t('baudrate'), self.baudrate)
            self.fields = {'com': self.com_port, 'baud': self.baudrate}
        # Altro
        else:
            self.generic = QLineEdit()
            form.addRow(self.translator.t('visa_address'), self.generic)
            self.fields = {'address': self.generic}
        layout.addLayout(form)
        # Pulsante verifica
        btn_row = QHBoxLayout()
        self.check_btn = QPushButton(self.translator.t('check_connection'))
        self.check_btn.clicked.connect(self.check_connection)
        btn_row.addWidget(self.check_btn)
        self.ok_btn = QPushButton(self.translator.t('ok'))
        self.ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.ok_btn)
        layout.addLayout(btn_row)
        self.setLayout(layout)
    def compose_address(self):
        t = self.conn_type['type'].lower() if self.conn_type else ''
        if t in ['lxi', 'tcpip', 'ethernet']:
            ip = self.fields['ip'].text().strip()
            port = self.fields['port'].text().strip()
            return f"TCPIP::{ip}::{port}::SOCKET"
        elif t == 'gpib':
            board = self.fields['board'].text().strip()
            addr = self.fields['address'].text().strip()
            return f"GPIB{board}::{addr}::INSTR"
        elif t == 'usb':
            serial = self.fields['serial'].text().strip()
            return f"USB::{serial}::INSTR"
        elif t in ['rs232', 'serial']:
            com = self.fields['com'].text().strip()
            baud = self.fields['baud'].text().strip()
            return f"ASRL{com}::INSTR (baudrate {baud})"
        else:
            return self.fields['address'].text().strip()
    def check_connection(self):
        # Mock: validazione sintattica base
        addr = self.compose_address()
        if not addr or '::' not in addr:
            QMessageBox.warning(self, self.translator.t('error'), self.translator.t('invalid_address'))
            return
        QMessageBox.information(self, self.translator.t('check_connection'), self.translator.t('address_valid'))
    def accept(self):
        self.address = self.compose_address()
        super().accept()

if __name__ == '__main__':
    """
    Main entry point for the application. Initializes QApplication and shows the main window.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())