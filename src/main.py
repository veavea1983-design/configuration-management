"""Эмулятор командной оболочки UNIX."""

import argparse
import getpass
import json
import os
import platform
import re
import socket
import sys

from vfs import VirtualFileSystem


def get_prompt():
    """Сформировать приглашение из данных ОС. 1"""
    username = getpass.getuser()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$ "


def expand_variables(text):
    """Раскрыть переменные окружения. 1"""
    pattern = r"\$([A-Za-z_][A-Za-z0-9_]*)"

    def replace_variable(match):
        """Подставить значение переменной окружения. 1"""
        name = match.group(1)
        return os.environ.get(name, "")

    return re.sub(pattern, replace_variable, text)


def save_vfs_command(arguments, vfs):
    """Выполнить команду сохранения VFS. 3"""
    if len(arguments) != 1:
        print("vfs-save: требуется один аргумент — путь")
        return False

    if vfs is None:
        print("vfs-save: виртуальная система не загружена")
        return False

    try:
        vfs.save(arguments[0])
    except (OSError, ValueError) as error:
        print(f"vfs-save: ошибка: {error}")
        return False

    print(f"VFS сохранена: {arguments[0]}")
    return True


def ls_command(arguments, vfs):
    """Вывести содержимое виртуального каталога. 4"""
    if len(arguments) > 1:
        print("ls: слишком много аргументов")
        return False

    if vfs is None:
        print(f"ls: аргументы = {arguments}")
        return True

    path = arguments[0] if arguments else "."

    try:
        for name in vfs.list_directory(path):
            print(name)
    except (OSError, ValueError) as error:
        print(f"ls: {error}")
        return False

    return True


def cd_command(arguments, vfs):
    """Перейти в виртуальный каталог. 4"""
    if len(arguments) > 1:
        print("cd: слишком много аргументов")
        return False

    if vfs is None:
        print(f"cd: аргументы = {arguments}")
        return True

    path = arguments[0] if arguments else "/"

    try:
        vfs.change_directory(path)
    except (OSError, ValueError) as error:
        print(f"cd: {error}")
        return False

    return True


def clear_command(arguments):
    """Очистить экран терминала. 4"""
    if arguments:
        print("clear: аргументы не поддерживаются")
        return False

    print("\033[2J\033[H", end="")
    return True


def uname_command(arguments):
    """Вывести название операционной системы. 4"""
    if arguments:
        print("uname: аргументы не поддерживаются")
        return False

    print(platform.system())
    return True


def tree_command(arguments, vfs):
    """Вывести дерево виртуальной файловой системы. 4"""
    if len(arguments) > 1:
        print("tree: слишком много аргументов")
        return False

    if vfs is None:
        print("tree: виртуальная система не загружена")
        return False

    path = arguments[0] if arguments else "."

    try:
        print(vfs.render_tree(path))
    except (OSError, ValueError) as error:
        print(f"tree: {error}")
        return False

    return True


def touch_command(arguments, vfs):
    """Создать пустой файл в виртуальной системе. 5"""
    if len(arguments) != 1:
        print("touch: требуется один аргумент — имя файла")
        return False

    if vfs is None:
        print("touch: виртуальная система не загружена")
        return False

    try:
        vfs.touch_file(arguments[0])
    except (OSError, ValueError) as error:
        print(f"touch: {error}")
        return False

    return True


def rm_command(arguments, vfs):
    """Удалить файл из виртуальной системы. 5"""
    if len(arguments) != 1:
        print("rm: требуется один аргумент — имя файла")
        return False

    if vfs is None:
        print("rm: виртуальная система не загружена")
        return False

    try:
        vfs.remove_file(arguments[0])
    except (OSError, ValueError) as error:
        print(f"rm: {error}")
        return False

    return True


