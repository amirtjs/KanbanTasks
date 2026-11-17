#include "MainWindow.h"

#include <QWidget>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QPushButton>
#include <QGroupBox>
#include <QFormLayout>
#include <QDialog>
#include <QDialogButtonBox>
#include <QMessageBox>
#include <QFileDialog>
#include <QFile>
#include <QCoreApplication>
#include <QDir>
#include <QColor>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setWindowTitle(QString::fromUtf8("Канбан учебных задач"));
    resize(980, 620);

    dataPath = QCoreApplication::applicationDirPath() + "/tasks.txt";
    // если рядом с exe нет файла, берём из папки проекта (удобно при запуске из Qt Creator)
    if (!QFile::exists(dataPath)) {
        QString fromProject = QDir(QCoreApplication::applicationDirPath()).absoluteFilePath("../data/tasks.txt");
        if (QFile::exists(fromProject))
            dataPath = fromProject;
        else
            dataPath = QDir::currentPath() + "/data/tasks.txt";
    }

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);

    QHBoxLayout *top = new QHBoxLayout();
    QPushButton *btnAdd = new QPushButton(QString::fromUtf8("Добавить"));
    QPushButton *btnEdit = new QPushButton(QString::fromUtf8("Изменить"));
    QPushButton *btnDel = new QPushButton(QString::fromUtf8("Удалить"));
    QPushButton *btnLoad = new QPushButton(QString::fromUtf8("Открыть"));
    QPushButton *btnSave = new QPushButton(QString::fromUtf8("Сохранить"));

    comboField = new QComboBox();
    comboField->addItem(QString::fromUtf8("По сроку"));
    comboField->addItem(QString::fromUtf8("По названию"));
    comboField->addItem(QString::fromUtf8("По предмету"));

    // Список алгоритмов. Индекс = номер в Board::sortTasks / Sort.cpp
    comboAlgo = new QComboBox();
    comboAlgo->addItem(QString::fromUtf8("Пузырьком"));  // индекс 0 -> bubbleSort
    comboAlgo->addItem(QString::fromUtf8("Вставками"));  // индекс 1 -> insertionSort
    comboAlgo->addItem(QString::fromUtf8("Всплытием"));  // индекс 2 -> floatSort

    QPushButton *btnSort = new QPushButton(QString::fromUtf8("Сортировать"));

    top->addWidget(btnAdd);
    top->addWidget(btnEdit);
    top->addWidget(btnDel);
    top->addSpacing(12);
    top->addWidget(btnLoad);
    top->addWidget(btnSave);
    top->addStretch();
    top->addWidget(new QLabel(QString::fromUtf8("Сортировка:")));
    top->addWidget(comboField);
    top->addWidget(comboAlgo);
    top->addWidget(btnSort);
    mainLayout->addLayout(top);

    labelInfo = new QLabel();
    mainLayout->addWidget(labelInfo);

    QHBoxLayout *cols = new QHBoxLayout();

    auto makeColumn = [](const QString &title, QListWidget **listOut) {
        QGroupBox *box = new QGroupBox(title);
        QVBoxLayout *v = new QVBoxLayout(box);
        QListWidget *list = new QListWidget();
        list->setSelectionMode(QAbstractItemView::SingleSelection);
        v->addWidget(list);
        *listOut = list;
        return box;
    };

    cols->addWidget(makeColumn(QString::fromUtf8("Планируется"), &listTodo));
    cols->addWidget(makeColumn(QString::fromUtf8("В работе"), &listDoing));
    cols->addWidget(makeColumn(QString::fromUtf8("Готово"), &listDone));
    mainLayout->addLayout(cols);

    QHBoxLayout *moveRow = new QHBoxLayout();
    QPushButton *btnDoing = new QPushButton(QString::fromUtf8("В работу ->"));
    QPushButton *btnDone = new QPushButton(QString::fromUtf8("Готово ->"));
    QPushButton *btnBack = new QPushButton(QString::fromUtf8("<- Назад"));
    moveRow->addStretch();
    moveRow->addWidget(btnBack);
    moveRow->addWidget(btnDoing);
    moveRow->addWidget(btnDone);
    moveRow->addStretch();
    mainLayout->addLayout(moveRow);

    connect(btnAdd, &QPushButton::clicked, this, &MainWindow::onAdd);
    connect(btnEdit, &QPushButton::clicked, this, &MainWindow::onEdit);
    connect(btnDel, &QPushButton::clicked, this, &MainWindow::onDelete);
    connect(btnDoing, &QPushButton::clicked, this, &MainWindow::onMoveDoing);
    connect(btnDone, &QPushButton::clicked, this, &MainWindow::onMoveDone);
    connect(btnBack, &QPushButton::clicked, this, &MainWindow::onMoveBack);
    connect(btnSort, &QPushButton::clicked, this, &MainWindow::onSort);
    connect(btnSave, &QPushButton::clicked, this, &MainWindow::onSave);
    connect(btnLoad, &QPushButton::clicked, this, &MainWindow::onLoad);

    if (!board.loadFromFile(dataPath)) {
        // демо-данные, если файла ещё нет
        Task a;
        a.title = QString::fromUtf8("Лабораторная по C++");
        a.subject = QString::fromUtf8("Программирование");
        a.deadline = QDate::currentDate().addDays(5);
        a.status = 0;
        a.note = QString::fromUtf8("Канбан-доска");
        board.addTask(a);

        Task b;
        b.title = QString::fromUtf8("Реферат");
        b.subject = QString::fromUtf8("История");
        b.deadline = QDate::currentDate().addDays(-2);
        b.status = 1;
        b.note = QString::fromUtf8("Сдать преподавателю");
        board.addTask(b);

        Task c;
        c.title = QString::fromUtf8("Контрольная");
        c.subject = QString::fromUtf8("Математика");
        c.deadline = QDate::currentDate().addDays(1);
        c.status = 0;
        c.note = "";
        board.addTask(c);

        Task d;
        d.title = QString::fromUtf8("Отчёт по практике");
        d.subject = QString::fromUtf8("Практика");
        d.deadline = QDate::currentDate().addDays(-10);
        d.status = 2;
        d.note = QString::fromUtf8("Уже сдано");
        board.addTask(d);
    }

    refreshLists();
}

