#!/usr/bin/env python3
"""
MultiMC Instance Creator
Automates creation of Minecraft instances with Fabric loader and mods from Modrinth
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional

# Configuration: paths and world name come from config.json (see config.example.json).
MODRINTH_API_BASE = "https://api.modrinth.com/v2"
FABRIC_META_API = "https://meta.fabricmc.net/v2"

# Mods to download from Modrinth
DEFAULT_MODS = [
    "fabric-api",
    "modmenu",
    "cloth-config"
]


def get_config() -> Dict:
    """Load config.json from script dir. User-specific paths must be set there (see config.example.json)."""
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / "config.json"
    allowed_keys = {
        "multimc_instances_path",
        "java_path",
        "world_source_dir",
        "world_to_copy",
    }
    defaults = {
        "multimc_instances_path": None,
        "java_path": None,
        "world_source_dir": None,
        "world_to_copy": "Test World",
    }
    if not config_path.exists():
        example = script_dir / "config.example.json"
        if example.exists():
            print(f"config.json not found. Copy config.example.json to config.json and set your paths.")
            print(f"  Example: copy {example.name} config.json")
        return defaults
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return {**defaults, **{k: v for k, v in data.items() if k in allowed_keys}}
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}. Using defaults.")
        return defaults


def fetch_json(url: str) -> Dict:
    """Fetch JSON from a URL"""
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}")
        sys.exit(1)


def download_file(url: str, dest_path: Path) -> None:
    """Download a file from URL to destination"""
    try:
        print(f"Downloading {dest_path.name}...")
        with urllib.request.urlopen(url) as response:
            dest_path.write_bytes(response.read())
        print(f"[OK] Downloaded {dest_path.name}")
    except urllib.error.URLError as e:
        print(f"Error downloading {url}: {e}")
        sys.exit(1)


def get_latest_fabric_loader() -> str:
    """Get the latest stable Fabric loader version"""
    url = f"{FABRIC_META_API}/versions/loader"
    data = fetch_json(url)
    if not data:
        print("Error: Could not fetch Fabric loader versions")
        sys.exit(1)
    return data[0]["version"]


def get_modrinth_mod_version(mod_slug: str, mc_version: str, loader: str = "fabric") -> Optional[Dict]:
    """Get the latest compatible mod version from Modrinth"""
    url = f"{MODRINTH_API_BASE}/project/{mod_slug}/version?loaders=%5B%22{loader}%22%5D&game_versions=%5B%22{mc_version}%22%5D"
    try:
        data = fetch_json(url)
        if not data:
            print(f"Warning: No versions found for {mod_slug} on {mc_version}")
            return None
        return data[0]  # Return the latest version
    except Exception as e:
        print(f"Warning: Could not fetch {mod_slug}: {e}")
        return None


def create_instance_cfg(instance_name: str, java_path: str) -> str:
    """Generate instance.cfg content"""
    return f"""AutoCloseConsole=false
