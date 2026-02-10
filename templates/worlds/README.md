# World templates

Put world saves here so new instances get them without depending on any existing MultiMC instance.

**To add "Test World" (or any world):**

1. Copy the world folder from an instance’s `.minecraft/saves/` into this directory.
   - Example: from `…\MultiMC\instances\1.21.3\.minecraft\saves\Test World`  
     copy the whole **Test World** folder so you have:
     `templates/worlds/Test World/` (with `level.dat`, `region/`, etc. inside).
2. Run `setup_instance.py` as usual. It will use this copy first.

The script looks for worlds in this order: **templates/worlds/** → config `world_source_dir` → existing instances.

**Repo size:** World saves are large (hundreds of MB). To keep the repo small, add to `.gitignore`:

```
templates/worlds/Test World/
```

(or ignore `templates/worlds/*/` to exclude all world folders). The README can stay committed. If you’re fine with the size, you can commit the world and have it versioned with the project.