def run_shell_command(command, arguments, vfs):
    """Выполнить поддерживаемую команду. 4-5"""
    if command == "ls":
        return ls_command(arguments, vfs)

    if command == "cd":
        return cd_command(arguments, vfs)

    if command == "clear":
        return clear_command(arguments)

    if command == "uname":
        return uname_command(arguments)

    if command == "tree":
        return tree_command(arguments, vfs)

    if command == "touch":
        return touch_command(arguments, vfs)

    if command == "rm":
        return rm_command(arguments, vfs)

    if command == "vfs-save":
        return save_vfs_command(arguments, vfs)

    print(f"{command}: команда не найдена")
    return False


def process_command(line, vfs=None):
    """Обработать команду и вернуть статусы. 2-4"""
    expanded = expand_variables(line)
    parts = expanded.split()

    if not parts:
        return True, True

    command = parts[0]
    arguments = parts[1:]

    if command == "exit":
        if arguments:
            print("exit: неверные аргументы")
            return True, False
        return False, True

    success = run_shell_command(command, arguments, vfs)
    return True, success


def execute_command(line, vfs=None):
    """Выполнить команду в интерактивном режиме. 1-3"""
    continue_running, _ = process_command(line, vfs)
    return continue_running


def parse_arguments(argv=None):
    """Прочитать параметры командной строки. 2"""
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX"
    )
    parser.add_argument(
        "--vfs",
        help="Путь к виртуальной файловой системе"
    )
    parser.add_argument(
        "--startup-script",
        help="Путь к стартовому скрипту"
    )
    parser.add_argument(
        "--config",
        help="Путь к конфигурационному JSON-файлу"
    )
    return parser.parse_args(argv)


def load_config(path):
    """Загрузить настройки из JSON. 2"""
    if not path:
        return {}

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Конфигурация должна быть объектом JSON")

    for key in ("vfs_path", "startup_script"):
        value = data.get(key)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Параметр {key} должен быть строкой")

    return data


def get_settings(args):
    """Объединить настройки с приоритетом JSON. 2"""
    config = load_config(args.config)

    settings = {
        "vfs_path": args.vfs,
        "startup_script": args.startup_script,
        "config_path": args.config
    }

    for key in ("vfs_path", "startup_script"):
        if key in config:
            settings[key] = config[key]

    return settings


def print_settings(settings):
    """Вывести текущие настройки. 2"""
    print("Настройки эмулятора:")
    print(f"VFS: {settings['vfs_path']}")
    print(f"Скрипт: {settings['startup_script']}")
    print(f"Конфигурация: {settings['config_path']}")


def load_vfs(path):
    """Загрузить VFS из директории. 3"""
    if not path:
        return None

    vfs = VirtualFileSystem(path)
    info = vfs.get_info()

    print("Виртуальная файловая система загружена")
    print(f"Файлов: {info['files']}")
    print(f"Директорий: {info['directories']}")
    return vfs


def run_startup_script(path, vfs=None):
    """Выполнить стартовый скрипт до ошибки. 2-3"""
    if not path:
        return True, True

    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        command = line.strip()
        if not command:
            continue

        print(f"{get_prompt()}{command}")
        continue_running, success = process_command(
            command, vfs
        )

        if not success:
            print("Ошибка выполнения стартового скрипта")
            return False, False

        if not continue_running:
            return True, False

    return True, True


def interactive_mode(vfs=None):
    """Запустить интерактивный режим. 2-3"""
    while True:
        try:
            line = input(get_prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not execute_command(line, vfs):
            break


def main(argv=None):
    """Запустить эмулятор с конфигурацией и VFS. 1-3"""
    args = parse_arguments(argv)

    try:
        settings = get_settings(args)
        print_settings(settings)

        vfs = load_vfs(settings["vfs_path"])
        success, continue_running = run_startup_script(
            settings["startup_script"], vfs
        )
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки или выполнения: {error}")
        return 1

    if not success:
        return 1

    if continue_running:
        interactive_mode(vfs)

    return 0


if __name__ == "__main__":
    sys.exit(main())
