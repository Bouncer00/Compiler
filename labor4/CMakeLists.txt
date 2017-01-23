cmake_minimum_required(VERSION 3.6)
project(labor4)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        interpreter.cc)

add_executable(labor4 ${SOURCE_FILES})