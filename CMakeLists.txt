cmake_minimum_required(VERSION 3.16)
project(KanbanTasks LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets)

set(SOURCES
    src/main.cpp
    src/Task.cpp
    src/Sort.cpp
    src/Board.cpp
    src/MainWindow.cpp
)

set(HEADERS
    src/Task.h
    src/Sort.h
    src/Board.h
    src/MainWindow.h
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_add_executable(KanbanTasks ${SOURCES} ${HEADERS})
else()
    add_executable(KanbanTasks ${SOURCES} ${HEADERS})
endif()

target_include_directories(KanbanTasks PRIVATE src)
target_link_libraries(KanbanTasks PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

if(MSVC)
    target_compile_options(KanbanTasks PRIVATE /utf-8)
endif()
