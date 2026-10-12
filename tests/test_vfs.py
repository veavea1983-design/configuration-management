"""Автоматические тесты виртуальной файловой системы."""

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


class TestVFS(unittest.TestCase):
    """Проверить виртуальную файловую систему. 3"""

    def setUp(self):
        """Создать временную файловую систему. 3"""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()

        self.nested = self.source / "home" / "user" / "docs"
        self.nested.mkdir(parents=True)

        self.file = self.nested / "readme.txt"
        self.file.write_text("Hello VFS", encoding="utf-8")

    def test_load_files(self):
        """Проверить загрузку файлов. 3"""
        vfs = VirtualFileSystem(self.source)
        path = Path("home/user/docs/readme.txt")

        self.assertIn(path, vfs.files)
        self.assertEqual(vfs.files[path], b"Hello VFS")

    def test_nested_directories(self):
        """Проверить вложенность директорий. 3"""
        vfs = VirtualFileSystem(self.source)

        self.assertIn(Path("home"), vfs.directories)
        self.assertIn(Path("home/user"), vfs.directories)
        self.assertIn(
            Path("home/user/docs"),
            vfs.directories
        )

    def test_binary_content(self):
        """Проверить загрузку двоичных данных. 3"""
        binary = bytes([0, 1, 127, 255])
        (self.source / "binary.bin").write_bytes(binary)

        vfs = VirtualFileSystem(self.source)

        self.assertEqual(
            vfs.files[Path("binary.bin")],
            binary
        )

    def test_save(self):
        """Проверить сохранение VFS. 3"""
        vfs = VirtualFileSystem(self.source)
        destination = self.root / "saved"

        vfs.save(destination)

        saved_file = destination / "home/user/docs/readme.txt"
        self.assertTrue(saved_file.exists())
        self.assertEqual(saved_file.read_bytes(), b"Hello VFS")

    def test_source_unchanged(self):
        """Проверить неизменность источника. 3"""
        vfs = VirtualFileSystem(self.source)
        original = self.file.read_bytes()

        vfs.save(self.root / "saved")

        self.assertEqual(self.file.read_bytes(), original)

    def test_missing_source(self):
        """Проверить отсутствие источника. 3"""
        missing = self.root / "missing"

        with self.assertRaises(FileNotFoundError):
            VirtualFileSystem(missing)

    def test_save_into_source(self):
        """Проверить защиту исходной VFS. 3"""
        vfs = VirtualFileSystem(self.source)

        with self.assertRaises(ValueError):
            vfs.save(self.source / "saved")

    def test_save_command(self):
        """Проверить команду vfs-save. 3"""
        vfs = VirtualFileSystem(self.source)
        destination = self.root / "saved"
        command = f"vfs-save {destination}"

        with contextlib.redirect_stdout(io.StringIO()):
            result = process_command(command, vfs)

        self.assertEqual(result, (True, True))
        self.assertTrue(
            (destination / "home/user/docs/readme.txt").exists()
        )

    def test_script_error(self):
        """Проверить остановку скрипта при ошибке. 3"""
        vfs = VirtualFileSystem(self.source)
        script = self.root / "startup.txt"

        script.write_text(
            "ls\nvfs-save\ncd after_error\n",
            encoding="utf-8"
        )

        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = run_startup_script(script, vfs)

        self.assertEqual(result, (False, False))
        self.assertNotIn(
            "cd: аргументы",
            output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
