from ..types import *

__all__ = ("parsePatch", "writePatch",)

def parsePatch(patch: str, ext: str) -> Patch:
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
                search  = section[0],
                replace = "\n".join(section[1:])
            ))

            section.clear()
        elif line.startswith("import "):
            if ext != ".java":
                raise Exception("Import statements are only allowed in .fp-java files")
            elif inSection:
                raise Exception("Import statements are not allowed in sections")

            if line.endswith(";"):
                print("[FunCutter] [Patches/WARN] Imports don't have to end with a ';'")

            sections.append(Section(
                search  = "import ",
                replace = "import %s;\nimport " % line[7:].removesuffix(";")
            ))
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

    patch = parsePatch(patchRaw, "." + physicalPath.rpartition(".")[2])

    with open(physicalPath, "rb+") as f:
        encoding = "utf-8"
        physical = f.read().decode(encoding)

        f.seek(0)

        for section in patch:
            physical = physical.replace(section['search'], section['replace'], 1)

        encoded = physical.encode(encoding)

        f.write(encoded)
        f.truncate(len(encoded))
