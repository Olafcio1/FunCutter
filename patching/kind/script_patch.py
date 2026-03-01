import json

__all__ = ("scriptPatch",)
SCRIPTABLES = {
    "json": (json.loads, lambda text: json.dumps(text, indent=2))
}

def scriptPatch(patchPath: str, physicalPath: str) -> None:
    global SCRIPTABLES
    if (ext := physicalPath.rpartition(".")[2]) not in SCRIPTABLES:
        raise Exception("Expected a scriptable extension (.%s is not supported)" % ext)

    with open(patchPath, "r", encoding="utf-8") as f:
        userscript = f.read()

    load, dump = SCRIPTABLES[ext]
    compiled = compile(userscript, patchPath, "exec")

    with open(physicalPath, "rb+") as f:
        encoding = "utf-8"
        physical = f.read().decode(encoding)

        f.seek(0)

        parsed = load(physical)

        exec(compiled, {
            "this": parsed
        }, {})

        dumped = dump(parsed)
        encoded = dumped.encode(encoding)

        f.write(encoded)
        f.truncate(len(encoded))
