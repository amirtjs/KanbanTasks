#ifndef BOARD_H
#define BOARD_H

#include <QVector>
#include <QString>
#include "Task.h"

// Хранит все задачи и умеет читать/писать текстовый файл
class Board
{
public:
    QVector<Task> tasks;
    int nextId;

    Board();

    void addTask(Task t);
    bool removeById(int id);
    Task *findById(int id);
    QVector<Task> byStatus(int status) const;

    int overdueCount() const;
    int soonCount() const;

    bool loadFromFile(const QString &path);
    bool saveToFile(const QString &path) const;

    // Выбор алгоритма сортировки (реализация в Board.cpp, сами алгоритмы в Sort.cpp)
    // algorithm: 0 пузырёк, 1 вставки, 2 всплытие
    // field:     0 срок, 1 название, 2 предмет
    void sortTasks(int algorithm, int field);
};

#endif
