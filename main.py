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
        items = os.listdir(path)
        prefixes_to_remove = [prefix.strip() for prefix in self.prefix_input.text().split(',')]

        for item in items:
            full_path = os.path.join(path, item)

            if item.startswith('.DS_Store'):
                continue

            # Удаление файлов по указанным шаблонам
            if (item.startswith('[DMC.RIP]') and item.endswith('.url')) or (
                    item.startswith('[WWW.SW.BAND]') and (item.endswith('.url') or item.endswith('.docx'))):
                os.remove(full_path)
                continue

            # Переименование файлов, начинающихся на указанные префиксы
            for prefix in prefixes_to_remove:
                if item.startswith(prefix):
                    new_name = item.replace(prefix, '').strip()
                    new_full_path = os.path.join(path, new_name)
                    os.rename(full_path, new_full_path)
                    item = new_name
                    break  # Выход из цикла, если префикс был найден и удалён

            # Вывод структуры папки
            self.output_area.append(' ' * indent + f"📁 {item}")

            # Если элемент является папкой, рекурсивно обрабатываем её содержимое
            if os.path.isdir(full_path):
                self.rename_and_print_directory_structure(full_path, indent + 4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DirectoryCleaner()
    ex.resize(600, 400)
    ex.show()
    sys.exit(app.exec_())
