"""Эмулятор командной оболочки UNIX."""

import argparse
import getpass
import json
import os
import re
import socket
import sys


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


def process_command(line):
    """Обработать команду и вернуть статусы. 2"""
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

    if command == "ls":
        print(f"ls: аргументы = {arguments}")
    elif command == "cd":
        print(f"cd: аргументы = {arguments}")
    else:
        print(f"{command}: команда не найдена")
        return True, False

    return True, True


def execute_command(line):
    """Выполнить команду в интерактивном режиме. 1-2"""
    continue_running, _ = process_command(line)
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


def run_startup_script(path):
    """Выполнить стартовый скрипт до первой ошибки. 2"""
    if not path:
        return True, True

    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        command = line.strip()
        if not command:
            continue

        print(f"{get_prompt()}{command}")
        continue_running, success = process_command(command)

        if not success:
            print("Ошибка выполнения стартового скрипта")
            return False, False

        if not continue_running:
            return True, False

    return True, True


def interactive_mode():
    """Запустить интерактивный режим. 2"""
    while True:
        try:
            line = input(get_prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not execute_command(line):
            break


def main(argv=None):
    """Запустить эмулятор с конфигурацией. 1-2"""
    args = parse_arguments(argv)

    try:
        settings = get_settings(args)
        print_settings(settings)

        success, continue_running = run_startup_script(
            settings["startup_script"]
        )
    except (OSError, ValueError) as error:
        print(f"Ошибка конфигурации или скрипта: {error}")
        return 1

    if not success:
        return 1

    if continue_running:
        interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
