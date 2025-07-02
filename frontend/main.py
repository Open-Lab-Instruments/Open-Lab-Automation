import sys
import os
import json
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QAction, QDialog, QPushButton, QHBoxLayout, QComboBox, QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QSplitter, QRadioButton, QButtonGroup, QSpinBox, QGroupBox, QFormLayout, QTextEdit, QSizePolicy, QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QSettings
import uuid

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
        # --- Open last project if available ---
        settings = QSettings('LabAutomation', 'App')
        last_project_path = settings.value('last_project_path', '', type=str)
        if last_project_path and os.path.isfile(last_project_path):
            try:
                with open(last_project_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                self.current_project_dir = os.path.dirname(last_project_path)
                self.current_project_data = project_data
                self.refresh_project_files()
            except Exception:
                pass

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
        # Tools menu
        tools_menu = menubar.addMenu(self.translator.t('tools') if hasattr(self.translator, 't') else 'Tools')
        manage_lib_action = QAction(self.translator.t('manage_instrument_library') if hasattr(self.translator, 't') else 'Gestisci libreria strumenti', self)
        manage_lib_action.triggered.connect(self.open_instrument_library_dialog)
        tools_menu.addAction(manage_lib_action)

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
            # Salva percorso ultimo progetto
            settings.setValue('last_project_path', project_file)
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
                # Salva percorso ultimo progetto
                settings = QSettings('LabAutomation', 'App')
                settings.setValue('last_project_path', file_path)
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

    def open_instrument_library_dialog(self):
        """
        Open the instrument library manager dialog.
        """
        dlg = InstrumentLibraryDialog(self, self.translator)
        dlg.exec_()

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
        self.left_layout = QtW.QVBoxLayout()
        self.setup_dynamic_variable_selectors()  # <--- AGGIUNTA QUI
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
        self.left_layout.addWidget(group_vin)
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
        self.left_layout.addWidget(group_iout)
        # Button to apply parameters to JSON
        self.apply_params_btn = QtW.QPushButton(self.translator.t('apply_to_data'))
        self.apply_params_btn.clicked.connect(self.apply_params_to_json)
        self.left_layout.addWidget(self.apply_params_btn)
        self.left_layout.addStretch()
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
        main_layout.addLayout(self.left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)
        # Prefill parameters on the left if present in JSON
        self.populate_params_from_json()
        # Sync parameters if JSON is manually modified
        self.data_edit.textChanged.connect(self.sync_params_from_json)

    def get_inst_file_variables(self):
        """
        Carica i nomi delle variabili di setpoint (VAR_set) e misura (VAR) dal file .inst associato al progetto.
        Restituisce due liste: setpoint_vars, measured_vars.
        """
        import os, json
        # Trova la directory del progetto e il file .inst associato
        project_dir = os.path.dirname(self.file_path)
        # Cerca il file .json del progetto nella stessa cartella
        project_json = None
        for f in os.listdir(project_dir):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(project_dir, f), 'r', encoding='utf-8') as pj:
                        data = json.load(pj)
                    if 'inst_file' in data:
                        project_json = data
                        break
                except Exception:
                    continue
        if not project_json:
            return [], []
        inst_file = project_json.get('inst_file')
        inst_path = os.path.join(project_dir, inst_file)
        if not os.path.isfile(inst_path):
            return [], []
        try:
            with open(inst_path, 'r', encoding='utf-8') as f:
                inst_data = json.load(f)
        except Exception:
            return [], []
        setpoint_vars = []
        measured_vars = []
        # Estrai variabili dai canali degli strumenti
        for inst in inst_data.get('instruments', []):
            type_key = inst.get('instrument_type', '')
            channels = inst.get('channels', [])
            if type_key in ['power_supplies', 'electronic_loads']:
                for ch in channels:
                    var = ch.get('variable', '')
                    if var:
                        setpoint_vars.append(var)
            elif type_key in ['dataloggers']:
                for ch in channels:
                    var = ch.get('measured_variable', '')
                    if var:
                        measured_vars.append(var)
        # Rimuovi duplicati e ordina
        setpoint_vars = sorted(set(setpoint_vars))
        measured_vars = sorted(set(setpoint_vars + measured_vars))
        return setpoint_vars, measured_vars

    def setup_dynamic_variable_selectors(self):
        """
        Crea le combobox per la selezione delle variabili sweep (setpoint) e misura, usando i nomi dinamici dal .inst.
        """
        set_vars, meas_vars = self.get_inst_file_variables()
        # Sweep variable (setpoint)
        self.sweep_var_combo = QComboBox()
        for v in set_vars:
            self.sweep_var_combo.addItem(f"{v}_set", v)
        self.sweep_var_combo.setToolTip(self.translator.t('select_sweep_variable'))
        # Measured variable
        self.measured_var_combo = QComboBox()
        for v in meas_vars:
            self.measured_var_combo.addItem(v, v)
        self.measured_var_combo.setToolTip(self.translator.t('select_measured_variable'))
        # Inserisci le combobox in cima al layout a sinistra
        self.left_layout.insertWidget(0, QLabel(self.translator.t('sweep_variable_label')))
        self.left_layout.insertWidget(1, self.sweep_var_combo)
        self.left_layout.insertWidget(2, QLabel(self.translator.t('measured_variable_label')))
        self.left_layout.insertWidget(3, self.measured_var_combo)

    def populate_params_from_json(self):
        """
        Popola i campi del form a sinistra leggendo i dati dal JSON (se presenti), incluse le variabili dinamiche.
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
        # Seleziona le variabili se presenti nel JSON
        sweep_var = self.data.get('sweep_variable', None)
        measured_var = self.data.get('measured_variable', None)
        if hasattr(self, 'sweep_var_combo') and sweep_var:
            idx = self.sweep_var_combo.findData(sweep_var)
            if idx >= 0:
                self.sweep_var_combo.setCurrentIndex(idx)
        if hasattr(self, 'measured_var_combo') and measured_var:
            idx = self.measured_var_combo.findData(measured_var)
            if idx >= 0:
                self.measured_var_combo.setCurrentIndex(idx)

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
        Salva i dati modificati nel file .eff, includendo le variabili sweep e misura selezionate.
        Mostra un messaggio di errore se il salvataggio fallisce.
        """
        try:
            data = json.loads(self.data_edit.toPlainText())
            # Salva le variabili selezionate
            data['sweep_variable'] = self.sweep_var_combo.currentData()
            data['measured_variable'] = self.measured_var_combo.currentData()
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
        # Seleziona le variabili se presenti nel JSON
        sweep_var = self.data.get('sweep_variable', None)
        measured_var = self.data.get('measured_variable', None)
        if hasattr(self, 'sweep_var_combo') and sweep_var:
            idx = self.sweep_var_combo.findData(sweep_var)
            if idx >= 0:
                self.sweep_var_combo.setCurrentIndex(idx)
        if hasattr(self, 'measured_var_combo') and measured_var:
            idx = self.measured_var_combo.findData(measured_var)
            if idx >= 0:
                self.measured_var_combo.setCurrentIndex(idx)

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
        Salva i dati attuali nel file .was e chiude la dialog.
        Mostra un messaggio di errore se il salvataggio fallisce.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
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
        # Nuova mappa: type_key -> (label, series_key)
        self.type_map = {
            'power_supplies': (self.translator.t('power_supply') if hasattr(self.translator, 't') else 'Alimentatore', 'power_supplies_series'),
            'dataloggers': (self.translator.t('datalogger') if hasattr(self.translator, 't') else 'Datalogger', 'dataloggers_series'),
            'oscilloscopes': (self.translator.t('oscilloscope') if hasattr(self.translator, 't') else 'Oscilloscopio', 'oscilloscopes_series'),
            'electronic_loads': (self.translator.t('electronic_load') if hasattr(self.translator, 't') else 'Carico elettronico', 'electronic_loads_series')
        }
        # Carica dati file .inst
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.inst_data = json.load(f)
        except Exception:
            self.inst_data = {"instruments": []}
        # Carica libreria strumenti
        self.instrument_library = self.load_instrument_library()
        # Editor JSON raw (opzionale, solo per debug)
        self.data_edit = QTextEdit()
        self.data_edit.setText(json.dumps(self.inst_data, indent=2))
        # Lista strumenti già aggiunti
        layout.addWidget(QLabel(self.translator.t('added_instruments') if hasattr(self.translator, 't') else 'Strumenti aggiunti'))
        self.instruments_list_widget = QListWidget()
        layout.addWidget(self.instruments_list_widget)
        self.refresh_instruments_list()
        remove_btn = QPushButton(self.translator.t('remove_selected') if hasattr(self.translator, 't') else 'Rimuovi selezionato')
        remove_btn.clicked.connect(self.remove_selected_instrument)
        layout.addWidget(remove_btn)
        # Permetti doppio click per editare canali
        self.instruments_list_widget.itemDoubleClicked.connect(self.edit_instrument_channels)
        # --- Form per aggiunta nuovo strumento ---
        layout.addWidget(QLabel(self.translator.t('add_new_instrument') if hasattr(self.translator, 't') else 'Aggiungi nuovo strumento'))
        form = QFormLayout()
        self.instance_name_edit = QLineEdit()
        form.addRow(self.translator.t('instance_name') if hasattr(self.translator, 't') else 'Nome istanza', self.instance_name_edit)
        # Menu tipo strumento
        self.type_combo = QComboBox()
        for k, (v, _) in self.type_map.items():
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
        # Canali: layout verticale con pulsanti e lista scrollabile
        channel_box = QVBoxLayout()
        btn_row = QHBoxLayout()
        self.enable_all_btn = QPushButton(self.translator.t('enable_all') if hasattr(self.translator, 't') else 'Attiva tutti')
        self.disable_all_btn = QPushButton(self.translator.t('disable_all') if hasattr(self.translator, 't') else 'Disattiva tutti')
        self.enable_all_btn.clicked.connect(self.enable_all_channels)
        self.disable_all_btn.clicked.connect(self.disable_all_channels)
        btn_row.addWidget(self.enable_all_btn)
        btn_row.addWidget(self.disable_all_btn)
        channel_box.addLayout(btn_row)
        # Lista canali scrollabile
        self.channels_widget = QListWidget()
        self.channels_widget.setMinimumHeight(120)
        self.channels_widget.setMaximumHeight(200)
        self.channels_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        channel_box.addWidget(self.channels_widget)
        form.addRow(self.translator.t('channel_assignments') if hasattr(self.translator, 't') else 'Assegnazione canali', QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.FieldRole).widget().setLayout(channel_box)
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

    def enable_all_channels(self):
        """
        Abilita tutti i canali nella lista canali.
        """
        for i in range(self.channels_widget.count()):
            ch_conf = self.channels_widget.item(i).data(Qt.UserRole)
            ch_conf['used'] = True
            # Aggiorna label
            label = self.channels_widget.item(i).text()
            if label.startswith('[DIS] '):
                self.channels_widget.item(i).setText(label[6:])
        self.channels_widget.repaint()

    def disable_all_channels(self):
        """
        Disabilita tutti i canali nella lista canali.
        """
        for i in range(self.channels_widget.count()):
            ch_conf = self.channels_widget.item(i).data(Qt.UserRole)
            ch_conf['used'] = False
            # Aggiorna label
            label = self.channels_widget.item(i).text()
            if not label.startswith('[DIS] '):
                self.channels_widget.item(i).setText('[DIS] ' + label)
        self.channels_widget.repaint()

    def update_series_combo(self):
        """
        Aggiorna la combo delle serie in base al tipo selezionato.
        Gestisce struttura a lista di oggetti (series_id, series_name, models).
        """
        type_key = self.type_combo.currentData()
        self.series_combo.clear()
        self._current_series_list = []  # Salva la lista per uso in update_model_combo
        if not type_key or type_key not in self.type_map:
            return
        series_key = self.type_map[type_key][1]  # Usa la chiave corretta per la libreria
        if series_key not in self.instrument_library:
            return
        series_list = self.instrument_library[series_key]
        for s in series_list:
            label = s.get('series_name', s.get('series_id', str(s)))
            self.series_combo.addItem(label, s.get('series_id', label))
        self._current_series_list = series_list
        self.update_model_combo()

    def update_model_combo(self):
        """
        Aggiorna la combo dei modelli in base alla serie selezionata.
        Gestisce struttura a lista di oggetti.
        """
        type_key = self.type_combo.currentData()
        series_id = self.series_combo.currentData()
        self.model_combo.clear()
        if not type_key or not series_id or not hasattr(self, '_current_series_list'):
            return
        # Trova la serie selezionata
        series_obj = next((s for s in self._current_series_list if s.get('series_id') == series_id), None)
        if not series_obj or 'models' not in series_obj:
            return
        for m in series_obj['models']:
            label = m.get('name', m.get('id', str(m)))
            self.model_combo.addItem(label, m.get('id', label))
        self._current_model_list = series_obj['models']
        self.update_connection_types()

    def update_connection_types(self):
        """
        Aggiorna la combo dei tipi di connessione in base al modello selezionato.
        """
        type_key = self.type_combo.currentData()
        series_id = self.series_combo.currentData()
        model_id = self.model_combo.currentData()
        self.connection_type_combo.clear()
        if not type_key or not series_id or not model_id or not hasattr(self, '_current_model_list'):
            return
        # Trova il modello selezionato
        model_obj = next((m for m in self._current_model_list if m.get('id') == model_id), None)
        if not model_obj or 'interface' not in model_obj:
            return
        conn_types = model_obj['interface'].get('supported_connection_types', [])
        for conn in conn_types:
            label = conn.get('type', conn.get('address_format_example', str(conn)))
            self.connection_type_combo.addItem(label, label)
        self.update_channels_widget()

    def update_channels_widget(self):
        """
        Aggiorna la visualizzazione dei canali per il modello selezionato.
        Mostra solo i canali usati e precompila i campi se già configurati.
        Di default tutti i canali sono disattivati (used: False).
        """
        self.channels_widget.clear()
        type_key = self.type_combo.currentData()
        series_id = self.series_combo.currentData()
        model_id = self.model_combo.currentData()
        if not type_key or not series_id or not model_id or not hasattr(self, '_current_model_list'):
            return
        # Trova il modello selezionato
        model_obj = next((m for m in self._current_model_list if m.get('id') == model_id), None)
        n_channels = 0
        channel_labels = []
        if model_obj:
            caps = model_obj.get('capabilities', {})
            # Caso 1: lista di oggetti canale
            if 'channels' in caps and isinstance(caps['channels'], list):
                n_channels = len(caps['channels'])
                channel_labels = [ch.get('label', f"Ch{i+1}") for i, ch in enumerate(caps['channels'])]
            # Caso 2: channels è un intero (datalogger)
            elif 'channels' in caps and isinstance(caps['channels'], int):
                n_channels = caps['channels']
                channel_labels = [f"Ch{i+1}" for i in range(n_channels)]
            elif 'number_of_channels' in caps:
                n_channels = caps['number_of_channels']
                channel_labels = [f"Ch{i+1}" for i in range(n_channels)]
        # Cerca se esiste già una configurazione per questo strumento
        instance_name = self.instance_name_edit.text().strip()
        existing = None
        for inst in self.inst_data.get('instruments', []):
            if inst.get('instance_name', '') == instance_name:
                existing = inst
                break
        used_channels = existing.get('channels', []) if existing else []
        for ch_idx in range(n_channels):
            # Cerca se già configurato
            ch_conf = next((c for c in used_channels if c.get('index', -1) == ch_idx), None)
            if not ch_conf:
                ch_conf = {'index': ch_idx, 'used': False}  # Di default disattivato
                if type_key == 'dataloggers':
                    ch_conf['measured_variable'] = ''
                    ch_conf['attenuation'] = 1.0
                    ch_conf['measure_type'] = 'voltage'
                else:
                    ch_conf['variable'] = ''
                    ch_conf['attenuation'] = 1.0
            label = channel_labels[ch_idx] if ch_idx < len(channel_labels) else f"Ch{ch_idx+1}"
            if not ch_conf.get('used', False):
                label = '[DIS] ' + label
            if type_key == 'dataloggers':
                label += f" ({ch_conf.get('measured_variable','')})"
            elif type_key in ['power_supplies', 'electronic_loads']:
                label += f" ({ch_conf.get('variable','')})"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, ch_conf)
            self.channels_widget.addItem(item)

    def add_instrument_to_inst(self):
        """
        Aggiunge o aggiorna uno strumento nella lista, salvando solo i canali usati e tutte le variabili.
        """
        instance_name = self.instance_name_edit.text().strip()
        type_key = self.type_combo.currentData()
        series = self.series_combo.currentData()
        model = self.model_combo.currentData()
        conn_type = self.connection_type_combo.currentData()
        visa_addr = self.visa_address_label.text().strip()
        # Raccogli configurazione canali dalla QListWidget
        channels = []
        for i in range(self.channels_widget.count()):
            ch_conf = self.channels_widget.item(i).data(Qt.UserRole)
            # Salva solo se usato
            if ch_conf.get('used', True):
                channels.append(ch_conf)
        # Aggiorna o aggiungi
        found = False
        for inst in self.inst_data['instruments']:
            if inst.get('instance_name','') == instance_name:
                inst.update({
                    'instrument_type': type_key,
                    'series': series,
                    'model': model,
                    'connection_type': conn_type,
                    'visa_address': visa_addr,
                    'channels': channels
                })
                found = True
                break
        if not found:
            self.inst_data['instruments'].append({
                'instance_name': instance_name,
                'instrument_type': type_key,
                'series': series,
                'model': model,
                'connection_type': conn_type,
                'visa_address': visa_addr,
                'channels': channels
            })
        self.refresh_instruments_list()
        self.save_inst_file()
        self.update_channels_widget()

    def edit_instrument_channels(self, item):
        """
        Apre la ChannelConfigDialog per modificare i canali dello strumento selezionato.
        """
        inst = item.data(Qt.UserRole)
        dlg = ChannelConfigDialog(inst, self.translator, self)
        if dlg.exec_() == QDialog.Accepted:
            # Aggiorna i canali modificati
            inst['channels'] = dlg.get_channels()
            self.refresh_instruments_list()
            self.save_inst_file()

    def open_visa_address_dialog(self):
        """
        Dialog per comporre l'indirizzo VISA (placeholder, da implementare secondo necessità).
        """
        from PyQt5.QtWidgets import QInputDialog
        addr, ok = QInputDialog.getText(self, self.translator.t('compose_visa_address'), self.translator.t('enter_visa_address'))
        if ok:
            self.visa_address_label.setText(addr)

    def save_changes(self):
        """
        Salva i dati attuali nel file .inst e chiude la dialog.
        Mostra un messaggio di errore se il salvataggio fallisce.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.inst_data, f, indent=2)
            self.accept()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.translator.t('error'), str(e))

    def load_instrument_library(self):
        """
        Carica la libreria strumenti da Instruments_LIB/instruments_lib.json.
        Gestisce sia la chiave 'instrument_library' sia struttura piatta. Restituisce sempre un dict con tutte le chiavi attese.
        """
        import os, json
        lib_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Instruments_LIB', 'instruments_lib.json')
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Se la chiave principale è 'instrument_library', usala
            if 'instrument_library' in data:
                data = data['instrument_library']
            # Assicurati che tutte le chiavi attese siano presenti
            for k in ['power_supplies_series', 'dataloggers_series', 'oscilloscopes_series', 'electronic_loads_series']:
                if k not in data:
                    data[k] = []
            return data
        except Exception as e:
            # In caso di errore, restituisci struttura vuota con tutte le chiavi
            return {
                'power_supplies_series': [],
                'dataloggers_series': [],
                'oscilloscopes_series': [],
                'electronic_loads_series': []
            }

    def refresh_instruments_list(self):
        """
        Aggiorna la QListWidget degli strumenti aggiunti, mostrando nome istanza, tipo, modello e canali abilitati.
        """
        self.instruments_list_widget.clear()
        for inst in self.inst_data.get('instruments', []):
            instance_name = inst.get('instance_name', '')
            type_key = inst.get('instrument_type', '')
            model = inst.get('model', '')
            channels = inst.get('channels', [])
            # Mostra solo i canali abilitati
            enabled_channels = [ch for ch in channels if ch.get('used', True)]
            ch_descr = ', '.join(
                ch.get('measured_variable', ch.get('variable', f"Ch{ch.get('index', '?')+1}"))
                for ch in enabled_channels
            )
            label = f"{instance_name} [{type_key}] {model} | Canali: {ch_descr}"
            item = QListWidgetItem(label)
            # Salva l'intero dict per doppio click/modifica
            item.setData(Qt.UserRole, inst)
            self.instruments_list_widget.addItem(item)

    def remove_selected_instrument(self):
        """
        Rimuove lo strumento selezionato dalla lista e aggiorna il file .inst.
        """
        selected = self.instruments_list_widget.currentRow()
        if selected < 0:
            return
        # Rimuovi dallo storage
        if 0 <= selected < len(self.inst_data.get('instruments', [])):
            del self.inst_data['instruments'][selected]
            self.refresh_instruments_list()
            self.save_inst_file()

    def save_inst_file(self):
        """
        Salva i dati attuali di self.inst_data nel file .inst associato.
        Mostra un messaggio di errore se il salvataggio fallisce.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.inst_data, f, indent=2)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.translator.t('error'), f"Errore salvataggio .inst: {e}")

