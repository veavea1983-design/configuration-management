"""Автоматические тесты основных команд UNIX."""

import contextlib
import io
import os
import platform
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src")
)

from main import process_command, run_startup_script
from vfs import VirtualFileSystem


class TestCommands(unittest.TestCase):
    """Проверить основные команды эмулятора. 4"""

    def setUp(self):
        """Создать временную VFS для тестирования. 4"""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.source = Path(self.temp.name) / "vfs"
        self.source.mkdir()

        directory = self.source / "home" / "user"
        directory.mkdir(parents=True)

        (self.source / "root.txt").write_text(
            "root file", encoding="utf-8"
        )
        (directory / "notes.txt").write_text(
            "user notes", encoding="utf-8"
        )

        self.vfs = VirtualFileSystem(self.source)

    def run_command(self, command):
        """Выполнить команду и получить вывод. 4"""
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = process_command(command, self.vfs)

        return result, output.getvalue()

    def test_ls_root(self):
        """Проверить просмотр корневой директории. 4"""
        result, output = self.run_command("ls")
        self.assertEqual(result, (True, True))
        self.assertIn("home/", output)
        self.assertIn("root.txt", output)

    def test_ls_argument(self):
        """Проверить ls с указанным путём. 4"""
        result, output = self.run_command("ls /home/user")
        self.assertEqual(result, (True, True))
        self.assertIn("notes.txt", output)

    def test_cd(self):
        """Проверить переход в каталог. 4"""
        result, _ = self.run_command("cd home")
        self.assertEqual(result, (True, True))
        self.assertEqual(self.vfs.get_current_path(), "/home")

    def test_cd_parent(self):
        """Проверить переход к родительскому каталогу. 4"""
        self.run_command("cd home/user")
        self.run_command("cd ..")
        self.assertEqual(self.vfs.get_current_path(), "/home")

    def test_cd_absolute(self):
        """Проверить абсолютный виртуальный путь. 4"""
        self.run_command("cd /home/user")
        self.assertEqual(
            self.vfs.get_current_path(), "/home/user"
        )

    def test_cd_root(self):
        """Проверить возвращение в корень. 4"""
        self.run_command("cd home/user")
        self.run_command("cd /")
        self.assertEqual(self.vfs.get_current_path(), "/")

    def test_missing_directory(self):
        """Проверить отсутствующий каталог. 4"""
        result, output = self.run_command("cd unknown")
        self.assertEqual(result, (True, False))
        self.assertIn("Каталог не найден", output)

    def test_cd_file(self):
        """Проверить запрет перехода в файл. 4"""
        result, output = self.run_command("cd root.txt")
        self.assertEqual(result, (True, False))
        self.assertIn("Не каталог", output)

    def test_tree(self):
        """Проверить вывод дерева каталогов. 4"""
        result, output = self.run_command("tree")
        self.assertEqual(result, (True, True))
        self.assertIn("home/", output)
        self.assertIn("notes.txt", output)
        self.assertIn("root.txt", output)

    def test_uname(self):
        """Проверить определение операционной системы. 4"""
        result, output = self.run_command("uname")
        self.assertEqual(result, (True, True))
        self.assertIn(platform.system(), output)

    def test_clear(self):
        """Проверить команду очистки терминала. 4"""
        result, output = self.run_command("clear")
        self.assertEqual(result, (True, True))
        self.assertIn("\033[2J\033[H", output)

    def test_script_stops_on_cd_error(self):
        """Проверить остановку при ошибке cd. 4"""
        script = Path(self.temp.name) / "commands.txt"
        script.write_text(
            "ls\ncd unknown\ntree\n",
            encoding="utf-8"
        )

        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = run_startup_script(script, self.vfs)

        self.assertEqual(result, (False, False))
        self.assertNotIn("└── ", output.getvalue())


if __name__ == "__main__":
    unittest.main()
