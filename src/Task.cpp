#include "Task.h"

QString Task::statusName() const
{
    if (status == 1)
        return QString::fromUtf8("В работе");
    if (status == 2)
        return QString::fromUtf8("Готово");
    return QString::fromUtf8("Планируется");
}

int Task::daysLeft() const
{
    return QDate::currentDate().daysTo(deadline);
}

bool Task::isOverdue() const
{
    if (status == 2)
        return false;
    return daysLeft() < 0;
}

bool Task::isSoon() const
{
    if (status == 2)
        return false;
    int d = daysLeft();
    return d >= 0 && d <= 3;
}
