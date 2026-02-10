# Minecraft settings template

Files in this folder are copied into new instances' `.minecraft/` when you run `setup_instance.py` (unless you use `--no-settings`).

- **options.txt** – Video, controls, **keybinds**, sound, etc. Includes full keybinds from your previous setup (e.g. Elytra Assistant toggle on mouse 5, Jade, Xaero, Mod Menu). Only `resourcePacks` and `incompatibleResourcePacks` are kept minimal so new instances don't reference missing packs. Edit this file to change defaults for new instances.
- **servers.dat** (optional) – Server list. If you add this file here, it will be copied too. You can copy it from an existing instance's `.minecraft/servers.dat` if you want the same server list in every new instance.

No dependency on any MultiMC instance; everything is stored in this repo.
