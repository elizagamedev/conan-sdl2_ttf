#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake


class SDL2TtfConan(ConanFile):
    name = "sdl2_ttf"
    version = "2.0.15"
    description = "A TrueType font library for SDL2"
    topics = ("conan", "sdl2", "sdl2_ttf", "sdl", "sdl_ttf", "ttf", "font")
    url = "https://github.com/bincrafters/conan-sdl2_ttf"
    homepage = "https://www.libsdl.org/projects/SDL_ttf"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "ZLIB"
    exports = "LICENSE.md"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    requires = (
        "freetype/2.9.1@bincrafters/stable",
        "sdl2/2.0.9@bincrafters/stable",
    )
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    def config_options(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio":
            del self.options.shared
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        extracted_folder = "SDL2_ttf-{}".format(self.version)
        sha256 = "a9eceb1ad88c1f1545cd7bd28e7cbc0b2c14191d40238f531a15b01b1b22cd33"
        tools.get("{}/release/{}.tar.gz".format(self.homepage, extracted_folder), sha256=sha256)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists,
        "target_link_libraries(SDL2_ttf SDL2::SDL2 Freetype::Freetype)",
        "target_link_libraries(SDL2_ttf SDL2::SDL2 Freetype::Freetype ${CONAN_LIBS})")
        if not self.options["sdl2"].shared:
            tools.replace_in_file(cmakelists, "SDL2::SDL2", "SDL2::SDL2-static")
        tools.replace_in_file(cmakelists, "${CMAKE_BINARY_DIR}", "${CMAKE_CURRENT_BINARY_DIR}")
        # missing from distribution
        tools.save(os.path.join(self._source_subfolder, "SDL2_ttfConfig.cmake"),
                   """include(CMakeFindDependencyMacro)
find_dependency(Freetype)
include("${CMAKE_CURRENT_LIST_DIR}/SDL2_TTFTargets.cmake""")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
