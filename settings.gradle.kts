rootProject.name = "jlisa-witness-validator"

// jLISA composite build — not yet published to Maven Central, use a local checkout.
// Gradle automatically substitutes implementation("it.unive.jlisa:jlisa") with this build.
//
// Point at your local jLISA checkout via (in order of precedence):
//   1. -PjlisaPath=/abs/or/rel/path/to/jlisa   (Gradle property)
//   2. JLISA_HOME environment variable
//   3. default: ../jlisa   (sibling directory of this repo)
val jlisaPath = startParameter.projectProperties["jlisaPath"]
    ?: System.getenv("JLISA_HOME")
    ?: "../jlisa/jlisa"
includeBuild(jlisaPath)
