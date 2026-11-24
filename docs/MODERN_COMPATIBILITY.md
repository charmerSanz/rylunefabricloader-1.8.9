# Modern Fabric compatibility bridge

Rylune 0.4 introduces an offline compatibility preflight and staging converter. It is **not** a universal translator and does not make modern Minecraft internals available in 1.8.9.

## Supported subset

Portable Java mods with ordinary Fabric main/client initializer entrypoints, no Minecraft or Fabric API linkage, no Mixins/access wideners/nested JARs, no unbundled dependencies other than Fabric Loader/Java, and compatible Java class versions and loader requirements. The converter preserves original class bytes, loader and Java constraints, license files, and stores original metadata plus a source SHA-256 in the output. It adjusts the Minecraft version constraint only after preflight. Static checks cannot establish runtime compatibility or trust. Java 8/17/21/25 options check the selected version; they do not configure the launcher or make Minecraft 1.8.9 work on it.

From the extracted release source (Python 3.8+, no pip packages):

```cmd
python tools/modern_bridge.py inspect "C:\mods\example.jar"
python tools/modern_bridge.py convert "C:\mods\example.jar" "C:\rylune-staging\example-1.8.9.jar" --permission-to-adapt
```

Use the conversion command only if you have rights to modify the mod. Test the staged JAR in a disposable Ornithe Gen 2 instance with the matching Java and Fabric Loader. Do not install the original and adapted JAR together. Only run trusted mods; this scanner is not a security sandbox. It intentionally rejects many legitimate but nontrivial mods. It does not validate all bytecode linkages, Java standard-library API versions or reflective lookups.

## Native feature fallback

For incompatible modern Dynamic FPS, Zoomify, Lithium and FerriteCore JARs:

```cmd
python tools/modern_bridge.py native "C:\mods\lithium.jar" "%APPDATA%\.minecraft\rylune-1.8.9"
```

This reads the mod ID and enables Rylune's existing corresponding native feature. It does not load the original JAR. Lithium and FerriteCore alternatives are limited to selected experimental patches, not full engine ports. Sodium/Iris need a renderer backport; use a renderer explicitly built for Ornithe Gen 2; automatic Radium installation is disabled. The OneClient bridge defaults to Java 25. Use --loader with the actual installed loader version if different from 0.16.14. No automatic version bypass for ordinary game-dependent mods.

## Test coverage

CI compiles real Java fixture classes against Java 8 and Java 17 targets. It verifies preservation of original class bytes and metadata; rejects modern Minecraft linkage, mismatched Java/loader constraints, required Fabric API, Mixins and signed archives. A passing CI build is not proof of Minecraft runtime compatibility.
