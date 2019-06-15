#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng"
    upstream_version = "1.6.34"
    package_revision = "-r2"
    version = "{0}{1}".format(upstream_version, package_revision)

    description = "libpng is the official PNG file format reference library."
    homepage = "http://www.libpng.org"
    license = "http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeProjectWrapper.txt",
        "patches/skip-install-symlink.patch"
    ]
    url = "https://git.ircad.fr/conan/conan-libpng"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        
    def requirements(self):
        self.requires("common/1.0.0@sight/stable")
        if tools.os_info.is_windows:
            self.requires("zlib/1.2.11-r2@sight/testing")

    def source(self):
        tools.get("https://github.com/glennrp/libpng/archive/v{0}.tar.gz".format(self.upstream_version))
        os.rename("libpng-" + self.upstream_version, self.source_subfolder)

    def build(self):
        # Import common flags and defines
        import common

        libpng_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")
        tools.patch(libpng_source_dir, "patches/skip-install-symlink.patch")
        cmake = CMake(self)
        
        # Set common flags
        cmake.definitions["SIGHT_CMAKE_C_FLAGS"] = common.get_c_flags()
        cmake.definitions["SIGHT_CMAKE_CXX_FLAGS"] = common.get_cxx_flags()
        
        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        cmake.definitions["SKIP_INSTALL_PROGRAMS"] = "ON"
        cmake.definitions["SKIP_INSTALL_EXECUTABLES"] = "ON"
        if tools.os_info.is_windows or tools.os_info.is_macos:
            cmake.definitions["SKIP_INSTALL_SYMLINK"] = "ON"            
        else:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"
            
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
