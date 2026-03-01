import requests

from typing import ClassVar
from defusedxml.ElementTree import fromstring as parseXML

class Fabric:
  fabric_loader: ClassVar[str | None] = None

  @staticmethod
  def properties(minecraft_version: str) -> str:
    out = ""

    out += "minecraft_version=%s\n" % minecraft_version
    out += "yarn_mappings=%s\n" % Fabric.getYarn(minecraft_version)
    out += "loader_version=%s\n" % Fabric.getLoader()
    out += "fabric_version=%s\n" % Fabric.getAPI(minecraft_version)

    return out

  @staticmethod
  def getLoader() -> str:
    if Fabric.fabric_loader == None:
      Fabric.fabric_loader = requests.get("https://meta.fabricmc.net/v2/versions/loader").json()[0].version

    return Fabric.fabric_loader

  @staticmethod
  def getYarn(minecraft_version: str) -> str:
    data = requests.get("https://meta.fabricmc.net/v2/versions/yarn").json()
    for obj in data:
      if obj.gameVersion == minecraft_version:
        return obj['version']

    raise Exception("No Fabric yarn available")

  @staticmethod
  def getAPI(minecraft_version: str) -> str:
    data = requests.get("https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/maven-metadata.xml").content

    xml = parseXML(data)
    versions = xml[2][2] # versioning > versions

    for node in versions:
      version = node.text
      if version.endswith((
          "+" + minecraft_version,
          "-" + minecraft_version
      )):
        return version

    raise Exception("No Fabric API available")
