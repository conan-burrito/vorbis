from conans import tools, ConanFile, CMake

import os


# Note: adapted from https://github.com/conan-io/conan-center-index/tree/master/recipes/vorbis
class VorbisConan(ConanFile):
    name = 'vorbis'
    version = '1.3.7'
    description = 'Reference implementation of the Ogg Vorbis audio format.'
    homepage = 'https://github.com/xiph/vorbis'
    license = 'BSD-3-Clause'
    url = 'https://github.com/conan-burrito/vorbis'

    generators = 'cmake'

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    build_policy = 'missing'

    exports_sources = ['CMakeLists.txt', 'patches/*']

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        # It's a C project - remove irrelevant settings
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def source_subfolder(self):
        return 'src'

    @property
    def build_subfolder(self):
        return "_build"

    def requirements(self):
        self.requires("ogg/1.3.4@conan-burrito/stable")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libvorbis-{}".format(self.version), self.source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self.build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("COPYING", src=self.source_subfolder, dst="licenses", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Vorbis"
        self.cpp_info.names["cmake_find_package_multi"] = "Vorbis"

        # vorbis
        self.cpp_info.components["vorbismain"].names["cmake_find_package"] = "vorbis"
        self.cpp_info.components["vorbismain"].names["cmake_find_package_multi"] = "vorbis"
        self.cpp_info.components["vorbismain"].names["pkg_config"] = "vorbis"
        self.cpp_info.components["vorbismain"].libs = ["vorbis"]
        if self.settings.os == "Linux":
            self.cpp_info.components["vorbismain"].system_libs.append("m")
        self.cpp_info.components["vorbismain"].requires = ["ogg::ogg"]

        # vorbisenc
        self.cpp_info.components["vorbisenc"].names["cmake_find_package"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].names["cmake_find_package_multi"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].names["pkg_config"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].libs = ["vorbisenc"]
        self.cpp_info.components["vorbisenc"].requires = ["vorbismain"]

        # vorbisfile
        self.cpp_info.components["vorbisfile"].names["cmake_find_package"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].names["cmake_find_package_multi"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].names["pkg_config"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].libs = ["vorbisfile"]
        self.cpp_info.components["vorbisfile"].requires = ["vorbismain"]

        # VorbisConfig.cmake defines components 'Enc' and 'File',
        # which create the imported targets Vorbis::vorbisenc and Vorbis::vorbisfile
        self.cpp_info.components["vorbisenc-alias"].names["cmake_find_package"] = "Enc"
        self.cpp_info.components["vorbisenc-alias"].names["cmake_find_package_multi"] = "Enc"
        self.cpp_info.components["vorbisenc-alias"].requires.append("vorbisenc")
        self.cpp_info.components["vorbisfile-alias"].names["cmake_find_package"] = "File"
        self.cpp_info.components["vorbisfile-alias"].names["cmake_find_package_multi"] = "File"
        self.cpp_info.components["vorbisfile-alias"].requires.append("vorbisfile")