ForgeVersion=
InstanceType=OneSix
IntendedVersion=
JavaPath={java_path}
JoinServerOnLaunch=false
JoinServerOnLaunchAddress=
JoinSingleplayerWorldOnLaunch=false
JoinSingleplayerWorldOnLaunchName=
JoinWorldOnLaunch=false
JvmArgs=
LWJGLVersion=
LaunchMaximized=false
LiteloaderVersion=
LogPrePostOutput=true
MCLaunchMethod=LauncherPart
ManagedPack=false
ManagedPackID=
ManagedPackName=
ManagedPackType=
ManagedPackVersionID=
ManagedPackVersionName=
MaxMemAlloc=16384
MinMemAlloc=4096
MinecraftWinHeight=480
MinecraftWinWidth=854
OverrideCommands=false
OverrideConsole=false
OverrideGameTime=false
OverrideJava=false
OverrideJavaArgs=false
OverrideJavaLocation=false
OverrideMCLaunchMethod=false
OverrideMemory=false
OverrideNativeWorkarounds=false
OverrideWindow=false
PermGen=128
PostExitCommand=
PreLaunchCommand=
RecordGameTime=true
ShowConsole=false
ShowConsoleOnError=true
ShowGameTime=true
UseNativeGLFW=false
UseNativeOpenAL=false
WrapperCommand=
iconKey=default
lastLaunchTime=0
lastTimePlayed=0
name={instance_name}
notes=
totalTimePlayed=0
"""


def create_mmc_pack_json(mc_version: str, fabric_loader_version: str) -> Dict:
    """Generate mmc-pack.json structure"""
    return {
        "components": [
            {
                "cachedName": "Minecraft",
                "cachedVersion": mc_version,
                "important": True,
                "uid": "net.minecraft",
                "version": mc_version
            },
            {
                "cachedName": "Intermediary Mappings",
                "cachedRequires": [
                    {
                        "equals": mc_version,
                        "uid": "net.minecraft"
                    }
                ],
                "cachedVersion": mc_version,
                "cachedVolatile": True,
                "dependencyOnly": True,
                "uid": "net.fabricmc.intermediary",
                "version": mc_version
            },
            {
                "cachedName": "Fabric Loader",
                "cachedRequires": [
                    {
                        "uid": "net.fabricmc.intermediary"
                    }
                ],
                "cachedVersion": fabric_loader_version,
                "uid": "net.fabricmc.fabric-loader",
                "version": fabric_loader_version
            }
        ],
        "formatVersion": 1
    }


def get_settings_template_dir() -> Path:
    """Path to local templates/minecraft/ (options.txt, optional servers.dat)."""
    return Path(__file__).resolve().parent / "templates" / "minecraft"


def copy_minecraft_settings(dest_minecraft_path: Path) -> None:
    """Copy Minecraft settings from local templates/minecraft/ into the instance."""
    template_dir = get_settings_template_dir()
    if not template_dir.exists():
        print(f"Warning: Settings template dir not found at {template_dir}")
        return

    print("\nCopying Minecraft settings from templates/minecraft/...")
    import shutil
    for entry in template_dir.iterdir():
        if entry.is_file():
            dest_file = dest_minecraft_path / entry.name
            shutil.copy2(entry, dest_file)
            print(f"  [OK] Copied {entry.name}")


def get_template_world_path(world_name: str) -> Path:
    """Path to a world under this project's templates/worlds/ (e.g. templates/worlds/Test World)."""
    return Path(__file__).resolve().parent / "templates" / "worlds" / world_name


def find_world_source(world_name: str, config: Dict) -> Optional[Path]:
    """Find world: project templates/worlds/ first, then config world_source_dir, then any instance."""
    # 1) Local to this project – no dependency on instances or external paths
    local = get_template_world_path(world_name)
    if local.exists() and local.is_dir():
        return local
    # 2) Optional backup dir from config
    world_dir = config.get("world_source_dir")
    if world_dir:
        path = Path(world_dir) / world_name
        if path.exists() and path.is_dir():
            return path
    # 3) Search existing instances
    instances_path = Path(config["multimc_instances_path"])
    if not instances_path.exists():
        return None
    for entry in instances_path.iterdir():
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        saves = entry / ".minecraft" / "saves" / world_name
        if saves.exists() and saves.is_dir():
            return saves
    return None


def copy_world(world_name: str, dest_minecraft_path: Path, config: Dict) -> None:
    """Copy a world save from config world_source_dir or an instance into the new instance's saves folder."""
    import shutil
    source = find_world_source(world_name, config)
    if not source:
        print(f"\nWarning: World '{world_name}' not found. Add it under templates/worlds/{world_name}/ or set config world_source_dir, or keep an instance that has it.")
        return
    dest_saves = dest_minecraft_path / "saves"
    dest_saves.mkdir(parents=True, exist_ok=True)
    dest_world = dest_saves / world_name
    if dest_world.exists():
        print(f"\nWarning: Destination {dest_world} already exists; skipping world copy.")
        return
    print(f"\nCopying world '{world_name}'...")
    shutil.copytree(source, dest_world)
    if source.resolve() == get_template_world_path(world_name).resolve():
        from_label = "templates/worlds/"
    elif config.get("world_source_dir") and source.parent.resolve() == Path(config["world_source_dir"]).resolve():
        from_label = "backup"
    else:
        from_label = source.parent.parent.parent.name  # instance folder name
    print(f"  [OK] Copied from {from_label}")


