from typing import TypedDict
from .properties import Properties

__all__ = ("Version",  "Versions", "parseFuncutter",)

class Version(TypedDict):
    name: str
    properties: Properties

Versions = list[Version]

def parseFuncutter(data: str) -> Versions:
    versionName:             str|None     = None
    versionProperties: Properties = {}

    versions: Versions = []

    def addVersion() -> None:
        nonlocal versionName, \
                 versionProperties, \
                 versions

        assert versionName != None

        versions.append(Version(
            name             = versionName,
            properties = versionProperties
        ))

        versionProperties = {}
        versionName = None

    lines = data.splitlines()

    for line in lines:
        if line.startswith("#"):
            if versionName != None:
                addVersion()

            versionName = line[1:].strip()
        elif versionName == None:
            raise Exception("Cannot put properties out of version scope")
        elif line.strip() != "":
            key, _, value = line.partition("=")
            versionProperties[key] = value

    if versionProperties:
        addVersion()

    return versions
