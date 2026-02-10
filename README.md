# MultiMC Instance Creator

Creates Minecraft instances for **MultiMC** with **Fabric** loader and common mods (Fabric API, Mod Menu, Cloth Config). Optionally copies a world save and your Minecraft settings so you can test mods in a clean instance that matches your preferences.

## Setup

### Prerequisites

- Python 3.7+
- [MultiMC](https://multimc.org/) installed
- Java (for `javaw.exe` path)

### Config

User-specific paths and options live in **config.json**. Do not commit it (it is in .gitignore).

1. Copy the example and edit with your paths:
   ```cmd
   copy config.example.json config.json
   ```
2. Edit **config.json** and set:
   - **multimc_instances_path** – Where MultiMC stores instances (e.g. `C:\...\MultiMC\instances`). Required.
   - **java_path** – Path to `javaw.exe` used to launch Minecraft (e.g. `C:/Program Files/Java/jdk-22/bin/javaw.exe`). Required.
   - **world_to_copy** – Name of the world save to copy into new instances (e.g. `"Test World"`). Set to `null` to disable. Optional.
   - **world_source_dir** – Optional. If set, the script copies the world from this folder instead of searching existing instances. Use `null` to search instances or use **templates/worlds/**.

See **config.README.md** for the full config reference.

## Usage

### Create an instance

From this folder:

```cmd
py setup_instance.py 1.21.11
```

This creates an instance named `1.21.11` in your MultiMC instances folder, with Fabric loader and Fabric API, Mod Menu, and Cloth Config. It also copies Minecraft settings from **templates/minecraft/** and, if **world_to_copy** is set in config, copies that world into the instance.

### Include your mod jar

To drop your mod into the new instance (e.g. for testing before release):

```cmd
py setup_instance.py 1.21.11 --mod path/to/yourmod-fabric-1.0.7-mc1.21.11.jar
```

### Options

| Option | Description |
|--------|-------------|
| **--mod \<path>** | Path to a mod jar to copy into the instance’s `mods` folder. |
| **--no-settings** | Do not copy Minecraft settings from **templates/minecraft/**. |
| **--no-world** | Do not copy the world (ignores **world_to_copy** for this run). |

### Examples

```cmd
py setup_instance.py 1.21.11
py setup_instance.py 1.21.11 --mod path/to/elytraassistant-fabric-1.0.7-mc1.21.11.jar
py setup_instance.py 1.21.10 --no-settings
py setup_instance.py 1.21.9 --no-world
```

## Templates

- **templates/minecraft/** – Options and other Minecraft settings to copy into new instances (e.g. `options.txt`). Edit these to match your preferred defaults.
- **templates/worlds/** – Optional. Put a world folder here (e.g. **Test World**) so new instances get that world without depending on an existing instance. See **templates/worlds/README.md** for how to add a world.

## Integration with release workflow

This tool is typically used **before** releasing a mod: create an instance (optionally with `--mod` pointing at your built jar), launch and test in-game, then run your release script (e.g. **elytra-release-tools** `release_all.py`) when satisfied.
