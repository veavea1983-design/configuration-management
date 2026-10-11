"""Эмулятор командной оболочки UNIX. Этап 1"""

import getpass
import os
import re
import socket

def get_prompt():
  """Создать приглашение из данных текущей OC"""
   username = getpass.getuser()
   hostname = socket.gethostname()
   return f"{username}@{hostname}:~$ "

def expand_variables(text):
  """Раскрыть переменные окружения вида $NAME"""
  pattern = r"\$([A-Za-z_][A-Za-z0-9_]*)"

  def replace_variable(match):
      name = match.group(1)
  return os.environ.get(name, "")
        
  return re.sub(pattern, replace_variable, text)

def execute_command(line):
    """Разобрать команду и выполнить её"""
    expanded_line = expand_variables(line)
    parts = expanded_line.split()

    if not parts:
        return True

    command = parts[0]
    arguments = parts[1:]

    if command == "exit":
        if arguments:
            print("exit: неверные аргументы")
            return True
        return False

    if command == "ls":
        print(f"ls: аргументы = {arguments}")
    elif command == "cd":
        print(f"cd: аргументы = {arguments}")
    else:
        print(f"{command}: команда не найдена")

    return True
    
def main():
    """Запустить интерактивный режим эмулятора"""
    while True:
        try:
            line = input(get_prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not execute_command(line):
            break
if __name__ == "__main__":
    main()




        
