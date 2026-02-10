# config.json

Copy **config.example.json** to **config.json** and set your paths. The script requires `multimc_instances_path` and `java_path`; the rest are optional.

| Key | Description |
|-----|-------------|
| **multimc_instances_path** | Where MultiMC stores instances (e.g. `C:\...\MultiMC\instances`). Required. |
| **java_path** | Path to `javaw.exe` used to launch Minecraft (e.g. `C:/Program Files/Java/jdk-22/bin/javaw.exe`). Required. |
| **world_source_dir** | Optional. If set, the script copies the world from this folder instead of searching existing instances. Use a path to a folder that contains world folders (e.g. a backup folder with your world name inside). Use `null` to search existing instances. |
| **world_to_copy** | Name of the world save to copy into the new instance (e.g. `"Test World"`). Set to `null` to disable copying a world. |

If **config.json** is missing, the script will tell you to copy config.example.json.