void MainWindow::fillList(QListWidget *list, int status)
{
    list->clear();
    QVector<Task> items = board.byStatus(status);
    for (int i = 0; i < items.size(); i++) {
        const Task &t = items[i];
        QString extra;
        if (t.status != 2) {
            int days = t.daysLeft();
            if (days < 0)
                extra = QString::fromUtf8("  [просрочено на %1 дн.]").arg(-days);
            else if (days == 0)
                extra = QString::fromUtf8("  [сегодня]");
            else
                extra = QString::fromUtf8("  [осталось %1 дн.]").arg(days);
        }

        QString text = t.title + "\n"
                + t.subject + "  |  "
                + t.deadline.toString("dd.MM.yyyy")
                + extra;

        QListWidgetItem *item = new QListWidgetItem(text);
        item->setData(Qt::UserRole, t.id);

        if (t.isOverdue())
            item->setBackground(QColor(255, 205, 210));
        else if (t.isSoon())
            item->setBackground(QColor(255, 249, 196));
        else if (t.status == 2)
            item->setBackground(QColor(200, 230, 201));

        list->addItem(item);
    }
}

void MainWindow::refreshLists()
{
    fillList(listTodo, 0);
    fillList(listDoing, 1);
    fillList(listDone, 2);

    labelInfo->setText(QString::fromUtf8(
        "Всего задач: %1    Просрочено: %2    Срок скоро (до 3 дней): %3")
        .arg(board.tasks.size())
        .arg(board.overdueCount())
        .arg(board.soonCount()));
}

QListWidget *MainWindow::activeList() const
{
    if (listDoing->currentItem())
        return listDoing;
    if (listDone->currentItem())
        return listDone;
    return listTodo;
}

int MainWindow::selectedId() const
{
    QListWidget *lists[3] = { listTodo, listDoing, listDone };
    for (int i = 0; i < 3; i++) {
        QListWidgetItem *item = lists[i]->currentItem();
        if (item && lists[i]->hasFocus())
            return item->data(Qt::UserRole).toInt();
    }
    // если фокуса нет — берём любой выделенный элемент
    for (int i = 0; i < 3; i++) {
        QListWidgetItem *item = lists[i]->currentItem();
        if (item)
            return item->data(Qt::UserRole).toInt();
    }
    return -1;
}

