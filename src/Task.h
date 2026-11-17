#ifndef TASK_H
#define TASK_H

#include <QString>
#include <QDate>

// Учебная задача на канбан-доске
struct Task {
    int id;
    QString title;
    QString subject;
    QDate deadline;
    int status; // 0 - планируется, 1 - в работе, 2 - готово
    QString note;

    QString statusName() const;
    int daysLeft() const;
    bool isOverdue() const;
    bool isSoon() const; // срок в ближайшие 3 дня
};

#endif
