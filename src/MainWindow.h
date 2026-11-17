#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QListWidget>
#include <QComboBox>
#include <QLabel>
#include <QDateEdit>
#include <QLineEdit>
#include <QTextEdit>

#include "Board.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);

private slots:
    void onAdd();
    void onEdit();
    void onDelete();
    void onMoveDoing();
    void onMoveDone();
    void onMoveBack();
    void onSort(); // кнопка сортировки -> Board::sortTasks -> src/Sort.cpp
    void onSave();
    void onLoad();

private:
    Board board;
    QString dataPath;

    QListWidget *listTodo;
    QListWidget *listDoing;
    QListWidget *listDone;
    QComboBox *comboAlgo;
    QComboBox *comboField;
    QLabel *labelInfo;

    void refreshLists();
    void fillList(QListWidget *list, int status);
    int selectedId() const;
    QListWidget *activeList() const;
    bool editTaskDialog(Task &task, const QString &windowTitle);
};

#endif
