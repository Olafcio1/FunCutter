import os
import subprocess

from .kind.file_patch import writePatch
from .kind.script_patch import scriptPatch

__all__ = ("writePatches",)

def writePatches(versionName: str, recovery: list, *, sub: str = "", recoveryLate: list|None = None) -> None:
    if recoveryLate is None:
        recoveryLate = []
        newLate = True
    else:
        newLate = False

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
            if os.path.exists(physN):
                raise Exception("Incorrect filetype")
            else:
                os.mkdir(physN)
                print("[Funcutter] [Patches] > Creating directory " + pathN)
                recoveryLate.append(lambda: os.rmdir(physN))

        if os.path.isdir(pathN):
            writePatches(versionName, recovery, sub=subN, recoveryLate=recoveryLate)
        elif (dotSplit := fn.rpartition("."))[2].startswith("fp-"):
            print("[Funcutter] [Patches] > Applying " + pathN)
            writePatch(pathN, physP + sub + "/" + dotSplit[0] + "." + dotSplit[2][3:])
        elif (dotSplit := fn.rpartition("."))[2].startswith("fs-"):
            print("[Funcutter] [Patches] > Running " + pathN)
            scriptPatch(pathN, physP + sub + "/" + dotSplit[0] + "." + dotSplit[2][3:])
        elif (dotSplit := fn.rpartition("."))[2].startswith("fd-"):
            print("[Funcutter] [Patches] > Deleting " + pathN)

            realP = physP + sub + "/" + dotSplit[0] + "." + dotSplit[2][3:]

            os.unlink(realP)
            recovery.append(runner(["git", "restore", realP]))
        else:
            print("[Funcutter] [Patches] > Creating " + pathN)

            with open(pathN, "rb") as src:
                with open(physN, "wb") as dest:
                    dest.write(src.read())

            recovery.append(deleter(physN))

    if newLate:
        recovery.extend(recoveryLate)

def runner(args: list[str]):
    return lambda: subprocess.run(args)

def deleter(path: str):
    return lambda: os.unlink(path) if os.path.exists(path) else None
