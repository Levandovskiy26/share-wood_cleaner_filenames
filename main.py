import os


def rename_and_print_directory_structure(path, indent=3):
    # Получаем список всех элементов в директории
    items = os.listdir(path)

    for item in items:
        # Полный путь к элементу
        full_path = os.path.join(path, item)

        # Пропускаем системные файлы MacOS
        if item.startswith('.DS_Store'):
            continue

        # Удаляем файлы по указанным шаблонам
        if (item.startswith('[DMC.RIP]') and item.endswith('.url')) or (item.startswith('[WWW.SW.BAND]') and (item.endswith('.url') or item.endswith('.docx'))):
            os.remove(full_path)
            continue

        # Проверяем, начинается ли название с '[SW.BAND]'
        if item.startswith('[SW.BAND]'):
            # Создаем новое имя, убирая '[SW.BAND]' в начале
            new_name = item.replace('[SW.BAND]', '').strip()
            new_full_path = os.path.join(path, new_name)

            # Переименовываем элемент
            os.rename(full_path, new_full_path)
            # print(' ' * indent + f"Переименовано: {new_name}")
            item = new_name  # Обновляем имя для дальнейшего использования

        # Определяем, является ли элемент папкой или файлом и добавляем соответствующий эмодзи
        if os.path.isdir(full_path):
            print(' ' * indent + f"🗂 {item}")
            # Если это папка, рекурсивно выводим её содержимое
            rename_and_print_directory_structure(full_path, indent + 4)
        else:
            print(' ' * indent + f"📁 {item}")


# Получаем путь к текущему скрипту
current_directory = os.path.dirname(os.path.abspath(__file__))

# Ищем папку в текущей директории
folder = next((item for item in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, item))),
              None)

# Если папка найдена, выводим её структуру и переименовываем файлы и папки
if folder:
    print(f"Структура папки: n{folder}")
    rename_and_print_directory_structure(os.path.join(current_directory, folder))
else:
    print("Папка не найдена.")
