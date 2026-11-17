#ifndef SORT_H
#define SORT_H

#include <QVector>
#include "Task.h"

/*
 * ============================================================
 *  СОРТИРОВКА ЗАДАЧ — заголовочный файл
 *  Реализация алгоритмов: src/Sort.cpp
 *  Вызов из доски:        src/Board.cpp  -> Board::sortTasks()
 *  Кнопка в окне:         src/MainWindow.cpp -> MainWindow::onSort()
 * ============================================================
 */

// Поле, по которому сравниваем задачи (индекс совпадает с comboField в окне)
enum SortField {
    ByDeadline = 0, // по сроку сдачи
    ByTitle = 1,    // по названию
    BySubject = 2   // по предмету
};

// Сравнение двух задач. Нужна всем трём алгоритмам ниже.
bool taskLess(const Task &a, const Task &b, int field);

// --- Алгоритм 1. Пузырьковая сортировка (bubbleSort) ---
void bubbleSort(QVector<Task> &arr, int field);

// --- Алгоритм 2. Сортировка вставками (insertionSort) ---
void insertionSort(QVector<Task> &arr, int field);

// --- Алгоритм 3. Сортировка всплытием / шейкерная (floatSort) ---
void floatSort(QVector<Task> &arr, int field);

#endif
