# Rylune Fabric 1.8.9 — OneClient / Ornithe Gen 2 — 0.4.0-alpha

This edition targets OneClient's Ornithe Calamus generation-2 mappings and Java 25 runtime. The previous v0.3.0-alpha targets Legacy Fabric generation 1 and must not be installed alongside this edition.

## Install
1. Open the OneClient 1.8.9 instance mods folder.
2. Remove earlier Rylune JARs and original modern-version mods; keep the client's existing dependencies.
3. Install only `RyluneFabric-1.8.9-OneClient-0.4.0-alpha.jar` from Releases after CI succeeds. Keep OneClient's own Java 25 setup.
4. Join a test world and press **F8** for Rylune settings. Right Shift is reserved for OneClient. Check latest.log for `Rylune Ornithe Gen 2 frame hook active`. Do not assume a successful build is a successful game launch.
5. Keep optional particle, hash cache, string pool and zoom patches off initially; enable individually only after testing. If a crash occurs remove Rylune and retain the log.

## Changes
- All five Mixin class targets and mapped method/field references ported by joining official obfuscated names from Legacy Fabric and Ornithe Calamus Gen 2 mappings.
- Build validates injection signatures against the remapped official 1.8.9 client; compiles the GUI against actual game classes.
- F8 settings menu, background FPS limiter, particle budget, optional block-state hash cache and resource-string pool, hold C zoom, benchmark.
- Modern bridge preflight accepts Java 25 and distinguishes native candidates, portable candidates and unsupported game-dependent JARs.
- Radium auto-install disabled for this edition because the pinned upstream build has not been confirmed for Ornithe Gen 2. OneClient already supplies rendering mods: don't install conflicting renderers.

## Modern Fabric mods
Use [the compatibility guide](docs/MODERN_COMPATIBILITY.md). This is NOT a modern Minecraft engine. A 1.21.x/26.x mod referencing modern Minecraft or Fabric APIs cannot be made compatible merely by updating Java or mapping names. Native substitutes for Dynamic FPS, Zoomify, selected Lithium/FerriteCore features are included, not full backports. Only portable pure-Java entrypoints can be experimentally adapted. Original modern JARs must remain outside mods.

## Build
JDK 17, Python 3.8+, Gradle 8.12.1. Run `python tools/prepare_game.py`, `python tools/verify_targets.py`, then `gradle --no-daemon clean build`. GitHub Actions compiles and publishes only on success. Java 8 classfile output remains compatible with Java 25. Game files stay in ignored .gradle; no Mojang binaries are distributed.

## Credits
Original Rylune code MIT. Mapping sources: https://github.com/OrnitheMC/calamus (CC0), https://github.com/Legacy-Fabric/Legacy-Intermediaries . Tiny Remapper: https://github.com/FabricMC/tiny-remapper . Third-party projects are independent. Runtime and performance validation on OneClient remain required.
