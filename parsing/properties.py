Properties = dict[str, str]

def parseProperties(data: str) -> Properties:
    lines = data.splitlines()
    out = {}

    index = 0
    for line in lines:
        if line.strip() != "" and not line.startswith("#"):
            key, _, value = line.partition("=")
            out[key] = value
        else:
            out["\x00" + str(index)] = line
            index += 1

    return out
