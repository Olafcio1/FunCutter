import msvcrt
from typing import TypeVar

__all__ = ("listInput",)

T = TypeVar('T')
def listInput(prompt: str, options: dict[str, tuple[str, T]]) -> T:
  print(prompt)
  for opt in options:
    print("  %s) %s" % (opt, options[opt][0]))

  while True:
    key = msvcrt.getch()
    if key == b'\x03':
      raise KeyboardInterrupt()
    else:
      dec = key.decode()
      if dec in options:
        return options[dec][1]
