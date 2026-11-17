QT += widgets
CONFIG += c++17
TEMPLATE = app
TARGET = KanbanTasks

SOURCES += \
    src/main.cpp \
    src/Task.cpp \
    src/Sort.cpp \
    src/Board.cpp \
    src/MainWindow.cpp

HEADERS += \
    src/Task.h \
    src/Sort.h \
    src/Board.h \
    src/MainWindow.h

INCLUDEPATH += src