bool MainWindow::editTaskDialog(Task &task, const QString &windowTitle)
{
    QDialog dlg(this);
    dlg.setWindowTitle(windowTitle);
    dlg.resize(420, 280);

    QFormLayout *form = new QFormLayout(&dlg);

    QLineEdit *editTitle = new QLineEdit(task.title);
    QLineEdit *editSubject = new QLineEdit(task.subject);
    QDateEdit *editDate = new QDateEdit(task.deadline.isValid() ? task.deadline : QDate::currentDate().addDays(7));
    editDate->setCalendarPopup(true);
    editDate->setDisplayFormat("dd.MM.yyyy");
    QComboBox *editStatus = new QComboBox();
    editStatus->addItem(QString::fromUtf8("Планируется"), 0);
    editStatus->addItem(QString::fromUtf8("В работе"), 1);
    editStatus->addItem(QString::fromUtf8("Готово"), 2);
    editStatus->setCurrentIndex(task.status);
    QTextEdit *editNote = new QTextEdit(task.note);

    form->addRow(QString::fromUtf8("Название:"), editTitle);
    form->addRow(QString::fromUtf8("Предмет:"), editSubject);
    form->addRow(QString::fromUtf8("Срок:"), editDate);
    form->addRow(QString::fromUtf8("Колонка:"), editStatus);
    form->addRow(QString::fromUtf8("Заметка:"), editNote);

    QDialogButtonBox *buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    form->addRow(buttons);
    connect(buttons, &QDialogButtonBox::accepted, &dlg, &QDialog::accept);
    connect(buttons, &QDialogButtonBox::rejected, &dlg, &QDialog::reject);

    if (dlg.exec() != QDialog::Accepted)
        return false;

    if (editTitle->text().trimmed().isEmpty()) {
        QMessageBox::warning(this, QString::fromUtf8("Ошибка"),
                             QString::fromUtf8("Название не должно быть пустым."));
        return false;
    }

    task.title = editTitle->text().trimmed();
    task.subject = editSubject->text().trimmed();
    task.deadline = editDate->date();
    task.status = editStatus->currentData().toInt();
    task.note = editNote->toPlainText().trimmed();
    return true;
}

void MainWindow::onAdd()
{
    Task t;
    t.status = 0;
    t.deadline = QDate::currentDate().addDays(7);
    if (!editTaskDialog(t, QString::fromUtf8("Новая задача")))
        return;
    board.addTask(t);
    refreshLists();
}

void MainWindow::onEdit()
{
    int id = selectedId();
    Task *t = board.findById(id);
    if (!t) {
        QMessageBox::information(this, QString::fromUtf8("Подсказка"),
                                 QString::fromUtf8("Сначала выберите задачу в одной из колонок."));
        return;
    }
    Task copy = *t;
    if (!editTaskDialog(copy, QString::fromUtf8("Изменить задачу")))
        return;
    *t = copy;
    refreshLists();
}

void MainWindow::onDelete()
{
    int id = selectedId();
    if (id < 0) {
        QMessageBox::information(this, QString::fromUtf8("Подсказка"),
                                 QString::fromUtf8("Выберите задачу для удаления."));
        return;
    }
    if (QMessageBox::question(this, QString::fromUtf8("Удаление"),
                              QString::fromUtf8("Удалить выбранную задачу?")) != QMessageBox::Yes)
        return;
    board.removeById(id);
    refreshLists();
}

void MainWindow::onMoveDoing()
{
    Task *t = board.findById(selectedId());
    if (!t)
        return;
    t->status = 1;
    refreshLists();
}

void MainWindow::onMoveDone()
{
    Task *t = board.findById(selectedId());
    if (!t)
        return;
    t->status = 2;
    refreshLists();
}

void MainWindow::onMoveBack()
{
    Task *t = board.findById(selectedId());
    if (!t)
        return;
    if (t->status > 0)
        t->status--;
    refreshLists();
}

// Кнопка «Сортировать»:
// comboAlgo  -> какой алгоритм (Sort.cpp)
// comboField -> по какому полю сравнивать (срок / название / предмет)
void MainWindow::onSort()
{
    board.sortTasks(comboAlgo->currentIndex(), comboField->currentIndex());
    refreshLists();
}

void MainWindow::onSave()
{
    QString path = QFileDialog::getSaveFileName(this, QString::fromUtf8("Сохранить задачи"),
                                                dataPath, QString::fromUtf8("Текст (*.txt)"));
    if (path.isEmpty())
        return;
    if (!board.saveToFile(path)) {
        QMessageBox::warning(this, QString::fromUtf8("Ошибка"),
                             QString::fromUtf8("Не удалось сохранить файл."));
        return;
    }
    dataPath = path;
}

void MainWindow::onLoad()
{
    QString path = QFileDialog::getOpenFileName(this, QString::fromUtf8("Открыть задачи"),
                                                dataPath, QString::fromUtf8("Текст (*.txt)"));
    if (path.isEmpty())
        return;
    if (!board.loadFromFile(path)) {
        QMessageBox::warning(this, QString::fromUtf8("Ошибка"),
                             QString::fromUtf8("Не удалось открыть файл."));
        return;
    }
    dataPath = path;
    refreshLists();
}
