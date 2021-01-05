

import cmake_generator as gen

lib = gen.Library("toto_shared")

headers = [
    "toto_shared.h",
    "sub-lib/lib.h",
]

sources = [
    "toto_shared.cpp",
    "sub-lib/lib.cpp",
]

lib.add_sources(sources)
lib.add_headers(headers)

project = gen.Project("JSONUtils", "1.0.0", custom_install="$ENV{HOME}/install", install=True)
project.add_targets(lib)

project.write()