class ChannelConfigDialog(QDialog):
    """
    Dialog di configurazione avanzata dei canali per uno strumento.
    Permette di abilitare/disabilitare canali, modificare variabile, attenuazione e tipo misura.
    """
    def __init__(self, instrument, translator, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translator.t('channel_config') if hasattr(translator, 't') else 'Configurazione canali')
        self.instrument = instrument
        self.translator = translator
        self.channels = instrument.get('channels', [])
        self.type_key = instrument.get('instrument_type', '')
        layout = QVBoxLayout()
        # Titolo
        layout.addWidget(QLabel(translator.t('channel_config_title') if hasattr(translator, 't') else 'Configurazione canali'))
        # Lista canali
        self.channel_widgets = []  # Per raccogliere i widget di ogni canale
        for idx, ch in enumerate(self.channels):
            group = QGroupBox(f"Ch{idx+1}")
            form = QFormLayout()
            # Abilitazione canale
            used_cb = QCheckBox(translator.t('channel_used') if hasattr(translator, 't') else 'Usa questo canale')
            used_cb.setChecked(ch.get('used', True))
            form.addRow(used_cb)
            # Variabile associata
            if self.type_key == 'dataloggers':
                var_label = translator.t('measured_variable') if hasattr(translator, 't') else 'Variabile misurata'
                var_edit = QLineEdit(ch.get('measured_variable', ''))
            else:
                var_label = translator.t('variable') if hasattr(translator, 't') else 'Variabile'
                var_edit = QLineEdit(ch.get('variable', ''))
            form.addRow(var_label, var_edit)
            # Attenuazione (solo se presente)
            att_label = translator.t('attenuation') if hasattr(translator, 't') else 'Attenuazione'
            att_edit = QLineEdit(str(ch.get('attenuation', '1')))
            form.addRow(att_label, att_edit)
            # Tipo misura (solo per datalogger)
            if self.type_key == 'dataloggers':
                mt_label = translator.t('measure_type') if hasattr(translator, 't') else 'Tipo misura'
                mt_combo = QComboBox()
                mt_combo.addItems(['voltage', 'current', 'temperature', 'resistance'])
                mt_combo.setCurrentText(ch.get('measure_type', 'voltage'))
                form.addRow(mt_label, mt_combo)
            else:
                mt_combo = None
            group.setLayout(form)
            layout.addWidget(group)
            # Salva riferimenti per raccolta dati
            self.channel_widgets.append({
                'used': used_cb,
                'variable': var_edit,
                'attenuation': att_edit,
                'measure_type': mt_combo
            })
        # Pulsanti OK/Annulla
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(translator.t('ok') if hasattr(translator, 't') else 'OK')
        cancel_btn = QPushButton(translator.t('cancel') if hasattr(translator, 't') else 'Annulla')
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_channels(self):
        """
        Restituisce la lista aggiornata dei canali con i dati inseriti dall'utente.
        """
        new_channels = []
        for idx, widgets in enumerate(self.channel_widgets):
            used = widgets['used'].isChecked()
            if not used:
                continue  # Salva solo canali abilitati
            ch = {'index': idx, 'used': True}
            var_val = widgets['variable'].text().strip()
            if self.type_key == 'dataloggers':
                ch['measured_variable'] = var_val
                mt_combo = widgets['measure_type']
                if mt_combo:
                    ch['measure_type'] = mt_combo.currentText()
            else:
                ch['variable'] = var_val
            # Attenuazione
            try:
                ch['attenuation'] = float(widgets['attenuation'].text().replace(',', '.'))
            except Exception:
                ch['attenuation'] = 1.0
            new_channels.append(ch)
        return new_channels

class InstrumentLibraryDialog(QDialog):
    """
    Dialog per la visualizzazione (sola lettura) della libreria strumenti.
    """
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.t('instrument_library') if hasattr(self.translator, 't') else 'Libreria strumenti')
        self.setModal(True)
        layout = QVBoxLayout()
        # Carica la libreria strumenti
        lib_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Instruments_LIB', 'instruments_lib.json')
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'instrument_library' in data:
                data = data['instrument_library']
            text = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            text = f"Errore nel caricamento della libreria strumenti:\n{e}"
        edit = QTextEdit()
        edit.setReadOnly(True)
        edit.setText(text)
        layout.addWidget(edit)
        close_btn = QPushButton(self.translator.t('close') if hasattr(self.translator, 't') else 'Chiudi')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)

def main():
    """
    Funzione principale per avviare l'applicazione PyQt5.
    """
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Imposta nome e organizzazione per QSettings
    app.setOrganizationName('LabAutomation')
    app.setApplicationName('Open Lab Automation')
    # Carica lingua da impostazioni

    settings = QSettings('LabAutomation', 'App')
    lang = settings.value('language', 'it')
    translator = Translator(default_lang=lang)
    window = MainWindow()



    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()