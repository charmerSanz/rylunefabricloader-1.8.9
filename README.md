# Rylune Fabric 1.8.9 — 0.2.0-alpha

Client-side optimization suite for native Minecraft 1.8.9, upstream Fabric Loader and Legacy Fabric **generation 1**. Java 8 baseline. Not a new loader fork; not universal modern Fabric compatibility.

## What's new
- **Rylune Settings:** dedicated black-and-white in-game screen, Right Shift during gameplay, left-click to cycle settings, Save & close or Escape to discard. Config changes persist. Does not patch HUD, inventory or chat drawing. If Right Shift conflicts with another mod, add `-Drylune.noMenu=true` to the game's JVM arguments.
- **Logic (Lithium-inspired):** opt-in memoization of immutable vanilla block-state property hash codes. This is one optimization technique, not Lithium's complete engine. It does not alter physics or server logic.
- **Memory (FerriteCore-inspired):** opt-in, bounded weak canonicalization of resource identifier strings. Not the complete FerriteCore backport. Restart after enabling to include newly created startup resource identifiers. Memory improvements depend on duplication; measure before keeping it enabled.
- **Bridge:** native feature substitutes for Dynamic FPS, Zoomify, Lithium (one patch) and FerriteCore (one patch). Does not translate or execute a modern JAR. Optional `C` zoom is a basic native FOV effect, not smooth Zoomify.
- **Renderer:** optional external integration tool for the upstream Sodium-derived **Radium** 1.8.9 release (0.8.7, Modrinth version ID nZyz0uhf). Downloads to staging by default and checks size and SHA-512. Experimental separate installation only; no Sodium/Radium code or JAR is bundled. Radium uses an additional graphics compatibility layer; mapping generation, Java runtime, driver support and compatibility with Rylune must be tested. Do not combine with OptiFine or other renderer/LWJGL replacements. Renderer status in settings detects mod ID only, not functioning rendering.
- Existing background FPS, hidden FPS, optional particle budget, graphics presets and frame-time benchmark retained.

## Install
1. Start Minecraft 1.8.9 once via official launcher. Install Legacy Fabric at https://legacyfabric.net/ with loader 0.16.14 or compatible Java-8 version, **intermediary generation 1**.
2. Create a separate game directory, e.g. `%APPDATA%\.minecraft\rylune-1.8.9`. Set Java 8 as baseline; on 8 GB physical RAM start with about 2 GB heap (`-Xmx2G`).
3. Put the GitHub-built `RyluneFabric-1.8.9-0.2.0-alpha.jar` in the isolated `mods` folder. Remove the earlier Rylune JAR. Do not install source JARs or modern mods directly.
4. Launch, join a test world, press Right Shift. Test the base configuration first. Leave experimental settings OFF until baseline is stable. Escape cancels edits. Use matching Legacy Fabric API only when needed by other mods.
5. Enable one experimental feature at a time and benchmark. If the game fails to start, remove the Rylune JAR and save latest.log. `enabled=false` stops optional behavior but cannot undo class transformation or existing deduplicated strings. Do not assume compatibility with Lunar, Badlion, OneClient or competitive server rules.

## Optional Radium renderer
Close Minecraft. Run from the extracted source folder (Python 3.8+):

```
python tools/bridge.py renderer "C:\path\to\rylune-instance" --java 8
```

This stages the pinned upstream JAR and prints its metadata, bytecode requirement and upstream dependencies. If Java 8 is rejected, follow the upstream release requirements before trying a newer runtime. The modern-runtime compatibility of Rylune itself has not been tested. The tool cannot prove the correct intermediary generation or graphics bridge compatibility. Only in a disposable test profile, after reviewing requirements, add `--install` and use the runtime you actually configured in the launcher. If the upstream dependency metadata requires additional projects, installation is refused; inspect their release instructions and install manually if appropriate. For manual testing, see https://modrinth.com/mod/radium-mod/version/nZyz0uhf . Do not use conflicting renderers. Remove Radium if it crashes or renders incorrectly. No third-party renderer is distributed by Rylune.

## Native compatibility features
```
python tools/bridge.py adapt "C:\path\to\rylune-instance" dynamic_fps
python tools/bridge.py adapt "C:\path\to\rylune-instance" zoomify
python tools/bridge.py adapt "C:\path\to\rylune-instance" lithium
python tools/bridge.py adapt "C:\path\to\rylune-instance" ferritecore
python tools/rylune.py scan "C:\path\to\mods" --java 8 --json
python tools/rylune.py preset "C:\path\to\rylune-instance" low
```

The bridge writes only Rylune configuration, backing up the previous file. Do not install the original modern JAR. The scanner reports candidates, not guaranteed compatible mods. The loader still performs dependency validation. No version bypass or bytecode rewriting is done. For vanilla PvP cues leave particleBudget=0. `benchmark=true` writes local `rylune-benchmark.csv` during focused play.

## Build (real dependencies)
Install JDK 17, Python 3.8+, Gradle 8.12.1. Run `python tools/prepare_game.py`, then `gradle --no-daemon clean build` (or `build.bat` on Windows). The preparatory script obtains Mojang's official 1.8.9 client and libraries, verifies Mojang checksums, and remaps it using Legacy Fabric generation-1 mappings and Tiny Remapper. The Gradle compile uses the actual game classes; the remapped game and libraries remain in ignored `.gradle/rylune-game/` and are never included in the mod/source ZIP. Do not commit the Minecraft JARs. Build depends on network access.

GitHub: the workflow automatically builds on pushes to main and publishes the prerelease `v0.2.0-alpha` only if the build and tests succeed. To rerun manually, use **Actions > Build and release Rylune Fabric > Run workflow** and leave publish enabled on main. Output `build/libs/RyluneFabric-1.8.9-0.2.0-alpha.jar` (not `-sources.jar`).

## Verification status
Pure Java core tests and five Python tests passed locally. All Java source syntax was checked against temporary minimal API signatures (not actual Minecraft runtime; stubs are not shipped). The real Gradle build, renderer download/install, and game launch have not been run locally because network/dependencies are unavailable. Check GitHub Actions for the dependency-based build result. No guaranteed FPS or RAM improvement.

## Credits / licensing
Rylune original code: MIT. Legacy Fabric intermediary mapping names: https://github.com/Legacy-Fabric/Legacy-Intermediaries . Tiny Remapper: https://github.com/FabricMC/tiny-remapper . Radium is an independent upstream project under its own license; it is downloaded directly from Modrinth only when requested. Lithium and FerriteCore are inspiration, not bundled code or endorsements. Minecraft is not redistributed. See docs/TESTING.md and docs/ROADMAP.md.
