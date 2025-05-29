import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox


class DirectoryCleaner(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Очистка папки')

        # Создаем вертикальный layout
        layout = QVBoxLayout()

        # Поле для ввода пути к папке
        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText('Введите путь к папке...')
        layout.addWidget(self.path_input)

        # Поле для ввода префиксов, которые нужно удалять
        self.prefix_input = QLineEdit(self)
        self.prefix_input.setPlaceholderText('Введите префиксы для удаления (через запятую)...')
        self.prefix_input.setText('[SW.BAND]')  # Установка начального значения
        layout.addWidget(self.prefix_input)

        # Окно для вывода структуры папки
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Кнопка "Очистить"
        self.clear_button = QPushButton('Очистить', self)
        self.clear_button.clicked.connect(self.clear_directory)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def clear_directory(self):
        path = self.path_input.text()
        if os.path.isdir(path):
            self.output_area.clear()
            self.rename_and_print_directory_structure(path)
            QMessageBox.information(self, 'Успех', 'Папка очищена!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Указанный путь не является папкой.')

    def rename_and_print_directory_structure(self, path, indent=0):
        prefixes_to_remove = [prefix.strip() for prefix in self.prefix_input.text().split(',')]

        # Сначала проверяем и переименовываем текущую папку, если она подходит под условия
        parent_dir = os.path.dirname(path)
        folder_name = os.path.basename(path)

        new_folder_name = folder_name
        for prefix in prefixes_to_remove:
            if folder_name.startswith(prefix):
                new_folder_name = folder_name.replace(prefix, '').strip()
                break

        if new_folder_name != folder_name:
            new_path = os.path.join(parent_dir, new_folder_name)
            os.rename(path, new_path)
            path = new_path  # Обновляем путь после переименования
            folder_name = new_folder_name

        # Выводим текущую папку
        self.output_area.append(' ' * indent + f"📁 {folder_name}")

        # Теперь обрабатываем содержимое этой папки
        try:
            items = os.listdir(path)
        except PermissionError:
            self.output_area.append(' ' * (indent + 4) + "[Ошибка доступа]")
            return

        for item in items:
            full_path = os.path.join(path, item)

            if item.startswith('.DS_Store'):
                continue

            # Удаление файлов по шаблонам
            if (item.startswith('[DMC.RIP]') and item.endswith('.url')) or (
                    item.startswith('[WWW.SW.BAND]') and (item.endswith('.url') or item.endswith('.docx'))):
                try:
                    if os.path.isdir(full_path):
                        os.rmdir(full_path)
                    else:
                        os.remove(full_path)
                except Exception as e:
                    self.output_area.append(' ' * (indent + 4) + f"[Ошибка удаления: {e}]")
                continue

            # Переименование файлов/папок, начинающихся с указанных префиксов
            new_item = item
            for prefix in prefixes_to_remove:
                if item.startswith(prefix):
                    new_item = item.replace(prefix, '').strip()
                    new_full_path = os.path.join(path, new_item)
                    try:
                        os.rename(full_path, new_full_path)
                    except Exception as e:
                        self.output_area.append(' ' * (indent + 4) + f"[Ошибка переименования: {e}]")
                    break  # выходим после первого совпадения

            # Если это папка, рекурсивно обрабатываем её
            new_full_path = os.path.join(path, new_item)
            if os.path.isdir(new_full_path):
                self.rename_and_print_directory_structure(new_full_path, indent + 4)
            else:
                self.output_area.append(' ' * (indent + 4) + f"📄 {new_item}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DirectoryCleaner()
    ex.resize(600, 400)
    ex.show()
    sys.exit(app.exec_())
