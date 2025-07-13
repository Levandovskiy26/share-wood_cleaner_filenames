import os
import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QLabel, QCheckBox, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt


class DirectoryCleaner(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.load_settings()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Очистка папки')
        layout = QVBoxLayout()

        # Путь к папке
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.settings.get("last_path", ""))
        self.choose_button = QPushButton('Выбрать папку', self)
        self.choose_button.clicked.connect(self.choose_folder)
        path_layout.addWidget(QLabel("Путь:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.choose_button)
        layout.addLayout(path_layout)

        # Префиксы
        prefix_layout = QHBoxLayout()
        self.prefix_area = QTextEdit()
        self.prefix_area.setPlainText(self.settings.get("prefixes", "[SW.BAND]\n[WWW.SW.BAND]"))
        prefix_layout.addWidget(QLabel("Префиксы для удаления:"))
        prefix_layout.addWidget(self.prefix_area)
        layout.addLayout(prefix_layout)

        # Regex
        self.regex_input = QLineEdit()
        self.regex_input.setText(self.settings.get("regex", r"$$DMC\.RIP$$.*\.url"))
        layout.addWidget(QLabel("Regex-шаблоны (через запятую):"))
        layout.addWidget(self.regex_input)

        # Dry run
        self.dry_run_checkbox = QCheckBox("Тестовый режим (Dry Run)", self)
        layout.addWidget(self.dry_run_checkbox)

        # Лог вывода
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Прогрессбар
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.clear_button = QPushButton('Очистить', self)
        self.clear_button.clicked.connect(self.start_cleaning)
        self.reset_button = QPushButton('Сбросить лог', self)
        self.reset_button.clicked.connect(self.reset_log)
        btn_layout.addWidget(self.clear_button)
        btn_layout.addWidget(self.reset_button)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self.path_input.setText(folder)

    def log(self, text, color="black"):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(text + "\n", fmt)
        self.output_area.setTextCursor(cursor)

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                import json
                self.settings = json.load(f)
        except Exception:
            self.settings = {}

    def save_settings(self):
        import json
        data = {
            "last_path": self.path_input.text(),
            "prefixes": self.prefix_area.toPlainText(),
            "regex": self.regex_input.text()
        }
        with open("settings.json", "w") as f:
            json.dump(data, f)

    def reset_log(self):
        self.output_area.clear()
        self.progress_bar.setValue(0)

    def start_cleaning(self):
        paths = self.path_input.text().splitlines()
        self.save_settings()

        for path in paths:
            path = path.strip()
            if not os.path.isdir(path):
                self.log(f"[Ошибка] Путь не найден: {path}", "red")
                continue

            self.log(f"\n🔄 Обработка папки: {path}\n", "blue")
            self.rename_and_print_directory_structure(path)

        self.log("\n✅ Очистка завершена.\n", "green")

    def rename_and_print_directory_structure(self, path, indent=0):
        prefixes_to_remove = [line.strip() for line in self.prefix_area.toPlainText().splitlines()]
        regex_patterns = [p.strip() for p in self.regex_input.text().split(',')]

        parent_dir = os.path.dirname(path)
        folder_name = os.path.basename(path)

        new_folder_name = folder_name
        for prefix in prefixes_to_remove:
            if folder_name.startswith(prefix):
                new_folder_name = folder_name.replace(prefix, '').strip()
                break

        old_full_path = path
        new_full_path = os.path.join(parent_dir, new_folder_name)

        if new_folder_name != folder_name:
            self.log(' ' * indent + f"🔄 Переименована папка: {folder_name} → {new_folder_name}", "blue")
            if not self.dry_run_checkbox.isChecked():
                try:
                    os.rename(old_full_path, new_full_path)
                except Exception as e:
                    self.log(' ' * indent + f"❌ Ошибка переименования: {e}", "red")
                path = new_full_path

        self.log(' ' * indent + f"📁 {new_folder_name}", "black")

        try:
            items = os.listdir(path)
        except PermissionError:
            self.log(' ' * (indent + 4) + "[Ошибка доступа]", "red")
            return

        total = len(items)
        count = 0

        for item in items:
            full_path = os.path.join(path, item)
            count += 1
            self.progress_bar.setValue(int(count / total * 100))

            if item.startswith('.DS_Store'):
                continue

            matched_regex = False
            for pattern in regex_patterns:
                if pattern and re.match(pattern, item):
                    matched_regex = True
                    try:
                        if os.path.isdir(full_path):
                            os.rmdir(full_path)
                        elif not self.dry_run_checkbox.isChecked():
                            os.remove(full_path)
                        self.log(' ' * (indent + 4) + f"🗑️ Удалён: {item}", "red")
                    except Exception as e:
                        self.log(' ' * (indent + 4) + f"❌ Ошибка удаления: {e}", "red")
                    break

            # Удаление конкретных файлов по имени
            if item == "Прочти перед изучением!.docx" or item == "SHAREWOOD_ZERKALO_COM_90000_курсов_на_нашем_форуме!.url":
                try:
                    if os.path.isdir(full_path):
                        os.rmdir(full_path)
                    elif not self.dry_run_checkbox.isChecked():
                        os.remove(full_path)
                    self.log(' ' * (indent + 4) + f"🗑️ Удалён: {item}", "red")
                except Exception as e:
                    self.log(' ' * (indent + 4) + f"❌ Ошибка удаления: {e}", "red")
                continue

            if matched_regex:
                continue

            new_item = item
            for prefix in prefixes_to_remove:
                if item.startswith(prefix):
                    new_item = item.replace(prefix, '').strip()
                    break

            if new_item != item:
                new_full_path_item = os.path.join(path, new_item)
                self.log(' ' * (indent + 4) + f"🔄 Переименован: {item} → {new_item}", "blue")
                if not self.dry_run_checkbox.isChecked():
                    try:
                        os.rename(full_path, new_full_path_item)
                    except Exception as e:
                        self.log(' ' * (indent + 4) + f"❌ Ошибка переименования: {e}", "red")
                item = new_item

            full_path_after_rename = os.path.join(path, item)

            if os.path.isdir(full_path_after_rename):
                self.rename_and_print_directory_structure(full_path_after_rename, indent + 4)
            else:
                self.log(' ' * (indent + 4) + f"📄 {item}", "black")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DirectoryCleaner()
    ex.resize(800, 600)
    ex.show()
    sys.exit(app.exec_())
