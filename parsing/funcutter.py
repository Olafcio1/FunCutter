from typing import TypedDict, Callable, Protocol
from .properties import Properties

__all__ = ("Version",  "Versions", "parseFuncutter",)

class Version(TypedDict):
    name: str
    properties: Properties
    extensions: list[str]
    abstract: bool

Versions = list[Version]

InternalProperties = list[tuple[str, str] | Callable[[], "InternalProperties"]]
InternalExtensions = list[str             | Callable[[], "InternalExtensions"]]

class InternalVersion(TypedDict):
    name: str
    source_name: str
    properties: InternalProperties
    extensions: InternalExtensions
    abstract: bool

class IVersion(Protocol):
    name: str
    abstract: bool

def process(obj, placeholders):
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = process(v, placeholders)
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = process(obj[k], placeholders)
    elif isinstance(obj, tuple):
        obj = tuple([process(v, placeholders) for v in obj])
    elif isinstance(obj, str):
        for k in placeholders:
            obj = obj.replace("{%s}" % k, placeholders[k])
    else:
        pass

    return obj

def provide(obj, placeholders, *, master: bool = True):
    if master and not placeholders:
        return

    if isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = provide(v, placeholders, master=False)
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = provide(obj[k], placeholders, master=False)
    elif isinstance(obj, tuple):
        obj = tuple([provide(v, placeholders, master=False) for v in obj])
    elif isinstance(obj, str):
        while "{}" in obj:
            if not placeholders:
                raise Exception("Not enough arguments")

            obj = obj.replace("{}", placeholders.pop(0), 1)
    elif isinstance(obj, Callable):
        obj = obj.rebind(lambda x: [provide(x, placeholders, master=False)])
    else:
        pass

    if placeholders and master:
        raise Exception("Too many arguments")

    return obj

def makePlaceholders(versionName):
    return {"@name": versionName}

def make(func, *args):
    def wrapper(*_args, **_kwargs):
        nonlocal func, args
        return func(*args, *_args, **_kwargs)

    wrapper.rebind = lambda consumer: make(func, *consumer(*args))
    wrapper.get = lambda: args

    return wrapper

def parseFuncutter(data: str) -> list[IVersion]:
    versionName:       str|None           = None
    versionProperties: InternalProperties = []
    versionExtensions: InternalExtensions = []
    versionAddons:     list[str]          = []
    versionAbstract:   bool               = False

    versions:     list[     InternalVersion] = []
    dictversions: dict[str, InternalVersion] = {}

    def addVersion() -> None:
        nonlocal versionName, \
                 versionProperties, \
                 versionAbstract, \
                 versionAddons, \
                 versions, dictversions

        assert versionName != None

        versions.append(ver := InternalVersion(
            name        = versionName,
            source_name = versionName,
            properties  = versionProperties.copy(),
            extensions  = versionExtensions.copy(),
            abstract    = versionAbstract
        ))

        dictversions[versionName] = ver

        for (addon, addonArgs) in versionAddons:
            addonName = addon + "-" + versionName

            addonProperties = versionProperties.copy()
            addonExtensions = versionExtensions.copy()

            addonExtensions.extend(dictversions[addon]['extensions'])
            addonExtensions.insert(0, addon)

            for ext in dictversions[addon]['extensions']:
                if isinstance(ext, Callable) and ext.get() == '{@name}':
                    break
            else:
                addonExtensions.insert(1, versionName)

            addonProperties.extend(dictversions[addon]['properties'])

            provide(addonProperties, addonArgs)
            provide(addonExtensions, addonArgs)

            versions.append(ver := InternalVersion(
                name        = addonName,
                source_name = versionName,
                properties  = addonProperties,
                extensions  = addonExtensions,
                abstract    = versionAbstract
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
            versionProperties.append(make(lambda name: dictversions[name]['properties'], name))
        elif line.startswith(";"):
            # Adds patches recursively and extends properties
            if versionName == None:
                raise Exception("Cannot put extension out of version scope")

            name = line[1:].strip()

            versionExtensions.append(make(lambda name: dictversions[name]['extensions'], name))
            versionExtensions.append(name)

            versionProperties.append(make(lambda name: dictversions[name]['properties'], name))
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

            name = line[2:]
            args = []

            while "(" in name:
                name, _, value = name.partition("(")
                value, _, rest = value.partition(")")

                name += rest
                args.append(value)

            name = name.strip()

            versionAddons.append((name, args))
        elif line.startswith("//"):
            # Comment
            pass
        elif not line.strip():
            pass
        elif versionName == None:
            raise Exception("Cannot put properties out of version scope")
        else:
            key, _, value = line.partition("=")
            versionProperties.append((key, value))

    if versionProperties:
        addVersion()

    return [ver if ver['abstract'] \
                else \
                     \
            Version(name       = ver['name'],                           \
                    properties = dict(convert(ver['properties'], ver)), \
                    extensions =      convert(ver['extensions'], ver),  \
                    abstract   = ver['abstract']                        ) for ver in versions]

def convert(obj, ver: InternalVersion):
    out = []
    placeholders = makePlaceholders(ver['source_name'])

    for el in obj:
        if isinstance(el, Callable):
            out.extend(convert(el.rebind(lambda name: [process(name, placeholders)])(), ver))
        else:
            out.append(process(el, placeholders))

    return out
