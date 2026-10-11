"""Автоматические тесты эмулятора UNIX"""

import contextlib
import io
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src")
)

from main import execute_command, expand_variables


class TestShell(unittest.TestCase):
    """Проверка функций эмулятора"""

    def run_command(self, command):
        """Выполнить команду и получить её вывод"""
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = execute_command(command)

        return result, output.getvalue()

    def test_ls(self):
        """Проверить команду ls"""
        result, output = self.run_command("ls folder")
        self.assertTrue(result)
        self.assertIn("folder", output)

    def test_cd(self):
        """Проверить команду cd"""
        result, output = self.run_command("cd documents")
        self.assertTrue(result)
        self.assertIn("documents", output)

    def test_unknown_command(self):
        """Проверить неизвестную команду"""
        result, output = self.run_command("hello")
        self.assertTrue(result)
        self.assertIn("команда не найдена", output)

    def test_environment_variable(self):
        """Проверить раскрытие переменной окружения"""
        with patch.dict(os.environ, {"TEST_VAR": "hello"}):
            result = expand_variables("$TEST_VAR")
        self.assertEqual(result, "hello")

    def test_exit(self):
        """Проверить завершение программы"""
        result, output = self.run_command("exit")
        self.assertFalse(result)
        self.assertEqual(output, "")

    def test_invalid_exit(self):
        """Проверить неверные аргументы exit"""
        result, output = self.run_command("exit wrong")
        self.assertTrue(result)
        self.assertIn("неверные аргументы", output)

    def test_empty_command(self):
        """Проверить пустую строку"""
        result, output = self.run_command("")
        self.assertTrue(result)
        self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()

