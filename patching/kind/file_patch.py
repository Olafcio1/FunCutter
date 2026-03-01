from ..types import *

__all__ = ("parsePatch", "writePatch",)

def parsePatch(patch: str) -> Patch:
    lines = patch.splitlines()

    section = []
    sections = []

    inSection = False

    for line in lines:
        if line == "{":
            if inSection:
                raise Exception("Tried to open a section in section scope")

            inSection = True
        elif line == "}":
            if not inSection:
                raise Exception("Tried to close a section in global scope")
            elif len(section) < 2:
                raise Exception("A section can have at minimum 2 lines")

            inSection = False

            sections.append(Section(
                search    = section[0],
                replace = "\n".join(section[1:])
            ))

            section.clear()
        else:
            if line.strip() == "":
                continue
            elif not line.startswith("    "):
                raise Exception("Expected a line starting with 4 spaces ('        ')")

            section.append(line[4:])

    return sections

def writePatch(patchPath: str, physicalPath: str) -> None:
    with open(patchPath, "r", encoding="utf-8") as f:
        patchRaw = f.read()

    patch = parsePatch(patchRaw)

    with open(physicalPath, "rb+") as f:
        encoding = "utf-8"
        physical = f.read().decode(encoding)

        f.seek(0)

        for section in patch:
            physical = physical.replace(section['search'], section['replace'], 1)

        encoded = physical.encode(encoding)

        f.write(encoded)
        f.truncate(len(encoded))
