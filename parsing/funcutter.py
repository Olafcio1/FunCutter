from typing import TypedDict
from .properties import Properties

__all__ = ("Version",  "Versions", "parseFuncutter",)

class Version(TypedDict):
    name: str
    properties: Properties
    extensions: list[str]

Versions = list[Version]

def parseFuncutter(data: str) -> Versions:
    versionName:       str|None   = None
    versionProperties: Properties = {}
    versionExtensions: list[str]  = []

    versions: Versions = []
    dictversions: dict[str, Version] =  {}

    def addVersion() -> None:
        nonlocal versionName, \
                 versionProperties, \
                 versions, dictversions

        assert versionName != None

        versions.append(ver := Version(
            name       = versionName,
            properties = versionProperties.copy(),
            extensions = versionExtensions.copy()
        ))

        dictversions[versionName] = ver

        versionProperties.clear()
        versionExtensions.clear()
        versionName = None

    lines = data.splitlines()

    for line in lines:
        if line.startswith("#"):
            if versionName != None:
                addVersion()

            versionName = line[1:].strip()
        elif line.startswith(":"):
            if versionName == None:
                raise Exception("Cannot put extension out of version scope")

            name = line[1:].strip()

            versionExtensions.append(name)
            versionProperties.update(dictversions[name]['properties'])
        elif versionName == None:
            raise Exception("Cannot put properties out of version scope")
        elif line.strip() != "":
            key, _, value = line.partition("=")
            versionProperties[key] = value

    if versionProperties:
        addVersion()

    return versions
