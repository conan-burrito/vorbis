cmake_minimum_required(VERSION 3.6)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Vorbis REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example Vorbis::vorbisenc)
set_target_properties(example
    PROPERTIES
    OUTPUT_NAME "test"
    CXX_STANDARD 11
)
