"""Виртуальная файловая система эмулятора UNIX."""

from pathlib import Path


class VirtualFileSystem:
    """Хранить виртуальные файлы в памяти. 3"""

    def __init__(self, source_path):
        """Создать VFS и загрузить директорию. 3"""
        self.source_path = Path(source_path).resolve()
        self.directories = set()
        self.files = {}
        self.load()

    def load(self):
        """Загрузить структуру VFS в память. 3"""
        source = self.source_path

        if not source.exists():
            raise FileNotFoundError(
                f"Директория VFS не найдена: {source}"
            )

        if not source.is_dir():
            raise ValueError(
                f"Источник VFS не является директорией: {source}"
            )

        self.directories = {Path(".")}
        self.files = {}

        for item in source.rglob("*"):
            relative_path = item.relative_to(source)

            if item.is_symlink():
                raise ValueError(
                    f"Символическая ссылка в VFS: {relative_path}"
                )

            if item.is_dir():
                self.directories.add(relative_path)
            elif item.is_file():
                self.files[relative_path] = item.read_bytes()
            else:
                raise ValueError(
                    f"Неподдерживаемый элемент VFS: {relative_path}"
                )

    def save(self, destination):
        """Сохранить состояние VFS на диск. 3"""
        target = Path(destination).resolve()
        source = self.source_path

        if target == source:
            raise ValueError("Нельзя перезаписать исходную VFS")

        if target.is_relative_to(source):
            raise ValueError("Нельзя сохранять VFS внутрь источника")

        if source.is_relative_to(target):
            raise ValueError("Нельзя сохранять VFS поверх источника")

        if target.exists():
            if not target.is_dir():
                raise ValueError("Путь сохранения не является папкой")
            if any(target.iterdir()):
                raise ValueError("Папка сохранения должна быть пустой")

        target.mkdir(parents=True, exist_ok=True)

        for directory in sorted(self.directories):
            (target / directory).mkdir(
                parents=True,
                exist_ok=True
            )

        for relative_path, content in self.files.items():
            file_path = target / relative_path
            file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            file_path.write_bytes(content)

    def get_info(self):
        """Получить сведения о загруженной VFS. 3"""
        return {
            "source": str(self.source_path),
            "directories": len(self.directories),
            "files": len(self.files)
        }
