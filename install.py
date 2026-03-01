import subprocess

profile = subprocess.run(["powershell", "-NoProfile", "-NoLogo", "-Command", "echo $profile"], stdout=subprocess.PIPE, text=True).stdout.rstrip()
path = "/".join(__file__.replace("\\", "/").split("/")[:-1])

with open(profile, "a", encoding="utf-8") as f:
  f.write("\nfunction funcutter() { python \"%s\" $args }" % path)
