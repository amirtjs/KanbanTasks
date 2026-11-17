#include "Sort.h"

/*
 * Файл src/Sort.cpp — здесь находится ВЕСЬ функционал сортировки.
 *
 * Как это связано с остальной программой:
 *   1) Пользователь жмёт «Сортировать» в окне
 *      (MainWindow::onSort, файл src/MainWindow.cpp)
 *   2) Окно вызывает Board::sortTasks(номер алгоритма, поле)
 *      (файл src/Board.cpp)
 *   3) sortTasks выбирает одну из трёх функций этого файла:
 *        0 -> bubbleSort     (пузырьком)
 *        1 -> insertionSort  (вставками)
 *        2 -> floatSort      (всплытием, шейкерная)
 */

// Сравнение задач: что считать «меньше».
// field = 0 срок, 1 название, 2 предмет.
bool taskLess(const Task &a, const Task &b, int field)
{
    if (field == ByTitle)
        return a.title.toLower() < b.title.toLower();
    if (field == BySubject)
        return a.subject.toLower() < b.subject.toLower();

    // по умолчанию — по сроку, если даты равны то по названию
    if (a.deadline != b.deadline)
        return a.deadline < b.deadline;
    return a.title.toLower() < b.title.toLower();
}

// ============================================================
// АЛГОРИТМ 1. СОРТИРОВКА ПУЗЫРЬКОМ
// Идея: соседние элементы сравниваются, больший «всплывает» вправо.
// Сложность: O(n^2)
// ============================================================
void bubbleSort(QVector<Task> &arr, int field)
{
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {                 // сколько проходов
        for (int j = 0; j < n - 1 - i; j++) {         // сравнение соседей
            if (taskLess(arr[j + 1], arr[j], field)) {
                // меняем местами, если порядок нарушен
                Task tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

// ============================================================
// АЛГОРИТМ 2. СОРТИРОВКА ВСТАВКАМИ
// Идея: берём очередной элемент и вставляем его в уже
// отсортированную левую часть массива.
// Сложность: O(n^2), на почти упорядоченных данных быстрее пузырька
// ============================================================
void insertionSort(QVector<Task> &arr, int field)
{
    int n = arr.size();
    for (int i = 1; i < n; i++) {
        Task key = arr[i];          // текущая задача, которую вставляем
        int j = i - 1;
        while (j >= 0 && taskLess(key, arr[j], field)) {
            arr[j + 1] = arr[j];    // сдвигаем вправо тех, кто больше key
            j--;
        }
        arr[j + 1] = key;           // вставка на свободное место
    }
}

// ============================================================
// АЛГОРИТМ 3. СОРТИРОВКА ВСПЛЫТИЕМ (шейкерная / cocktail sort)
// Идея: как пузырёк, но проход в обе стороны.
// Сначала максимум всплывает в конец, потом минимум «тонет» в начало.
// Сложность: O(n^2), на практике чуть меньше обменов, чем у пузырька
// ============================================================
void floatSort(QVector<Task> &arr, int field)
{
    int left = 0;
    int right = arr.size() - 1;
    while (left < right) {
        // проход слева направо — большой элемент всплывает
        for (int i = left; i < right; i++) {
            if (taskLess(arr[i + 1], arr[i], field)) {
                Task tmp = arr[i];
                arr[i] = arr[i + 1];
                arr[i + 1] = tmp;
            }
        }
        right--;

        // проход справа налево — маленький элемент тонет
        for (int i = right; i > left; i--) {
            if (taskLess(arr[i], arr[i - 1], field)) {
                Task tmp = arr[i];
                arr[i] = arr[i - 1];
                arr[i - 1] = tmp;
            }
        }
        left++;
    }
}
