class LegacyFabric:
  @staticmethod
  def properties(minecraft_version: str) -> str:
    out = ""

    out += "minecraft_version=%s\n" % minecraft_version
    out += "yarn_build=%d\n" % LegacyFabric.getYarn(minecraft_version)
    out += "loader_version=%s\n" % LegacyFabric.getLoader(minecraft_version)
    out += "fabric_version=%s\n" % LegacyFabric.getAPI(minecraft_version)

    return out

  @staticmethod
  def getYarn(minecraft_version: str) -> int:
    versions = requests.get("https://meta.legacyfabric.net/v2/versions/yarn/" + minecraft_version).json()
    return versions[0]['build']

  @staticmethod
  def getLoader(minecraft_version: str) -> int:
    versions = requests.get("https://meta.legacyfabric.net/v1/versions/loader/" + minecraft_version).json()
    return versions[0]['loader']['version']

  @staticmethod
  def getAPI(minecraft_version: str) -> int:
    versions = requests.get("https://api.modrinth.com/v2/project/legacy-fabric-api/version").json()

    for obj in versions:
      if minecraft_version in obj['game_versions']:
        return obj['version_number'] + "+" + minecraft_version

    raise Exception("No Legacy Fabric API available")
