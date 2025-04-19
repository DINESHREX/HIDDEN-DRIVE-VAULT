
import os
import json
import psutil
import shutil
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget, QFileDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QInputDialog, QComboBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from utils.usb_utils import get_vault_files, create_hidden_vault_folder

VAULT_FOLDER_NAME = ".vault"
META_FILENAME = ".vault_file_meta.json"
VAULT_KEY_FILENAME = "vault_key.json"

class USBVaultUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Hidden USB Vault — Per-Drive Passwords")
        self.setGeometry(200, 100, 960, 680)
        self.setStyleSheet("background-color: #121212; color: #FFFFFF;")
        self.usb_path = None
        self.vault_unlocked = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("🛡️ USB Vault — Secure Each Drive Separately")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #00d8ff;")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        self.drive_selector = QComboBox()
        self.drive_selector.addItem("Select a drive to create/access vault")
        self.drive_selector.currentIndexChanged.connect(self.on_drive_selected)
        self.layout.addWidget(self.drive_selector)

        self.vault_list = QListWidget()
        self.vault_list.setStyleSheet("""
            QListWidget {
                background-color: #1e272e;
                color: #00ff99;
                border: 2px solid #00cec9;
                font-family: Consolas;
                font-size: 14px;
            }
        """)
        self.layout.addWidget(self.vault_list)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("📁 Add File")
        self.restore_btn = QPushButton("📤 Restore")
        self.remove_btn = QPushButton("❌ Remove")
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.delete_btn = QPushButton("🗑️ Delete Vault")
        self.exit_btn = QPushButton("🚪 Exit")

        for btn in [self.add_btn, self.restore_btn, self.remove_btn, self.refresh_btn, self.delete_btn, self.exit_btn]:
            btn.setFixedHeight(42)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #00cec9;
                    color: #ffffff;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0984e3;
                }
            """)

        self.add_btn.clicked.connect(self.add_file_to_vault)
        self.restore_btn.clicked.connect(self.restore_selected_file)
        self.remove_btn.clicked.connect(self.remove_selected_file)
        self.refresh_btn.clicked.connect(self.refresh_lists)
        self.delete_btn.clicked.connect(self.delete_vault)
        self.exit_btn.clicked.connect(self.close)

        for btn in [self.add_btn, self.restore_btn, self.remove_btn, self.refresh_btn, self.delete_btn, self.exit_btn]:
            button_layout.addWidget(btn)

        self.layout.addLayout(button_layout)
        self.populate_all_drives()

    def get_password_file_path(self):
        return os.path.join(self.usb_path, VAULT_FOLDER_NAME, VAULT_KEY_FILENAME)

    def populate_all_drives(self):
        self.drive_selector.blockSignals(True)
        self.drive_selector.clear()
        self.drive_selector.addItem("Select a drive to create/access vault")
        drives = [p.mountpoint for p in psutil.disk_partitions() if os.path.exists(p.mountpoint)]
        self.drive_selector.addItems(drives)
        self.drive_selector.blockSignals(False)

    def on_drive_selected(self, index):
        if index == 0:
            return
        self.usb_path = self.drive_selector.currentText()
        vault_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME)
        create_hidden_vault_folder(vault_path)

        password_path = self.get_password_file_path()

        if not os.path.exists(password_path):
            new_pass, ok = QInputDialog.getText(self, "Set Vault Password", "Create new password:", QLineEdit.Password)
            if ok and new_pass:
                with open(password_path, "w") as f:
                    json.dump({"password": new_pass}, f)
                if os.name == 'nt':
                    os.system(f'attrib +h "{password_path}"')
            else:
                QMessageBox.warning(self, "Cancelled", "Password not set.")
                return

        password, ok = QInputDialog.getText(self, "Vault Unlock", "Enter Vault Password:", QLineEdit.Password)
        if ok and password == self.get_stored_password():
            self.vault_unlocked = True
            self.refresh_lists()
        else:
            QMessageBox.critical(self, "Access Denied", "Wrong password.")
            self.vault_list.clear()

    def get_stored_password(self):
        try:
            with open(self.get_password_file_path(), "r") as f:
                return json.load(f)["password"]
        except:
            return ""

    def refresh_lists(self):
        self.vault_list.clear()
        if self.vault_unlocked and self.usb_path:
            vault_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME)
            files = get_vault_files(vault_path)
            self.vault_list.addItems([f for f in files if not f.endswith(META_FILENAME) and not f.endswith(VAULT_KEY_FILENAME)])

    def load_file_meta(self):
        try:
            meta_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME, META_FILENAME)
            with open(meta_path, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_file_meta(self, meta):
        try:
            meta_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME, META_FILENAME)
            if os.name == 'nt' and os.path.exists(meta_path):
                os.system(f'attrib -r -s -h "{meta_path}"')
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)
            if os.name == 'nt':
                os.system(f'attrib +h +s "{meta_path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update metadata: {e}")

    def add_file_to_vault(self):
        if not self.vault_unlocked or not self.usb_path:
            QMessageBox.warning(self, "Vault Locked", "Unlock the vault first.")
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Select files to move to vault")
        if not files:
            return
        vault_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME)
        meta = self.load_file_meta()
        for file_path in files:
            name = os.path.basename(file_path)
            dest = os.path.join(vault_path, name)
            try:
                shutil.move(file_path, dest)
                meta[dest] = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to move file: {e}")
        self.save_file_meta(meta)
        self.refresh_lists()

    def restore_selected_file(self):
        if not self.vault_unlocked or not self.usb_path:
            return
        item = self.vault_list.currentItem()
        if item:
            filename = item.text()
            vault_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME)
            full_path = os.path.join(vault_path, filename)
            meta = self.load_file_meta()
            original_path = meta.get(full_path)

            if original_path and os.path.exists(os.path.dirname(original_path)):
                dest = original_path
            else:
                folder = QFileDialog.getExistingDirectory(self, "Select restore location")
                if not folder:
                    return
                dest = os.path.join(folder, filename)

            try:
                shutil.move(full_path, dest)
                meta.pop(full_path, None)
                self.save_file_meta(meta)
                self.refresh_lists()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Restore failed: {e}")

    def remove_selected_file(self):
        if not self.vault_unlocked or not self.usb_path:
            return
        item = self.vault_list.currentItem()
        if item:
            filename = item.text()
            vault_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME)
            full_path = os.path.join(vault_path, filename)
            meta = self.load_file_meta()
            confirm = QMessageBox.question(self, "Delete File", f"Delete '{filename}' from vault?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    os.remove(full_path)
                    meta.pop(full_path, None)
                    self.save_file_meta(meta)
                    self.refresh_lists()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Delete failed: {e}")

    def delete_vault(self):
        if not self.usb_path:
            QMessageBox.warning(self, "No Drive", "Please select a drive first.")
            return
        confirm = QMessageBox.question(self, "Delete Vault", "Permanently delete the vault?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                vault_path = os.path.join(self.usb_path, VAULT_FOLDER_NAME)
                shutil.rmtree(vault_path, ignore_errors=True)
                self.vault_list.clear()
                self.vault_unlocked = False
                self.populate_all_drives()
                QMessageBox.information(self, "Done", "Vault deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = USBVaultUI()
    window.show()
    sys.exit(app.exec())
