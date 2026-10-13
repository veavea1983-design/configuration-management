"""Тесты дополнительных команд touch и rm."""

import contextlib
import io
import os
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


class TestExtraCommands(unittest.TestCase):
    """Проверить создание и удаление файлов VFS. 5"""

    def setUp(self):
        """Подготовить временную файловую систему. 5"""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()

        (self.source / "docs").mkdir()
        (self.source / "original.txt").write_text(
            "Original data", encoding="utf-8"
        )
        self.vfs = VirtualFileSystem(self.source)

    def run_command(self, command):
        """Выполнить команду и получить результат. 5"""
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = process_command(command, self.vfs)

        return result, output.getvalue()

    def test_touch_creates_file(self):
        """Проверить создание пустого файла. 5"""
        result, _ = self.run_command("touch new.txt")

        self.assertEqual(result, (True, True))
        self.assertEqual(
            self.vfs.files[Path("new.txt")], b""
        )

    def test_touch_existing_file(self):
        """Проверить сохранение содержимого файла. 5"""
        result, _ = self.run_command("touch original.txt")

        self.assertEqual(result, (True, True))
        self.assertEqual(
            self.vfs.files[Path("original.txt")],
            b"Original data"
        )

    def test_touch_nested_file(self):
        """Проверить создание файла в подкаталоге. 5"""
        result, _ = self.run_command("touch docs/note.txt")

        self.assertEqual(result, (True, True))
        self.assertIn(
            Path("docs/note.txt"), self.vfs.files
        )

    def test_touch_missing_parent(self):
        """Проверить отсутствие родительской папки. 5"""
        result, output = self.run_command(
            "touch unknown/note.txt"
        )

        self.assertEqual(result, (True, False))
        self.assertIn("не найден", output)

    def test_touch_directory(self):
        """Проверить запрет создания поверх каталога. 5"""
        result, output = self.run_command("touch docs")

        self.assertEqual(result, (True, False))
        self.assertIn("Это каталог", output)

    def test_rm_existing_file(self):
        """Проверить удаление существующего файла. 5"""
        result, _ = self.run_command("rm original.txt")

        self.assertEqual(result, (True, True))
        self.assertNotIn(
            Path("original.txt"), self.vfs.files
        )

    def test_rm_missing_file(self):
        """Проверить ошибку удаления файла. 5"""
        result, output = self.run_command("rm missing.txt")

        self.assertEqual(result, (True, False))
        self.assertIn("Файл не найден", output)

    def test_rm_directory(self):
        """Проверить запрет удаления каталога. 5"""
        result, output = self.run_command("rm docs")

        self.assertEqual(result, (True, False))
        self.assertIn("Это каталог", output)

    def test_missing_arguments(self):
        """Проверить отсутствие аргументов команд. 5"""
        for command in ("touch", "rm"):
            with self.subTest(command=command):
                result, _ = self.run_command(command)
                self.assertEqual(result, (True, False))

    def test_source_unchanged(self):
        """Проверить сохранность исходных файлов. 5"""
        self.run_command("rm original.txt")
        self.run_command("touch new.txt")

        original = self.source / "original.txt"
        self.assertTrue(original.exists())
        self.assertEqual(
            original.read_text(encoding="utf-8"),
            "Original data"
        )
        self.assertFalse((self.source / "new.txt").exists())

    def test_save_modified_vfs(self):
        """Проверить сохранение изменённой VFS. 5"""
        self.run_command("rm original.txt")
        self.run_command("touch docs/new.txt")
        destination = self.root / "saved"

        self.vfs.save(destination)

        self.assertFalse(
            (destination / "original.txt").exists()
        )
        self.assertTrue(
            (destination / "docs/new.txt").exists()
        )

    def test_script_stops_on_rm_error(self):
        """Проверить остановку скрипта при ошибке rm. 5"""
        script = self.root / "startup.txt"
        script.write_text(
            "touch new.txt\nrm missing.txt\ntree\n",
            encoding="utf-8"
        )

        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = run_startup_script(script, self.vfs)

        self.assertEqual(result, (False, False))
        self.assertNotIn("└── ", output.getvalue())


if __name__ == "__main__":
    unittest.main()
