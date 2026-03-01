import subprocess
import json
import sys
import os
from typing import TypedDict

###########
## TYPES ##
###########

class Version(TypedDict):
  name: str
  properties: "Properties"

Properties = dict[str, str]
Versions = list[Version]

class Section(TypedDict):
  search: str
  replace: str

Patch = list[Section]

#############
## PARSING ##
#############

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

  return out

def parseFuncutter(data: str) -> Versions:
  versionName:       str|None   = None
  versionProperties: Properties = {}

  versions: Versions = []

  def addVersion() -> None:
    nonlocal versionName, \
             versionProperties, \
             versions

    assert versionName != None

    versions.append(Version(
      name       = versionName,
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

#############
## READING ##
#############

def readFuncutter() -> Versions:
  with open("./build.funcutter", "r", encoding="utf-8") as f:
    funcutter = f.read()

  return parseFuncutter(funcutter)

def readProperties() -> tuple[Properties, str]:
  with open("./gradle.properties", "r", encoding="utf-8") as f:
    properties = f.read()

  return (
    parseProperties(properties),
    properties
  )

#############
## WRITING ##
#############

def writeProperties(properties: Properties) -> None:
  with open("./gradle.properties", "w", encoding="utf-8") as f:
    for key in properties:
      if key[0] == "\x00":
        f.write(properties[key])
        continue

      f.write(key + "=" + properties[key] + "\n")

#############
## PATCHES ##
#############

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
      runScriptPatch(pathN, physP + sub + "/" + dotSplit[0] + "." + dotSplit[2][3:])
    else:
      print("[Funcutter] [Patches] > Creating " + pathN)

      with open(pathN, "rb") as src:
        with open(physN, "wb") as dest:
          dest.write(src.read())

      mess.append(pathN)

###########
## PATCH ##
###########

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
        search  = section[0],
        replace = "\n".join(section[1:])
      ))

      section.clear()
    else:
      if line.strip() == "":
        continue
      elif not line.startswith("    "):
        raise Exception("Expected a line starting with 4 spaces ('    ')")

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

SCRIPTABLES = {
  "json": (json.loads, lambda text: json.dumps(text, indent=2))
}

def runScriptPatch(patchPath: str, physicalPath: str) -> None:
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

##############
## BUILDING ##
##############

def buildAll() -> None:
  ###=============###
  ### READ CONFIG ###
  ###=============###
  print("[Funcutter] > Configuring")

  funcutter = readFuncutter()
  properties, propRaw = readProperties()

  jarName = properties['archives_base_name']

  ###=======###
  ### STASH ###
  ###=======###
  print("[Funcutter] > Storing")

  subprocess.run(["git", "add", "."])
  subprocess.run(["git", "commit", "-m", "funcutter -- temporary", "--allow-empty"])

  ###===================###
  ### MAKE EACH VERSION ###
  ###===================###
  files = []

  for version in funcutter:
    print("[Funcutter] > Version " + version['name'])

    files.clear()

    vproperties = {**properties, **version['properties']}
    vproperties['archives_base_name'] = jarName + "+" + version['name']

    writeProperties(vproperties)
    writePatches(version['name'], files)

    subprocess.run([".\\gradlew.bat", "build", *sys.argv[1:]])
    subprocess.run(["git", "reset", "--hard"])

    for path in files:
      os.unlink(path)

  ###===================###
  ### RESTORE OLD STATE ###
  ###===================###
  print("[Funcutter] > Restoring old state")

  with open("./gradle.properties", "w", encoding="utf-8") as f:
    f.write(propRaw)

  subprocess.run(["git", "reset", "--mixed", "HEAD~1"])

  ###==========###
  ### FINISHED ###
  ###==========###
  print("[Funcutter] > Finished")

##########
## MAIN ##
##########

while True:
  if os.path.exists("./build.funcutter"):
    buildAll()
    break
  elif os.getcwd().count("/") <= 1:
    print("[Funcutter] [Error] No 'build.funcutter' file could be found in your directory nor its ancestors")
    sys.exit(1)
  else:
    os.chdir("..")
