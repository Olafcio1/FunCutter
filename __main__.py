import subprocess
import signal
import msvcrt
import sys
import os

from input import *

from modloaders.fabric import Fabric
from modloaders.legacy_fabric import LegacyFabric

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
                f.write(properties[key] + "\n")
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
    only_errors = {
      "stdout": subprocess.PIPE,
      "stderr": subprocess.STDOUT
    }

    subprocess.run(["git", "add", "."], **only_errors)
    subprocess.run(["git", "commit", "-m", "funcutter -- temporary", "--allow-empty"], **only_errors)

    ###===================###
    ### MAKE EACH VERSION ###
    ###===================###
    pendingReset = False
    files = []

    try:
      command = [".\\gradlew.bat"]

      for _ in range(1):
        if len(sys.argv) > 1:
          if sys.argv[1] == "!wait":
            def runner():
              print(old := "[Funcutter] Waiting. To continue, press any key.", end="")
              sys.stdout.flush()
              if msvcrt.getch() == b'\x03':
                print()
                raise KeyboardInterrupt()

              print("\r[Funcutter] Continuing." + " "*(len(old) - 23))

            break
          else:
            args = sys.argv[1:]

            if not args[0].startswith("-"):
              command.append(args.pop(0))
            else: command.append('build')

            command.extend(args)
        else:
          command.append("build")

        runner = lambda: subprocess.run(command)

      for version in funcutter:
          print("[Funcutter] > Version " + version['name'])

          files.clear()
          pendingReset = True

          vproperties = {**properties, **version['properties']}
          vproperties['archives_base_name'] = jarName + "+" + version['name']

          writeProperties(vproperties)
          writePatches(version['name'], files)

          runner()
          subprocess.run(["git", "reset", "--hard"])
          pendingReset = False

          for path in files:
              os.unlink(path)
    except KeyboardInterrupt:
        print("[Funcutter] > Detected keyboard interrupt, cancelling")
        signal.signal(signal.SIGINT, lambda *_: None)

        if pendingReset:
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

#######################
## 'INIT' SUBCOMMAND ##
#######################

if len(sys.argv) > 1 and sys.argv[1] == "init":
  if os.path.isfile("build.funcutter"):
    print("ERROR: There's already a build.funcutter file in your directory")
    sys.exit(1)

  def logo():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)

    print("|----------------------------|")
    print("| FunCutter :: Project Setup |")
    print("|----------------------------|")
    print()

  try:
    logo()
    modloader = listInput("Please select your modloader >", {
      "a": ("Fabric",        Fabric),
      "b": ("Legacy Fabric", LegacyFabric)
    })

    logo()

    print("Please input your Minecraft versions >")
    print("Leave empty to mark ready")
    print()

    mcvers = []
    while True:
      mcver = input("  ) ")
      if mcver == '':
        break

      mcvers.append(mcver)
  except KeyboardInterrupt:
    print("\nCancelling.")
    sys.exit(2)
  else:
    signal.signal(signal.SIGINT, lambda *_: None)

  funcutter = ""

  for mcver in mcvers:
    funcutter += "# %s\n" % mcver
    funcutter += modloader.properties(mcver)
    funcutter += "\n"

  with open("build.funcutter", "w", encoding="utf-8") as f:
    f.write(funcutter[:-1])

  sys.exit(0)

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
