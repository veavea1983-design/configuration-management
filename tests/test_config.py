"""Тесты конфигурации эмулятора."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src")
)

from main import (
    get_settings,
    load_config,
    parse_arguments,
    run_startup_script
)


class TestConfig(unittest.TestCase):
    """Проверить конфигурацию эмулятора. 2"""

    def test_cli_arguments(self):
        """Проверить параметры командной строки. 2"""
        args = parse_arguments([
            "--vfs", "disk",
            "--startup-script", "start.txt"
        ])
        self.assertEqual(args.vfs, "disk")
        self.assertEqual(args.startup_script, "start.txt")

    def test_json_config(self):
        """Проверить чтение JSON. 2"""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump({"vfs_path": "disk"}, file)

            config = load_config(path)
            self.assertEqual(config["vfs_path"], "disk")

    def test_config_priority(self):
        """Проверить приоритет JSON. 2"""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump({"vfs_path": "json_disk"}, file)

            args = parse_arguments([
                "--vfs", "cli_disk",
                "--config", path
            ])
            settings = get_settings(args)
            self.assertEqual(settings["vfs_path"], "json_disk")

    def test_invalid_json(self):
        """Проверить ошибку формата JSON. 2"""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as file:
                file.write("{invalid}")

            with self.assertRaises(ValueError):
                load_config(path)

    def test_script_success(self):
        """Проверить успешный стартовый скрипт. 2"""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "start.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("ls\ncd folder\nexit\n")

            with contextlib.redirect_stdout(io.StringIO()):
                result = run_startup_script(path)

            self.assertEqual(result, (True, False))

    def test_script_error(self):
        """Проверить остановку при ошибке. 2"""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "start.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("ls\nunknown\ncd folder\n")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = run_startup_script(path)

            self.assertEqual(result, (False, False))
            self.assertNotIn(
                "cd: аргументы",
                output.getvalue()
            )


if __name__ == "__main__":
    unittest.main()
