#include "Board.h"
#include "Sort.h"

#include <QFile>
#include <QTextStream>
#include <QStringList>
#include <QtGlobal>

Board::Board()
{
    nextId = 1;
}

void Board::addTask(Task t)
{
    t.id = nextId;
    nextId++;
    tasks.push_back(t);
}

bool Board::removeById(int id)
{
    for (int i = 0; i < tasks.size(); i++) {
        if (tasks[i].id == id) {
            tasks.removeAt(i);
            return true;
        }
    }
    return false;
}

Task *Board::findById(int id)
{
    for (int i = 0; i < tasks.size(); i++) {
        if (tasks[i].id == id)
            return &tasks[i];
    }
    return nullptr;
}

QVector<Task> Board::byStatus(int status) const
{
    QVector<Task> result;
    for (int i = 0; i < tasks.size(); i++) {
        if (tasks[i].status == status)
            result.push_back(tasks[i]);
    }
    return result;
}

int Board::overdueCount() const
{
    int c = 0;
    for (int i = 0; i < tasks.size(); i++) {
        if (tasks[i].isOverdue())
            c++;
    }
    return c;
}

int Board::soonCount() const
{
    int c = 0;
    for (int i = 0; i < tasks.size(); i++) {
        if (tasks[i].isSoon())
            c++;
    }
    return c;
}

// Формат строки: id;title;subject;yyyy-MM-dd;status;note
bool Board::loadFromFile(const QString &path)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        return false;

    tasks.clear();
    nextId = 1;

    QTextStream in(&file);
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    in.setCodec("UTF-8");
#endif

    while (!in.atEnd()) {
        QString line = in.readLine().trimmed();
        if (line.isEmpty() || line.startsWith("#"))
            continue;

        QStringList parts = line.split(";");
        if (parts.size() < 5)
            continue;

        Task t;
        t.id = parts[0].toInt();
        t.title = parts[1];
        t.subject = parts[2];
        t.deadline = QDate::fromString(parts[3], "yyyy-MM-dd");
        t.status = parts[4].toInt();
        if (parts.size() >= 6)
            t.note = parts[5];

        if (t.id >= nextId)
            nextId = t.id + 1;

        tasks.push_back(t);
    }

    return true;
}

bool Board::saveToFile(const QString &path) const
{
    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text))
        return false;

    QTextStream out(&file);
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    out.setCodec("UTF-8");
#endif

    out << QString::fromUtf8("# id;название;предмет;срок;статус;заметка\n");
    for (int i = 0; i < tasks.size(); i++) {
        const Task &t = tasks[i];
        QString note = t.note;
        note.replace(";", ",");
        out << t.id << ";"
            << t.title << ";"
            << t.subject << ";"
            << t.deadline.toString("yyyy-MM-dd") << ";"
            << t.status << ";"
            << note << "\n";
    }
    return true;
}

// Сюда приходит нажатие кнопки «Сортировать» из MainWindow::onSort().
// Сами алгоритмы НЕ здесь — они в файле src/Sort.cpp
void Board::sortTasks(int algorithm, int field)
{
    if (algorithm == 1)
        insertionSort(tasks, field); // Sort.cpp, алгоритм 2
    else if (algorithm == 2)
        floatSort(tasks, field);     // Sort.cpp, алгоритм 3 (всплытие)
    else
        bubbleSort(tasks, field);    // Sort.cpp, алгоритм 1 (пузырёк)
}
