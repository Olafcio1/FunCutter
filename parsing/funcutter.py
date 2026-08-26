from typing import TypedDict
from .properties import Properties

__all__ = ("Version",  "Versions", "parseFuncutter",)

class Version(TypedDict):
    name: str
    properties: Properties
    extensions: list[str]
    abstract: bool

Versions = list[Version]

def parseFuncutter(data: str) -> Versions:
    versionName:       str|None   = None
    versionProperties: Properties = {}
    versionExtensions: list[str]  = []
    versionAddons:     list[str]  = []
    versionAbstract:   bool       = False

    versions: Versions = []
    dictversions: dict[str, Version] =  {}

    def addVersion() -> None:
        nonlocal versionName, \
                 versionProperties, \
                 versionAbstract, \
                 versionAddons, \
                 versions, dictversions

        assert versionName != None

        versions.append(ver := Version(
            name       = versionName,
            properties = versionProperties.copy(),
            extensions = versionExtensions.copy(),
            abstract   = versionAbstract
        ))

        dictversions[versionName] = ver

        for addon in versionAddons:
            addonName = addon + "-" + versionName

            addonProperties = dictversions[addon]['properties'].copy()
            addonExtensions = dictversions[addon]['extensions'].copy()

            addonExtensions.extend(versionProperties)
            addonExtensions.insert(0, versionName)
            addonProperties.update(versionProperties)

            versions.append(ver := Version(
                name       = addonName,
                properties = addonProperties,
                extensions = addonExtensions,
                abstract   = versionAbstract
            ))

            dictversions[addonName] = ver

        versionProperties.clear()
        versionExtensions.clear()
        versionAddons.clear()
        versionName = None
        versionAbstract = False

    lines = data.splitlines()

    for line in lines:
        if line.startswith("#"):
            # Defines version scope
            if versionName != None:
                addVersion()

            versionName = line[1:].strip()
        elif line.startswith("$"):
            # Defines version base scope
            if versionName != None:
                addVersion()

            versionName = line[1:].strip()
            versionAbstract = True
        elif line.startswith(":"):
            # Adds patches and extends properties
            if versionName == None:
                raise Exception("Cannot put extension out of version scope")

            name = line[1:].strip()

            versionExtensions.append(name)
            versionProperties.update(dictversions[name]['properties'])
        elif line.startswith(";"):
            # Adds patches recursively and extends properties
            if versionName == None:
                raise Exception("Cannot put extension out of version scope")

            name = line[1:].strip()

            versionExtensions.extend(dictversions[name]['extensions'])
            versionExtensions.append(name)
            versionProperties.update(dictversions[name]['properties'])
        elif line.startswith("!"):
            # Only adds patches
            if versionName == None:
                raise Exception("Cannot put extension out of version scope")

            name = line[1:].strip()

            versionExtensions.append(name)
        elif line.startswith("<-"):
            # Addon
            if versionName == None:
                raise Exception("Cannot put addon out of version scope")

            name = line[2:].strip()

            versionAddons.append(name)
        elif line.startswith("//"):
            # Comment
            pass
        elif versionName == None:
            raise Exception("Cannot put properties out of version scope")
        elif line.strip() != "":
            key, _, value = line.partition("=")
            versionProperties[key] = value

    if versionProperties:
        addVersion()

    return versions
