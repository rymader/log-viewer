# log_reader.py
import subprocess
import sys
from typing import List
from abc import ABC, abstractmethod


# Command Interface
class Command(ABC):
    @abstractmethod
    def execute(self, args: List[str]) -> str:
        pass


# Journalctl Command Implementation
class JournalctlCommand(Command):
    def execute(self, args: List[str]) -> str:
        result = subprocess.run([
            'journalctl',
            '-S', '2024-07-18 14:30:00',
            '-U', '2024-07-22 21:53:00',
            '--no-pager',
            '-g', 'error'
        ], capture_output=True, text=True)
        return result.stdout


# CLI Class
class CLI:
    def __init__(self, command: Command):
        self.command = command

    def run(self, args: List[str]) -> None:
        output = self.command.execute(args)
        print(output)


if __name__ == "__main__":
    command = JournalctlCommand()
    cli = CLI(command)
    cli.run(sys.argv[1:])