def create_instance(mc_version: str, custom_mod_path: Optional[str] = None, copy_settings: bool = True, copy_world_save: bool = True) -> None:
    """Create a new MultiMC instance with Fabric and mods"""
    config = get_config()

    if not config.get("multimc_instances_path") or not config.get("java_path"):
        print("Error: Set multimc_instances_path and java_path in config.json (see config.example.json).")
        sys.exit(1)

    print(f"\n=== Creating MultiMC Instance for Minecraft {mc_version} ===\n")

    # Setup paths
    instance_path = Path(config["multimc_instances_path"]) / mc_version
    minecraft_path = instance_path / ".minecraft"
    mods_path = minecraft_path / "mods"

    # Check if instance already exists
    if instance_path.exists():
        response = input(f"Instance '{mc_version}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        print("Removing existing instance...")
        import shutil
        shutil.rmtree(instance_path)

    # Create directory structure
    print("Creating directory structure...")
    mods_path.mkdir(parents=True, exist_ok=True)

    # Get latest Fabric loader version
    print("Fetching latest Fabric loader version...")
    fabric_loader_version = get_latest_fabric_loader()
    print(f"[OK] Using Fabric Loader {fabric_loader_version}")

    # Create instance.cfg
    print("Creating instance.cfg...")
    (instance_path / "instance.cfg").write_text(create_instance_cfg(mc_version, config["java_path"]))
    print("[OK] Created instance.cfg")

    # Create mmc-pack.json
    print("Creating mmc-pack.json...")
    mmc_pack = create_mmc_pack_json(mc_version, fabric_loader_version)
    (instance_path / "mmc-pack.json").write_text(json.dumps(mmc_pack, indent=4))
    print("[OK] Created mmc-pack.json")

    # Download mods from Modrinth
    print("\nDownloading mods from Modrinth...")
    for mod_slug in DEFAULT_MODS:
        print(f"\nFetching {mod_slug}...")
        mod_version = get_modrinth_mod_version(mod_slug, mc_version)
        if mod_version:
            # Get the primary file
            files = mod_version.get("files", [])
            if files:
                primary_file = next((f for f in files if f.get("primary", False)), files[0])
                download_url = primary_file["url"]
                filename = primary_file["filename"]
                download_file(download_url, mods_path / filename)

    # Copy custom mod if provided
    if custom_mod_path:
        print(f"\nCopying custom mod...")
        custom_mod = Path(custom_mod_path)
        if custom_mod.exists():
            import shutil
            shutil.copy2(custom_mod, mods_path / custom_mod.name)
            print(f"[OK] Copied {custom_mod.name}")
        else:
            print(f"Warning: Custom mod not found at {custom_mod_path}")

    # Copy Minecraft settings from local templates/minecraft/
    if copy_settings:
        copy_minecraft_settings(minecraft_path)

    # Copy world if configured (world_to_copy in config; source: world_source_dir or existing instance)
    world_to_copy = config.get("world_to_copy")
    if copy_world_save and world_to_copy:
        copy_world(world_to_copy, minecraft_path, config)

    print(f"\n=== Instance '{mc_version}' created successfully! ===")
    print(f"Location: {instance_path}")
    print("\nYou can now launch this instance from MultiMC.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python setup_instance.py <minecraft_version> [options]")
        print("\nOptions:")
        print("  --mod <path>        Path to custom mod jar to include")
        print("  --no-settings       Don't copy Minecraft settings from template")
        print("  --no-world          Don't copy the world (world name is set in config.json)")
        print("\nExamples:")
        print("  python setup_instance.py 1.21.11")
        print("  python setup_instance.py 1.21.11 --mod C:/path/to/mymod.jar")
        print("  python setup_instance.py 1.21.11 --no-settings")
        print("  python setup_instance.py 1.21.9 --no-world")
        sys.exit(1)

    mc_version = sys.argv[1]

    # Parse options
    custom_mod_path = None
    copy_settings = True
    copy_world_save = True

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--mod' and i + 1 < len(args):
            custom_mod_path = args[i + 1]
            i += 2
        elif args[i] == '--no-settings':
            copy_settings = False
            i += 1
        elif args[i] == '--no-world':
            copy_world_save = False
            i += 1
        else:
            # Legacy support: positional argument for mod path
            custom_mod_path = args[i]
            i += 1

    create_instance(mc_version, custom_mod_path, copy_settings, copy_world_save)


if __name__ == "__main__":
    main()
