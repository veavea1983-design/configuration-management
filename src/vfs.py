"""Виртуальная файловая система эмулятора UNIX."""

from pathlib import Path


class VirtualFileSystem:
    """Хранить виртуальные файлы в памяти. 3-4"""

    def __init__(self, source_path):
        """Создать VFS и текущий каталог. 3-4"""
        self.source_path = Path(source_path).resolve()
        self.directories = set()
        self.files = {}
        self.current_directory = Path(".")
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

    def resolve_path(self, path):
        """Преобразовать виртуальный путь в относительный. 4"""
        raw_path = str(path).replace("\\", "/")

        if raw_path.startswith("/"):
            parts = []
        elif self.current_directory == Path("."):
            parts = []
        else:
            parts = list(self.current_directory.parts)

        for part in raw_path.split("/"):
            if part in ("", "."):
                continue

            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)

        return Path(*parts) if parts else Path(".")

    def require_directory(self, path):
        """Проверить существование каталога VFS. 4"""
        target = self.resolve_path(path)

        if target in self.files:
            raise NotADirectoryError(f"Не каталог: {path}")

        if target not in self.directories:
            raise FileNotFoundError(f"Каталог не найден: {path}")

        return target

    def change_directory(self, path):
        """Изменить текущую виртуальную директорию. 4"""
        target = self.require_directory(path)
        self.current_directory = target

    def list_directory(self, path="."):
        """Получить содержимое виртуального каталога. 4"""
        target = self.require_directory(path)
        names = []

        for directory in self.directories:
            if directory != target and directory.parent == target:
                names.append(directory.name + "/")

        for file_path in self.files:
            if file_path.parent == target:
                names.append(file_path.name)

        return sorted(names)

    def get_current_path(self):
        """Получить абсолютный виртуальный путь. 4"""
        if self.current_directory == Path("."):
            return "/"

        return "/" + self.current_directory.as_posix()

    def build_tree_lines(self, directory, prefix=""):
        """Сформировать строки дерева каталогов. 4"""
        entries = self.list_directory(
            "/" + directory.as_posix()
            if directory != Path(".") else "/"
        )
        lines = []

        for index, name in enumerate(entries):
            last = index == len(entries) - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + name)

            if name.endswith("/"):
                child = directory / name.rstrip("/")
                extension = "    " if last else "│   "
                lines.extend(
                    self.build_tree_lines(child, prefix + extension)
                )

        return lines

    def render_tree(self, path="."):
        """Построить дерево виртуальных файлов. 4"""
        target = self.require_directory(path)

        if target == Path("."):
            title = "/"
        else:
            title = target.name + "/"

        lines = [title]
        lines.extend(self.build_tree_lines(target))
        return "\n".join(lines)

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
