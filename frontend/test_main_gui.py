import os
import pytest
from PyQt5.QtWidgets import QApplication
from frontend.main import MainWindow, SettingsDialog, DatabaseDialog, AddFileDialog, EffFileDialog, WasFileDialog, InstFileDialog, Translator

@pytest.fixture(scope="session")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def main_window(app, tmp_path):
    # Setup: crea una cartella temporanea e copia un appinfo.json minimale
    appinfo = tmp_path / "appinfo.json"
    appinfo.write_text('{"app_name": "TestApp", "version": "1.0", "author": "Test", "repository": ""}', encoding="utf-8")
    # Crea anche una lingua minima
    lang_dir = tmp_path / "lang"
    lang_dir.mkdir()
    (lang_dir / "en.json").write_text('{"remote_control": "Remote Control", "settings": "Settings", "database_settings": "Database", "add_file": "Add File", "edit_eff_file": "Edit .eff", "edit_was_file": "Edit .was", "edit_inst_file": "Edit .inst", "save": "Save", "apply": "Apply", "file_type": "File Type", "file_name": "File Name", "efficiency_settings": "Efficiency", "oscilloscope_settings": "Oscilloscope", "vin_loop": "Vin loop", "vin_list_mode": "List", "vin_range_mode": "Range", "vin_list_placeholder": "1,2,3", "vin_start_placeholder": "Start", "vin_stop_placeholder": "Stop", "vin_points_label": "Points", "apply_to_data": "Apply", "efficiency_data": "Efficiency Data", "oscilloscope_settings_data": "Oscilloscope Data", "instruments_data": "Instruments Data", "error": "Error"}', encoding="utf-8")
    # Cambia la working dir temporaneamente
    cwd = os.getcwd()
    os.chdir(str(tmp_path))
    mw = MainWindow()
    yield mw
    os.chdir(cwd)


def test_mainwindow_starts(main_window, qtbot):
    main_window.show()
    qtbot.waitExposed(main_window)
    assert main_window.isVisible()
    assert main_window.windowTitle() == "TestApp"
    assert main_window.tabs.count() > 0


def test_open_settings_dialog(main_window, qtbot):
    dlg = SettingsDialog(main_window, main_window.translator)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    dlg.close()


def test_open_database_dialog(main_window, qtbot):
    dlg = DatabaseDialog(main_window, main_window.translator)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    dlg.close()


def test_addfile_dialog(main_window, qtbot):
    dlg = AddFileDialog(main_window, main_window.translator)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    dlg.close()


def test_translator_loads(main_window):
    t = main_window.translator
    assert t.t("remote_control") == "Remote Control"
    assert t.t("settings") == "Settings"


def test_efffile_dialog(tmp_path, main_window, qtbot):
    eff_file = tmp_path / "test.eff"
    eff_file.write_text('{"type": "efficiency", "data": {"Vin loop": [1,2,3]}}', encoding="utf-8")
    dlg = EffFileDialog(str(eff_file), main_window.translator)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    dlg.close()


def test_wasfile_dialog(tmp_path, main_window, qtbot):
    was_file = tmp_path / "test.was"
    was_file.write_text('{"type": "oscilloscope_settings", "settings": {"time_per_div": 1, "volt_per_div": 2}}', encoding="utf-8")
    dlg = WasFileDialog(str(was_file), main_window.translator)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    dlg.close()


def test_instfile_dialog(tmp_path, main_window, qtbot):
    inst_file = tmp_path / "test.inst"
    inst_file.write_text('{"instruments": []}', encoding="utf-8")
    dlg = InstFileDialog(str(inst_file), main_window.translator)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    dlg.close()
