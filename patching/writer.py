import os

from .kind.file_patch import writePatch
from .kind.script_patch import scriptPatch

__all__ = ("writePatches",)

def writePatches(versionName: str, mess: list[str], *, sub: str = "") -> None:
    try:
        path = "versions/" + versionName + sub
        files = os.listdir(path)
    except FileNotFoundError as e:
        if sub != "":
            raise e

        return

    for fn in files:
        fnSlashed = "/" + fn

        subN = sub + fnSlashed
        pathN = path + fnSlashed

        physP = "src/main"
        physN = physP + subN

        if os.path.isdir(pathN) != os.path.isdir(physN):
            raise Exception("Incorrect filetype")
        elif os.path.isdir(pathN):
            writePatches(versionName, mess, sub=subN)
        elif (dotSplit := fn.rpartition("."))[2].startswith("fp-"):
            print("[Funcutter] [Patches] > Applying " + pathN)
            writePatch(pathN, physP + sub + "/" + dotSplit[0] + "." + dotSplit[2][3:])
        elif (dotSplit := fn.rpartition("."))[2].startswith("fs-"):
            print("[Funcutter] [Patches] > Running " + pathN)
            scriptPatch(pathN, physP + sub + "/" + dotSplit[0] + "." + dotSplit[2][3:])
        else:
            print("[Funcutter] [Patches] > Creating " + pathN)

            with open(pathN, "rb") as src:
                with open(physN, "wb") as dest:
                    dest.write(src.read())

            mess.append(physN)
