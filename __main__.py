import subprocess
import sys
import os

from parsing.properties import *
from parsing.funcutter import *

from patching.writer import writePatches

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
        print("[Funcutter] [Main/ERROR] No 'build.funcutter' file could be found in your directory nor its ancestors")
        sys.exit(1)
    else:
        os.chdir("..")
