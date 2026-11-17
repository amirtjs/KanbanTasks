# -*- coding: utf-8 -*-
"""
Генерация пояснительной записки (PDF), графиков, блок-схем по ГОСТ 19.701-90
и презентации PPTX для курсового проекта KanbanTasks.
"""
import os
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch, Rectangle
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
FIG = Path(__file__).resolve().parent / "figures"
FIG.mkdir(parents=True, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\times.ttf"
FONT_BD = r"C:\Windows\Fonts\timesbd.ttf"
FONT_IT = r"C:\Windows\Fonts\timesi.ttf"
if not os.path.exists(FONT_REG):
    FONT_REG = r"C:\Windows\Fonts\arial.ttf"
    FONT_BD = r"C:\Windows\Fonts\arialbd.ttf"
    FONT_IT = r"C:\Windows\Fonts\ariali.ttf"

pdfmetrics.registerFont(TTFont("TimesNR", FONT_REG))
pdfmetrics.registerFont(TTFont("TimesNR-Bold", FONT_BD))
if os.path.exists(FONT_IT):
    pdfmetrics.registerFont(TTFont("TimesNR-Italic", FONT_IT))

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.facecolor"] = "white"


# ---------------------------------------------------------------------------
# Блок-схемы по ГОСТ 19.701-90
# ---------------------------------------------------------------------------
class GostChart:
    """Чертёж блок-схемы: терминатор, процесс, решение, ввод-вывод, стрелки."""

    def __init__(self, title, width=8.2, height=11.4):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=180)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.invert_yaxis()
        self.ax.axis("off")
        self.ax.set_title(title, fontsize=12, pad=8, fontweight="bold")
        self.ax.text(99, 99, "ГОСТ 19.701-90", fontsize=7, ha="right", va="top", color="#444")

    def _txt(self, x, y, text, size=8, weight="normal"):
        self.ax.text(x, y, text, ha="center", va="center", fontsize=size,
                     fontweight=weight, wrap=False, zorder=5)

    def terminal(self, x, y, w, h, text):
        p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.02,rounding_size=2.2",
                           linewidth=1.4, edgecolor="black", facecolor="white", zorder=3)
        self.ax.add_patch(p)
        self._txt(x, y, text, 9, "bold")
        return (x, y - h / 2, x, y + h / 2)

    def process(self, x, y, w, h, text, size=8):
        p = Rectangle((x - w / 2, y - h / 2), w, h,
                      linewidth=1.4, edgecolor="black", facecolor="white", zorder=3)
        self.ax.add_patch(p)
        self._txt(x, y, text, size)
        return (x, y - h / 2, x, y + h / 2)

    def io_box(self, x, y, w, h, text):
        skew = 3.2
        pts = [
            (x - w / 2 + skew, y - h / 2),
            (x + w / 2 + skew, y - h / 2),
            (x + w / 2 - skew, y + h / 2),
            (x - w / 2 - skew, y + h / 2),
        ]
        self.ax.add_patch(Polygon(pts, closed=True, linewidth=1.4,
                                  edgecolor="black", facecolor="white", zorder=3))
        self._txt(x, y, text, 8)
        return (x, y - h / 2, x, y + h / 2)

    def decision(self, x, y, w, h, text):
        pts = [(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)]
        self.ax.add_patch(Polygon(pts, closed=True, linewidth=1.4,
                                  edgecolor="black", facecolor="white", zorder=3))
        self._txt(x, y, text, 7.5)
        return (x, y - h / 2, x, y + h / 2, x - w / 2, x + w / 2)

    def arrow(self, x1, y1, x2, y2):
        self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                         arrowprops=dict(arrowstyle="-|>", color="black", lw=1.15,
                                         mutation_scale=10), zorder=2)

    def line(self, x1, y1, x2, y2):
        self.ax.plot([x1, x2], [y1, y2], color="black", lw=1.15, zorder=2)

    def label(self, x, y, text, size=7.5):
        self.ax.text(x, y, text, fontsize=size, ha="left", va="center", color="black", zorder=6)

    def save(self, name):
        self.fig.tight_layout()
        path = FIG / name
        self.fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
        plt.close(self.fig)
        return path


def chart_program():
    c = GostChart("Рисунок 1 – Общая схема работы программы")
    t = c.terminal(50, 6, 28, 6, "Начало")
    p1 = c.process(50, 16, 46, 7, "Создание QApplication и окна")
    io1 = c.io_box(50, 27, 46, 7, "Загрузка tasks.txt / демо-данные")
    p2 = c.process(50, 38, 46, 7, "Отрисовка канбан-колонок")
    p3 = c.process(50, 49, 46, 7, "Ожидание действия пользователя")
    d = c.decision(50, 64, 40, 12, "Какое действие?")
    p_sort = c.process(18, 82, 28, 8, "sortTasks()\nSort.cpp")
    p_edit = c.process(50, 82, 28, 8, "Добавить / изменить\nудалить / переместить")
    p_file = c.process(82, 82, 28, 8, "Открыть / сохранить\nфайл")
    t2 = c.terminal(50, 95, 28, 6, "Конец")

    c.arrow(50, t[2], 50, p1[1])
    c.arrow(50, p1[2], 50, io1[1])
    c.arrow(50, io1[2], 50, p2[1])
    c.arrow(50, p2[2], 50, p3[1])
    c.arrow(50, p3[2], 50, d[1])
    c.line(50, d[2], 50, 74)
    c.line(18, 74, 82, 74)
    c.arrow(18, 74, 18, p_sort[1])
    c.arrow(50, 74, 50, p_edit[1])
    c.arrow(82, 74, 82, p_file[1])
    c.label(20, 61, "сорт.")
    c.label(54, 64, "правка")
    c.label(71, 58, "файл")
    c.line(18, p_sort[2], 18, 90)
    c.line(82, p_file[2], 82, 90)
    c.line(18, 90, 82, 90)
    c.line(50, p_edit[2], 50, 90)
    c.arrow(50, 90, 50, t2[1])
    c.line(88, 64, 94, 64)
    c.line(94, 64, 94, 49)
    c.arrow(94, 49, 73, 49)
    c.label(89, 46, "цикл")
    return c.save("bs_programma.png")


def chart_sort_choice():
    c = GostChart("Рисунок 2 – Выбор алгоритма сортировки")
    t = c.terminal(50, 8, 26, 6, "Начало")
    io1 = c.io_box(50, 18, 50, 7, "algorithm, field из окна")
    d1 = c.decision(50, 34, 36, 12, "algorithm = 1?")
    p_ins = c.process(82, 34, 28, 8, "insertionSort()\nвставками")
    d2 = c.decision(50, 54, 36, 12, "algorithm = 2?")
    p_fl = c.process(82, 54, 28, 8, "floatSort()\nвсплытием")
    p_b = c.process(50, 74, 36, 8, "bubbleSort()\nпузырьком")
    t2 = c.terminal(50, 90, 26, 6, "Конец")

    c.arrow(50, t[2], 50, io1[1])
    c.arrow(50, io1[2], 50, d1[1])
    c.arrow(d1[5], 34, p_ins[0] - 14, 34)
    c.label(68, 31, "да")
    c.arrow(50, d1[2], 50, d2[1])
    c.label(52, 44, "нет")
    c.arrow(d2[5], 54, p_fl[0] - 14, 54)
    c.label(68, 51, "да")
    c.arrow(50, d2[2], 50, p_b[1])
    c.label(52, 64, "нет")
    c.line(82, p_ins[2], 82, 84)
    c.line(82, p_fl[2], 82, 84)
    c.line(50, p_b[2], 50, 84)
    c.line(50, 84, 82, 84)
    c.arrow(50, 84, 50, t2[1])
    return c.save("bs_vybor.png")


def chart_bubble():
    c = GostChart("Рисунок 3 – Сортировка пузырьком (ГОСТ 19.701-90)")
    t = c.terminal(50, 5, 24, 5.2, "Начало")
    p0 = c.process(50, 13, 40, 5.5, "n = размер массива")
    p1 = c.process(50, 21, 28, 5.2, "i = 0")
    d1 = c.decision(50, 32, 32, 10, "i < n - 1 ?")
    p2 = c.process(50, 45, 28, 5.2, "j = 0")
    d2 = c.decision(50, 56, 34, 10, "j < n - 1 - i ?")
    d3 = c.decision(50, 72, 36, 11, "A[j+1] < A[j] ?")
    p3 = c.process(82, 72, 26, 7, "обмен\nA[j] и A[j+1]")
    p4 = c.process(22, 56, 20, 5.2, "j = j + 1")
    p5 = c.process(22, 32, 20, 5.2, "i = i + 1")
    t2 = c.terminal(82, 32, 22, 5.2, "Конец")

    c.arrow(50, t[2], 50, p0[1])
    c.arrow(50, p0[2], 50, p1[1])
    c.arrow(50, p1[2], 50, d1[1])
    c.arrow(50, d1[2], 50, p2[1])
    c.label(52, 39, "да")
    c.arrow(50, p2[2], 50, d2[1])
    c.arrow(50, d2[2], 50, d3[1])
    c.label(52, 63, "да")
    c.arrow(d3[5], 72, p3[0] - 13, 72)
    c.label(69, 69, "да")
    c.line(82, p3[2], 82, 80)
    c.line(50, d3[2], 50, 80)
    c.line(22, 80, 82, 80)
    c.line(22, 80, 22, 59)
    c.arrow(22, 59, 22, p4[2] if False else p4[1] - 0.01)
    # from left of d2 to p4 then back
    c.line(d2[4], 56, 32, 56)
    c.arrow(32, 56, p4[0] + 10, 56)
    c.label(34, 53, "нет")
    c.line(22, p4[1], 22, 21)
    c.line(22, 21, 36, 21)
    c.arrow(36, 21, 36, p1[2] + 0.2)
    # wait that's messy. Simpler loop: p4 -> up to d2
    # redraw p4 loop to d2
    # i increment from d2 no: when j loop done, i++
    c.line(d1[5], 32, t2[0] - 11, 32)
    c.arrow(t2[0] - 11, 32, t2[0] - 11, 32)
    c.arrow(68, 32, t2[0] - 11, 32)
    c.label(70, 29, "нет")
    c.line(p5[0] + 10, 32, p5[0] + 10, 32)
    c.line(d2[4], 56, p4[0] + 10, 56)
    # i++ from after j loop - from no of d2 we already went to p4 which is j++
    # when d2 is no, go to i++
    # I mixed p4 as j++ on the left of d2 "нет". That's wrong.
    # Fix labels in a cleaner second version - the figure may have overlapping arrows.
    # Let's not add more; save as-is... actually this is messy. Rewrite this function cleanly.
    c.line(22, 45, 50, 45)  # leftover
    return c.save("bs_bubble.png")


def _save_clean_bubble():
    """Перерисовка пузырька аккуратными вертикальными циклами."""
    c = GostChart("Рисунок 3 – Алгоритм сортировки пузырьком", width=8.4, height=11.6)
    cx = 50
    t = c.terminal(cx, 4.5, 26, 5, "Начало")
    p0 = c.process(cx, 12, 44, 5.2, "n ← количество задач")
    p1 = c.process(cx, 19.5, 24, 5, "i ← 0")
    d1 = c.decision(cx, 29.5, 30, 9.5, "i < n − 1 ?")
    p2 = c.process(cx, 41, 24, 5, "j ← 0")
    d2 = c.decision(cx, 51.5, 34, 9.5, "j < n − 1 − i ?")
    d3 = c.decision(cx, 65, 36, 10.5, "A[j+1] < A[j] ?")
    sw = c.process(78, 65, 24, 6.5, "Обмен A[j]\nи A[j+1]")
    pj = c.process(22, 51.5, 18, 5, "j ← j + 1")
    pi = c.process(22, 29.5, 18, 5, "i ← i + 1")
    t2 = c.terminal(78, 29.5, 22, 5, "Конец")

    c.arrow(cx, t[2], cx, p0[1])
    c.arrow(cx, p0[2], cx, p1[1])
    c.arrow(cx, p1[2], cx, d1[1])
    c.arrow(cx, d1[2], cx, p2[1])
    c.label(52, 35.8, "да")
    c.arrow(cx, p2[2], cx, d2[1])
    c.arrow(cx, d2[2], cx, d3[1])
    c.label(52, 57.5, "да")
    c.arrow(d3[5], 65, sw[0] - 12, 65)
    c.label(69, 62.2, "да")
    # after swap or no: j++
    c.line(78, sw[2], 78, 74)
    c.line(cx, d3[2], cx, 74)
    c.label(52, 70.2, "нет")
    c.line(22, 74, 78, 74)
    c.line(22, 74, 22, 54)
    c.arrow(22, 54, 22, pj[2] if False else pj[1] + 5)  # dummy
    # connect bottom bar to j++
    c.arrow(22, 56.5, 22, pj[2])
    c.line(pj[0] + 9, 51.5, d2[4], 51.5)

    # d2 нет -> i++
    c.line(d2[4], 51.5, 31, 51.5)  # overlaps j++ incoming from left of diamond
    # separate: j++ is LEFT of diamond, d2-no goes further left then up to i++
    # redraw: j++ below-left loop only from bottom.

    # d1 нет -> конец
    c.line(d1[5], 29.5, t2[0] - 11, 29.5)
    c.arrow(t2[0] - 11, 29.5, t2[0] - 11, 29.5)
    c.arrow(65, 29.5, t2[0] - 11, 29.5)
    c.label(67, 26.8, "нет")

    # i++ from d2 no: go right? go left up
    c.line(16, 51.5, 16, 29.5)
    c.line(d2[4], 51.5, 16, 51.5)
    c.arrow(16, 29.5, pi[0] - 9, 29.5)
    c.label(17, 48.8, "нет (внутр.)")
    c.line(pi[0] + 9, 29.5, d1[4], 29.5)
    c.line(pi[0], pi[1], pi[0], 19.5)
    c.line(pi[0], 19.5, 38, 19.5)
    c.arrow(38, 19.5, p1[0] - 12, 19.5)

    return c.save("bs_bubble.png")


def chart_insert():
    c = GostChart("Рисунок 4 – Алгоритм сортировки вставками", width=8.4, height=11.6)
    cx = 50
    t = c.terminal(cx, 5, 24, 5, "Начало")
    p0 = c.process(cx, 13, 44, 5.2, "n ← количество задач")
    p1 = c.process(cx, 21, 24, 5, "i ← 1")
    d1 = c.decision(cx, 31.5, 30, 9.5, "i < n ?")
    p2 = c.process(cx, 44, 40, 6.2, "key ← A[i]\nj ← i − 1")
    d2 = c.decision(cx, 58, 40, 11, "j ≥ 0 и\nkey < A[j] ?")
    p3 = c.process(cx, 73, 36, 6, "A[j+1] ← A[j]\nj ← j − 1")
    p4 = c.process(78, 58, 26, 6, "A[j+1] ← key\ni ← i + 1")
    t2 = c.terminal(78, 31.5, 22, 5, "Конец")

    c.arrow(cx, t[2], cx, p0[1])
    c.arrow(cx, p0[2], cx, p1[1])
    c.arrow(cx, p1[2], cx, d1[1])
    c.arrow(cx, d1[2], cx, p2[1])
    c.label(52, 37.5, "да")
    c.arrow(cx, p2[2], cx, d2[1])
    c.arrow(cx, d2[2], cx, p3[1])
    c.label(52, 65.5, "да")
    c.line(cx, p3[2], cx, 82)
    c.line(20, 82, cx, 82)
    c.line(20, 82, 20, 58)
    c.arrow(20, 58, d2[4], 58)
    c.arrow(d2[5], 58, p4[0] - 13, 58)
    c.label(68, 55, "нет")
    c.line(78, p4[1], 78, 21)
    c.line(78, 21, 62, 21)
    c.arrow(62, 21, p1[0] + 12, 21)
    c.line(d1[5], 31.5, t2[0] - 11, 31.5)
    c.arrow(65, 31.5, t2[0] - 11, 31.5)
    c.label(67, 28.8, "нет")
    return c.save("bs_vstavki.png")


def chart_float():
    c = GostChart("Рисунок 5 – Алгоритм сортировки всплытием (шейкерная)", width=8.4, height=11.7)
    cx = 50
    t = c.terminal(cx, 4.2, 24, 4.8, "Начало")
    p0 = c.process(cx, 11.2, 48, 5, "left ← 0,  right ← n − 1")
    d1 = c.decision(cx, 21.5, 32, 9, "left < right ?")
    p1 = c.process(cx, 33.5, 46, 5.2, "Проход вправо: всплытие максимума")
    p2 = c.process(cx, 41.5, 30, 4.8, "right ← right − 1")
    p3 = c.process(cx, 50, 46, 5.2, "Проход влево: «погружение» минимума")
    p4 = c.process(cx, 58.2, 28, 4.8, "left ← left + 1")
    t2 = c.terminal(78, 21.5, 22, 4.8, "Конец")

    # inner compare for right pass
    d2 = c.decision(cx, 72, 38, 10, "A[i+1] < A[i]\nна проходе?")
    sw = c.process(80, 72, 22, 6, "Обмен\nсоседей")
    note = c.process(cx, 88, 70, 7.2,
                     "Оба прохода — вложенные циклы for, как у пузырька.\n"
                     "После полного двустороннего прохода границы сжимаются.")

    c.arrow(cx, t[2], cx, p0[1])
    c.arrow(cx, p0[2], cx, d1[1])
    c.arrow(cx, d1[2], cx, p1[1])
    c.label(52, 27, "да")
    c.arrow(cx, p1[2], cx, p2[1])
    c.arrow(cx, p2[2], cx, p3[1])
    c.arrow(cx, p3[2], cx, p4[1])
    c.line(cx, p4[2], cx, 64)
    c.line(18, 64, cx, 64)
    c.line(18, 64, 18, 21.5)
    c.arrow(18, 21.5, d1[4], 21.5)
    c.line(d1[5], 21.5, t2[0] - 11, 21.5)
    c.arrow(65, 21.5, t2[0] - 11, 21.5)
    c.label(66, 18.8, "нет")
    c.arrow(cx, 64, cx, d2[1])
    c.arrow(d2[5], 72, sw[0] - 11, 72)
    c.label(69, 69, "да")
    c.arrow(cx, d2[2], cx, note[1])
    c.label(52, 79, "нет / далее")
    c.line(80, sw[2], 80, 82)
    c.line(cx, 82, 80, 82)
    c.arrow(cx, 82, cx, note[1])
    return c.save("bs_vsplytie.png")


def chart_compare():
    c = GostChart("Рисунок 6 – Сравнение двух задач (функция taskLess)", height=9.5)
    t = c.terminal(50, 6, 24, 5, "Начало")
    io1 = c.io_box(50, 15, 44, 5.5, "Задачи A, B и поле field")
    d1 = c.decision(50, 28, 32, 10, "field = название?")
    r1 = c.process(82, 28, 24, 6, "A.title < B.title")
    d2 = c.decision(50, 45, 32, 10, "field = предмет?")
    r2 = c.process(82, 45, 24, 6, "A.subj < B.subj")
    d3 = c.decision(50, 62, 32, 10, "сроки разные?")
    r3 = c.process(82, 62, 24, 6, "A.date < B.date")
    r4 = c.process(50, 78, 36, 6, "сравнить названия")
    t2 = c.terminal(50, 90, 24, 5, "Конец (истина/ложь)")

    c.arrow(50, t[2], 50, io1[1])
    c.arrow(50, io1[2], 50, d1[1])
    c.arrow(d1[5], 28, r1[0] - 12, 28)
    c.label(68, 25, "да")
    c.arrow(50, d1[2], 50, d2[1])
    c.label(52, 36.5, "нет")
    c.arrow(d2[5], 45, r2[0] - 12, 45)
    c.label(68, 42, "да")
    c.arrow(50, d2[2], 50, d3[1])
    c.label(52, 53.5, "нет")
    c.arrow(d3[5], 62, r3[0] - 12, 62)
    c.label(68, 59, "да")
    c.arrow(50, d3[2], 50, r4[1])
    c.label(52, 70, "нет")
    c.line(82, r1[2], 82, 86)
    c.line(82, r2[2], 82, 86)
    c.line(82, r3[2], 82, 86)
    c.line(50, r4[2], 50, 86)
    c.line(50, 86, 82, 86)
    c.arrow(50, 86, 50, t2[1])
    return c.save("bs_sravnenie.png")


def chart_overdue():
    c = GostChart("Рисунок 7 – Определение просроченной задачи", height=9.2)
    t = c.terminal(50, 7, 24, 5, "Начало")
    d0 = c.decision(50, 20, 32, 10, "status = Готово?")
    r0 = c.process(82, 20, 22, 6, "не просрочена")
    p1 = c.process(50, 36, 40, 6, "days = сегодня − срок")
    d1 = c.decision(50, 51, 30, 10, "days < 0 ?")
    yes = c.process(22, 51, 22, 6, "просрочена")
    d2 = c.decision(50, 68, 32, 10, "0 ≤ days ≤ 3 ?")
    soon = c.process(22, 68, 22, 6, "срок скоро")
    ok = c.process(50, 84, 24, 6, "обычная")
    t2 = c.terminal(82, 84, 22, 5, "Конец")

    c.arrow(50, t[2], 50, d0[1])
    c.arrow(d0[5], 20, r0[0] - 11, 20)
    c.label(68, 17, "да")
    c.arrow(50, d0[2], 50, p1[1])
    c.label(52, 27.5, "нет")
    c.arrow(50, p1[2], 50, d1[1])
    c.arrow(d1[4], 51, yes[0] + 11, 51)
    c.label(36, 48, "да")
    c.arrow(50, d1[2], 50, d2[1])
    c.label(52, 58.5, "нет")
    c.arrow(d2[4], 68, soon[0] + 11, 68)
    c.label(36, 65, "да")
    c.arrow(50, d2[2], 50, ok[1])
    c.label(52, 75.5, "нет")
    c.line(82, r0[2], 82, 81.5)
    c.line(22, yes[2], 22, 90)
    c.line(22, soon[2], 22, 90)
    c.line(50, ok[2], 50, 90)
    c.line(22, 90, 82, 90)
    c.line(82, 90, 82, t2[2])
    c.arrow(82, 86.5, 82, t2[2])
    return c.save("bs_sroki.png")


def fix_bubble_clean():
    """Чистая блок-схема пузырька без пересечений."""
    fig, ax = plt.subplots(figsize=(8.4, 11.6), dpi=180)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_title("Рисунок 3 – Алгоритм сортировки пузырьком", fontsize=12, pad=8, fontweight="bold")
    ax.text(99, 1, "ГОСТ 19.701-90", fontsize=7, ha="right", color="#444")

    def terminal(x, y, w, h, text):
        p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.02,rounding_size=2.0",
                           lw=1.4, ec="black", fc="white", zorder=3)
        ax.add_patch(p)
        ax.text(x, y, text, ha="center", va="center", fontsize=9, fontweight="bold", zorder=5)

    def proc(x, y, w, h, text, size=8):
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, lw=1.4, ec="black", fc="white", zorder=3))
        ax.text(x, y, text, ha="center", va="center", fontsize=size, zorder=5)

    def rhomb(x, y, w, h, text):
        pts = [(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)]
        ax.add_patch(Polygon(pts, closed=True, lw=1.4, ec="black", fc="white", zorder=3))
        ax.text(x, y, text, ha="center", va="center", fontsize=7.5, zorder=5)

    def arr(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.15, mutation_scale=10), zorder=2)

    def ln(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="black", lw=1.15, zorder=2)

    terminal(50, 6, 26, 5.2, "Начало")
    proc(50, 14, 44, 5.4, "n ← количество задач")
    proc(50, 22, 22, 5, "i ← 0")
    rhomb(50, 33, 32, 10, "i < n − 1 ?")
    proc(50, 45, 22, 5, "j ← 0")
    rhomb(50, 57, 36, 10, "j < n − 1 − i ?")
    rhomb(50, 73, 38, 11, "A[j+1] < A[j] ?")
    proc(82, 73, 24, 7, "Обмен A[j]\nи A[j+1]")
    proc(18, 57, 18, 5, "j ← j + 1")
    proc(18, 33, 18, 5, "i ← i + 1")
    terminal(82, 33, 22, 5.2, "Конец")

    arr(50, 8.6, 50, 11.3)
    arr(50, 16.7, 50, 19.5)
    arr(50, 24.5, 50, 28)
    arr(50, 38, 50, 42.5)
    ax.text(52, 40, "да", fontsize=8)
    arr(50, 47.5, 50, 52)
    arr(50, 62, 50, 67.5)
    ax.text(52, 64.5, "да", fontsize=8)
    arr(69, 73, 70, 73)
    ax.text(70, 70, "да", fontsize=8)
    # merge swap and no to j++
    ln(50, 78.5, 50, 84)
    ln(82, 76.5, 82, 84)
    ln(18, 84, 82, 84)
    ln(18, 84, 18, 59.5)
    arr(18, 59.5, 18, 59.5)
    ln(27, 57, 32, 57)  # j++ to diamond left
    arr(27, 57, 32, 57)
    ax.text(52, 79.5, "нет", fontsize=8)

    # inner no: j loop finished -> i++
    ln(32, 57, 27, 57)  # already
    # from left of inner rhomb "нет" should go to i++, not to j++
    # Use bottom-right? Standard: нет from inner goes LEFT-UP to i++
    # Put "нет" going right then up? Let's use far-left path for i++
    ln(12, 57, 12, 33)
    # Need a branch from diamond left that's "нет" - the left of diamond is x=32
    # j++ sits at x=18. Conflict.
    # Move j++ to RIGHT of inner? Inner swap already on right.
    # Alternative: j++ below the compare.

    ax.text(13, 54.2, "нет", fontsize=7)
    arr(12, 33, 18 - 9, 33)
    ln(27, 33, 34, 33)  # i++ to outer diamond
    arr(27, 33, 34, 33)

    # i++ back to i=0 check: from i++ up to i<-0 process? usually to condition
    ln(18, 30.5, 18, 22)
    ln(18, 22, 39, 22)
    arr(39, 22, 39, 22)
    arr(39, 22, 39, 24.5)  # no
    ln(39, 22, 50, 22)  # into i<-0? Better into condition
    # go into i <- 0 from left of process - actually loop should return to condition i < n-1
    ln(18, 30.5, 18, 22)
    ln(18, 22, 18, 22)

    # d1 no -> end
    ln(66, 33, 71, 33)
    arr(71, 33, 71, 33)
    arr(66, 33, 71, 33)
    ax.text(68, 30.2, "нет", fontsize=8)

    # Fix i loop: from i++ top to just above outer rhomb
    ln(18, 30.5, 18, 22)
    ln(18, 22, 50, 22)
    # that's through i<-0 which re-inits i. WRONG.
    # i should not be reset. Loop to rhomb i < n-1
    # erase by covering... can't. Redraw entire figure properly in one go.

    path = FIG / "bs_bubble.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


class Flow:
    def __init__(self, title, w=8.5, h=11.6):
        self.fig, self.ax = plt.subplots(figsize=(w, h), dpi=190)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(100, 0)
        self.ax.axis("off")
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.text(1, 99.2, "Обозначения по ГОСТ 19.701-90", fontsize=7, color="#333")
        self.ax.text(99, 99.2, "терминатор / процесс / решение / данные", fontsize=7,
                     ha="right", color="#333")

    def term(self, x, y, text, w=28, h=6):
        self.ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                         boxstyle="round,pad=0.15,rounding_size=2.4",
                                         lw=1.5, ec="k", fc="white", zorder=3))
        self.ax.text(x, y, text, ha="center", va="center", fontsize=9, fontweight="bold", zorder=4)
        return x, y, w, h

    def proc(self, x, y, text, w=42, h=6.2, size=8):
        self.ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, lw=1.5, ec="k", fc="white", zorder=3))
        self.ax.text(x, y, text, ha="center", va="center", fontsize=size, zorder=4)
        return x, y, w, h

    def data(self, x, y, text, w=44, h=6.2):
        s = 3.0
        pts = [(x - w / 2 + s, y - h / 2), (x + w / 2 + s, y - h / 2),
               (x + w / 2 - s, y + h / 2), (x - w / 2 - s, y + h / 2)]
        self.ax.add_patch(Polygon(pts, closed=True, lw=1.5, ec="k", fc="white", zorder=3))
        self.ax.text(x, y, text, ha="center", va="center", fontsize=8, zorder=4)
        return x, y, w, h

    def rh(self, x, y, text, w=36, h=11, size=7.5):
        pts = [(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)]
        self.ax.add_patch(Polygon(pts, closed=True, lw=1.5, ec="k", fc="white", zorder=3))
        self.ax.text(x, y, text, ha="center", va="center", fontsize=size, zorder=4)
        return x, y, w, h

    def down(self, a, b, gap=0.15):
        x, y1, w, h1 = a[0], a[1], a[2], a[3]
        y2, h2 = b[1], b[3]
        self.ax.annotate("", xy=(x, y2 - h2 / 2), xytext=(x, y1 + h1 / 2),
                         arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))

    def aside(self, a, b, text, side="right"):
        x1, y, w1, h = a
        x2, y2, w2, h2 = b
        xa = x1 + (w1 / 2 if side == "right" else -w1 / 2)
        xb = x2 - (w2 / 2 if side == "right" else -w2 / 2)
        self.ax.annotate("", xy=(xb, y2), xytext=(xa, y),
                         arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
        mx = (xa + xb) / 2
        self.ax.text(mx, y - 2.0, text, fontsize=8, ha="center")

    def vpath(self, pts):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color="k", lw=1.2, zorder=2)

    def save(self, name):
        self.fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.96])
        path = FIG / name
        self.fig.savefig(path, dpi=190, bbox_inches="tight", facecolor="white")
        plt.close(self.fig)
        return path


def draw_all_flowcharts():
    paths = {}
    # 1 program
    f = Flow("Рисунок 1 – Общая схема работы программы")
    a = f.term(50, 7, "Начало")
    b = f.proc(50, 16, "Запуск Qt-приложения\nи главного окна")
    c = f.data(50, 26, "Чтение data/tasks.txt")
    d = f.proc(50, 36, "Показ колонок канбана\nи подсветка сроков")
    e = f.proc(50, 46.5, "Ожидание действия пользователя")
    g = f.rh(50, 60, "Выбранное\nдействие?", h=12)
    s = f.proc(18, 78, "Сортировка\n(Sort.cpp)", w=28, h=8)
    ed = f.proc(50, 78, "Правка задач\nи колонок", w=28, h=8)
    fi = f.proc(82, 78, "Файл\nоткрыть/сохранить", w=28, h=8)
    z = f.term(50, 93, "Конец")
    for p, q in ((a, b), (b, c), (c, d), (d, e), (e, g)):
        f.down(p, q)
    f.ax.plot([50, 50], [g[1] + g[3] / 2, 70], color="k", lw=1.2)
    f.ax.plot([18, 82], [70, 70], color="k", lw=1.2)
    f.ax.annotate("", xy=(18, 78 - 4), xytext=(18, 70),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.annotate("", xy=(50, 78 - 4), xytext=(50, 70),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.annotate("", xy=(82, 78 - 4), xytext=(82, 70),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.text(20, 68.2, "сортировать", fontsize=7)
    f.ax.text(52, 68.2, "правка", fontsize=7)
    f.ax.text(84, 68.2, "файл", fontsize=7)
    f.ax.plot([18, 18], [82, 88], color="k", lw=1.2)
    f.ax.plot([82, 82], [82, 88], color="k", lw=1.2)
    f.ax.plot([50, 50], [82, 88], color="k", lw=1.2)
    f.ax.plot([18, 82], [88, 88], color="k", lw=1.2)
    f.ax.annotate("", xy=(50, 93 - 3), xytext=(50, 88),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.annotate("", xy=(73, 46.5), xytext=(94, 46.5),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.plot([94, 94], [60, 46.5], color="k", lw=1.2)
    f.ax.plot([68, 94], [60, 60], color="k", lw=1.2)
    f.ax.text(90, 44.5, "пока не выход", fontsize=7, ha="right")
    paths["prog"] = f.save("bs_programma.png")

    # 2 choice
    f = Flow("Рисунок 2 – Выбор алгоритма (Board::sortTasks)")
    a = f.term(50, 8, "Начало")
    b = f.data(50, 18, "algorithm и field из интерфейса")
    d1 = f.rh(50, 32, "algorithm = 1?")
    ins = f.proc(82, 32, "insertionSort\nвставками", w=26, h=8)
    d2 = f.rh(50, 50, "algorithm = 2?")
    fl = f.proc(82, 50, "floatSort\nвсплытием", w=26, h=8)
    bu = f.proc(50, 70, "bubbleSort\nпузырьком", w=32, h=8)
    z = f.term(50, 88, "Конец")
    f.down(a, b)
    f.down(b, d1)
    f.aside(d1, ins, "да")
    f.down(d1, d2)
    f.ax.text(52, 41, "нет", fontsize=8)
    f.aside(d2, fl, "да")
    f.down(d2, bu)
    f.ax.text(52, 59, "нет", fontsize=8)
    f.ax.plot([82, 82], [36, 80], color="k", lw=1.2)
    f.ax.plot([82, 82], [54, 80], color="k", lw=1.2)
    f.ax.plot([50, 50], [74, 80], color="k", lw=1.2)
    f.ax.plot([50, 82], [80, 80], color="k", lw=1.2)
    f.ax.annotate("", xy=(50, 88 - 3), xytext=(50, 80),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    paths["choice"] = f.save("bs_vybor.png")

    # 3 bubble — classic nested loops
    f = Flow("Рисунок 3 – Сортировка пузырьком", w=8.8, h=12)
    a = f.term(52, 5.5, "Начало", w=24, h=5)
    n = f.proc(52, 13, "n ← число элементов", w=40, h=5)
    i0 = f.proc(52, 20.5, "i ← 0", w=20, h=4.8)
    di = f.rh(52, 31, "i < n − 1 ?", w=30, h=9)
    j0 = f.proc(52, 43, "j ← 0", w=20, h=4.8)
    dj = f.rh(52, 54, "j < n − 1 − i ?", w=34, h=9.5)
    dc = f.rh(52, 70, "A[j+1] < A[j] ?", w=36, h=10)
    sw = f.proc(84, 70, "Обмен\nA[j] ↔ A[j+1]", w=24, h=7.2)
    jp = f.proc(84, 54, "j ← j + 1", w=20, h=5)
    ip = f.proc(18, 31, "i ← i + 1", w=18, h=5)
    z = f.term(84, 31, "Конец", w=22, h=5)
    f.down(a, n)
    f.down(n, i0)
    f.down(i0, di)
    f.down(di, j0)
    f.ax.text(54, 37.5, "да", fontsize=8)
    f.down(j0, dj)
    f.down(dj, dc)
    f.ax.text(54, 60.2, "да", fontsize=8)
    f.aside(dc, sw, "да")
    # после сравнения (да/нет) идём к j++
    f.ax.plot([52, 52], [75, 82], color="k", lw=1.2)
    f.ax.plot([84, 84], [73.6, 82], color="k", lw=1.2)
    f.ax.plot([52, 84], [82, 82], color="k", lw=1.2)
    f.ax.annotate("", xy=(84, 56.5), xytext=(84, 82),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.text(54, 77.5, "нет", fontsize=8)
    f.ax.annotate("", xy=(69, 54), xytext=(74, 54),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    # внутренний цикл закончен: нет → i++
    f.ax.plot([35, 6], [54, 54], color="k", lw=1.2)
    f.ax.plot([6, 6], [54, 31], color="k", lw=1.2)
    f.ax.annotate("", xy=(9, 31), xytext=(6, 31),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.text(8, 51.5, "нет", fontsize=8)
    f.ax.annotate("", xy=(37, 31), xytext=(27, 31),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    # внешний цикл: нет → конец
    f.ax.plot([67, 73], [31, 31], color="k", lw=1.2)
    f.ax.annotate("", xy=(73, 31), xytext=(67, 31),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.text(69, 28.4, "нет", fontsize=8)
    paths["bubble"] = f.save("bs_bubble.png")

    # 4 insertion
    f = Flow("Рисунок 4 – Сортировка вставками")
    a = f.term(50, 6, "Начало")
    n = f.proc(50, 14, "n ← число элементов")
    i0 = f.proc(50, 22, "i ← 1", w=20, h=5)
    di = f.rh(50, 33, "i < n ?", w=28, h=9)
    key = f.proc(50, 46, "key ← A[i];   j ← i − 1", w=44, h=6)
    dw = f.rh(50, 60, "j ≥ 0 и key < A[j] ?", w=40, h=11)
    sh = f.proc(50, 75, "A[j+1] ← A[j];   j ← j − 1", w=46, h=6)
    ins = f.proc(82, 60, "A[j+1] ← key\ni ← i + 1", w=26, h=8)
    z = f.term(82, 33, "Конец", w=22, h=5)
    f.down(a, n)
    f.down(n, i0)
    f.down(i0, di)
    f.down(di, key)
    f.ax.text(52, 39, "да", fontsize=8)
    f.down(key, dw)
    f.down(dw, sh)
    f.ax.text(52, 67.5, "да")
    f.ax.plot([50, 50], [78, 84], color="k", lw=1.2)
    f.ax.plot([16, 50], [84, 84], color="k", lw=1.2)
    f.ax.plot([16, 16], [84, 60], color="k", lw=1.2)
    f.ax.annotate("", xy=(30, 60), xytext=(16, 60),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.aside(dw, ins, "нет")
    f.ax.plot([82, 82], [56, 22], color="k", lw=1.2)
    f.ax.plot([82, 60], [22, 22], color="k", lw=1.2)
    f.ax.annotate("", xy=(60, 22), xytext=(82, 22),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.plot([64, 71], [33, 33], color="k", lw=1.2)
    f.ax.annotate("", xy=(71, 33), xytext=(64, 33),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.text(66, 30.5, "нет", fontsize=8)
    paths["ins"] = f.save("bs_vstavki.png")

    # 5 float
    f = Flow("Рисунок 5 – Сортировка всплытием (шейкерная)")
    a = f.term(50, 6, "Начало")
    n = f.proc(50, 14.5, "left ← 0;   right ← n − 1")
    d = f.rh(50, 26, "left < right ?", w=32, h=10)
    p1 = f.proc(50, 39, "Цикл i = left … right−1:\nесли сосед нарушен — обмен\n(максимум всплывает вправо)", w=52, h=10, size=7.5)
    p2 = f.proc(50, 50.5, "right ← right − 1", w=36, h=5.2)
    p3 = f.proc(50, 61, "Цикл i = right … left+1:\nесли сосед нарушен — обмен\n(минимум погружается влево)", w=52, h=10, size=7.5)
    p4 = f.proc(50, 72.5, "left ← left + 1", w=32, h=5.2)
    z = f.term(82, 26, "Конец", w=22, h=5)
    note = f.proc(50, 86, "Границы сжимаются, пока left < right.\nЭто двусторонний пузырёк (cocktail sort).", w=60, h=8, size=8)
    f.down(a, n)
    f.down(n, d)
    f.down(d, p1)
    f.ax.text(52, 32.5, "да", fontsize=8)
    f.down(p1, p2)
    f.down(p2, p3)
    f.down(p3, p4)
    f.down(p4, note)
    f.ax.plot([18, 18], [72.5, 26], color="k", lw=1.2)
    f.ax.plot([34, 18], [72.5, 72.5], color="k", lw=1.2)
    f.ax.annotate("", xy=(34, 26), xytext=(18, 26),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.plot([66, 71], [26, 26], color="k", lw=1.2)
    f.ax.annotate("", xy=(71, 26), xytext=(66, 26),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    f.ax.text(67, 23.5, "нет", fontsize=8)
    paths["float"] = f.save("bs_vsplytie.png")

    # 6 taskLess
    f = Flow("Рисунок 6 – Функция сравнения taskLess", h=11.2)
    a = f.term(50, 6, "Начало")
    b = f.data(50, 15, "Задачи A, B; поле field")
    d1 = f.rh(50, 28, "field =\nназвание?", w=30, h=11)
    r1 = f.proc(82, 28, "вернуть\nA.title < B.title", w=26, h=8, size=7.5)
    d2 = f.rh(50, 46, "field =\nпредмет?", w=30, h=11)
    r2 = f.proc(82, 46, "вернуть\nA.subj < B.subj", w=26, h=8, size=7.5)
    d3 = f.rh(50, 64, "даты\nразличны?", w=30, h=11)
    r3 = f.proc(82, 64, "вернуть\nA.date < B.date", w=26, h=8, size=7.5)
    r4 = f.proc(50, 80, "вернуть A.title < B.title", w=42, h=6)
    z = f.term(50, 92, "Конец")
    f.down(a, b)
    f.down(b, d1)
    f.aside(d1, r1, "да")
    f.down(d1, d2)
    f.ax.text(52, 36.5, "нет", fontsize=8)
    f.aside(d2, r2, "да")
    f.down(d2, d3)
    f.ax.text(52, 54.5, "нет", fontsize=8)
    f.aside(d3, r3, "да")
    f.down(d3, r4)
    f.ax.text(52, 72.2, "нет", fontsize=8)
    f.down(r4, z)
    f.ax.plot([82, 82], [32, 88], color="k", lw=1.2)
    f.ax.plot([50, 82], [88, 88], color="k", lw=1.2)
    paths["cmp"] = f.save("bs_sravnenie.png")

    # 7 deadlines
    f = Flow("Рисунок 7 – Контроль сроков задачи", h=10.8)
    a = f.term(50, 6, "Начало")
    d0 = f.rh(50, 18, "Колонка\n«Готово»?", w=30, h=11)
    ok0 = f.proc(82, 18, "не подсвечивать\nкак просроченную", w=28, h=8, size=7.5)
    p = f.proc(50, 34, "days ← дней до deadline", w=44, h=6)
    d1 = f.rh(50, 48, "days < 0 ?", w=30, h=10)
    red = f.proc(18, 48, "красный\nпросрочено", w=24, h=8, size=7.5)
    d2 = f.rh(50, 66, "days ≤ 3 ?", w=28, h=10)
    yel = f.proc(18, 66, "жёлтый\nсрок скоро", w=24, h=8, size=7.5)
    nrm = f.proc(50, 82, "обычный цвет", w=30, h=6)
    z = f.term(82, 82, "Конец", w=22, h=5)
    f.down(a, d0)
    f.aside(d0, ok0, "да")
    f.down(d0, p)
    f.ax.text(52, 25.5, "нет", fontsize=8)
    f.down(p, d1)
    f.aside(d1, red, "да", side="left")
    f.down(d1, d2)
    f.ax.text(52, 55.5, "нет", fontsize=8)
    f.aside(d2, yel, "да", side="left")
    f.down(d2, nrm)
    f.ax.text(52, 73.5, "нет", fontsize=8)
    f.ax.plot([82, 82], [22, 82], color="k", lw=1.2)
    f.ax.plot([18, 18], [52, 90], color="k", lw=1.2)
    f.ax.plot([18, 18], [70, 90], color="k", lw=1.2)
    f.ax.plot([50, 50], [85, 90], color="k", lw=1.2)
    f.ax.plot([18, 82], [90, 90], color="k", lw=1.2)
    f.ax.plot([82, 82], [90, 84.5], color="k", lw=1.2)
    f.ax.annotate("", xy=(82, 84.5), xytext=(82, 90),
                  arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2, mutation_scale=11))
    paths["dead"] = f.save("bs_sroki.png")
    return paths


# ---------------------------------------------------------------------------
# Графики
# ---------------------------------------------------------------------------
def bubble(a):
    arr = list(a)
    cmp = sw = 0
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            cmp += 1
            if arr[j + 1] < arr[j]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                sw += 1
    return cmp, sw


def insertion(a):
    arr = list(a)
    cmp = sw = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            cmp += 1
            if key < arr[j]:
                arr[j + 1] = arr[j]
                sw += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
    return cmp, sw


def float_sort(a):
    arr = list(a)
    cmp = sw = 0
    left, right = 0, len(arr) - 1
    while left < right:
        for i in range(left, right):
            cmp += 1
            if arr[i + 1] < arr[i]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                sw += 1
        right -= 1
        for i in range(right, left, -1):
            cmp += 1
            if arr[i] < arr[i - 1]:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                sw += 1
        left += 1
    return cmp, sw


def make_graphs():
    ns = [10, 20, 40, 60, 80, 100]
    random.seed(7)
    c_b, c_i, c_f = [], [], []
    s_b, s_i, s_f = [], [], []
    for n in ns:
        acc = {k: [0, 0] for k in "bif"}
        for _ in range(12):
            data = [random.randint(0, 10_000) for _ in range(n)]
            cb, sb = bubble(data)
            ci, si = insertion(data)
            cf, sf = float_sort(data)
            acc["b"][0] += cb; acc["b"][1] += sb
            acc["i"][0] += ci; acc["i"][1] += si
            acc["f"][0] += cf; acc["f"][1] += sf
        c_b.append(acc["b"][0] / 12); s_b.append(acc["b"][1] / 12)
        c_i.append(acc["i"][0] / 12); s_i.append(acc["i"][1] / 12)
        c_f.append(acc["f"][0] / 12); s_f.append(acc["f"][1] / 12)

    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=180)
    ax.plot(ns, c_b, "o-", label="Пузырьком")
    ax.plot(ns, c_i, "s-", label="Вставками")
    ax.plot(ns, c_f, "^-", label="Всплытием")
    ax.set_xlabel("Число элементов n")
    ax.set_ylabel("Среднее число сравнений")
    ax.set_title("Рисунок 8 – Число сравнений на случайных наборах")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    p1 = FIG / "graf_sravneniya.png"
    fig.savefig(p1, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=180)
    ax.plot(ns, s_b, "o-", label="Пузырьком")
    ax.plot(ns, s_i, "s-", label="Вставками")
    ax.plot(ns, s_f, "^-", label="Всплытием")
    ax.set_xlabel("Число элементов n")
    ax.set_ylabel("Среднее число перестановок")
    ax.set_title("Рисунок 9 – Число перестановок на случайных наборах")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    p2 = FIG / "graf_obmeny.png"
    fig.savefig(p2, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    n = np.arange(5, 120)
    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=180)
    ax.plot(n, n ** 2, label="O(n²) — пузырёк, вставки, всплытие")
    ax.plot(n, n * np.log2(n), label="O(n log n) — для сравнения (в программе нет)")
    ax.plot(n, n, label="O(n) — линейный просмотр доски")
    ax.set_xlabel("n")
    ax.set_ylabel("Условная трудоёмкость")
    ax.set_title("Рисунок 10 – Теоретическая сложность алгоритмов")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    p3 = FIG / "graf_slozhnost.png"
    fig.savefig(p3, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # demo board stats
    labels = ["Планируется", "В работе", "Готово"]
    sizes = [3, 1, 1]
    colors_pie = ["#BBDEFB", "#FFE082", "#C8E6C9"]
    fig, ax = plt.subplots(figsize=(6.4, 5.0), dpi=180)
    ax.pie(sizes, labels=labels, colors=colors_pie, autopct="%1.0f%%", startangle=90)
    ax.set_title("Рисунок 11 – Распределение демо-задач по колонкам")
    fig.tight_layout()
    p4 = FIG / "graf_kolonki.png"
    fig.savefig(p4, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    cats = ["Просрочено", "Срок ≤ 3 дней", "Обычные", "Готово"]
    vals = [1, 1, 2, 1]
    bar_c = ["#EF9A9A", "#FFF59D", "#BBDEFB", "#A5D6A7"]
    fig, ax = plt.subplots(figsize=(7.4, 4.8), dpi=180)
    ax.bar(cats, vals, color=bar_c, edgecolor="black")
    ax.set_ylabel("Количество задач")
    ax.set_title("Рисунок 12 – Контроль сроков на демонстрационных данных")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    p5 = FIG / "graf_sroki.png"
    fig.savefig(p5, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p1, p2, p3, p4, p5


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="TTitle", fontName="TimesNR-Bold", fontSize=16,
                          leading=20, alignment=TA_CENTER, spaceAfter=8))
    ss.add(ParagraphStyle(name="THead", fontName="TimesNR-Bold", fontSize=14,
                          leading=18, alignment=TA_CENTER, spaceAfter=10, spaceBefore=6))
    ss.add(ParagraphStyle(name="H1", fontName="TimesNR-Bold", fontSize=13,
                          leading=17, alignment=TA_LEFT, spaceBefore=12, spaceAfter=8))
    ss.add(ParagraphStyle(name="H2", fontName="TimesNR-Bold", fontSize=12,
                          leading=16, alignment=TA_LEFT, spaceBefore=10, spaceAfter=6))
    ss.add(ParagraphStyle(name="Body", fontName="TimesNR", fontSize=12,
                          leading=18, alignment=TA_JUSTIFY, firstLineIndent=12.5 * mm,
                          spaceAfter=4))
    ss.add(ParagraphStyle(name="BodyNoInd", fontName="TimesNR", fontSize=12,
                          leading=18, alignment=TA_JUSTIFY, spaceAfter=4))
    ss.add(ParagraphStyle(name="Center", fontName="TimesNR", fontSize=12,
                          leading=16, alignment=TA_CENTER, spaceAfter=4))
    ss.add(ParagraphStyle(name="Caption", fontName="TimesNR", fontSize=11,
                          leading=14, alignment=TA_CENTER, spaceBefore=4, spaceAfter=10))
    ss.add(ParagraphStyle(name="TOC", fontName="TimesNR", fontSize=12,
                          leading=20, alignment=TA_LEFT))
    ss.add(ParagraphStyle(name="TabCell", fontName="TimesNR", fontSize=10, leading=13, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="TabHead", fontName="TimesNR-Bold", fontSize=10, leading=13, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="Footer", fontName="TimesNR", fontSize=11, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="Lit", fontName="TimesNR", fontSize=12, leading=18,
                          alignment=TA_LEFT, leftIndent=15, firstLineIndent=-15, spaceAfter=6))
    return ss


def add_page_number(canvas, doc):
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setFont("TimesNR", 12)
        canvas.drawCentredString(A4[0] / 2, 12 * mm, str(page))
    canvas.restoreState()


def img(path, w=16.5 * cm):
    im = Image(str(path), width=w, height=w)
    # keep ratio
    from PIL import Image as PILImage
    with PILImage.open(path) as p:
        pw, ph = p.size
    h = w * ph / pw
    max_h = 20 * cm
    if h > max_h:
        h = max_h
        w = h * pw / ph
    return Image(str(path), width=w, height=h)


def build_pdf(figs):
    ss = styles()
    out = ROOT / "docs" / "Poyasnitelnaya_zapiska.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=30 * mm, rightMargin=15 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
        title="Пояснительная записка. Канбан учебных задач",
        author="Курсовой проект",
    )
    S = []

    def P(text, st="Body"):
        S.append(Paragraph(text, ss[st]))

    def cap(text):
        S.append(Paragraph(text, ss["Caption"]))

    # Title
    for _ in range(2):
        S.append(Spacer(1, 8 * mm))
    P("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ<br/>РОССИЙСКОЙ ФЕДЕРАЦИИ", "Center")
    S.append(Spacer(1, 8 * mm))
    P("ПОЯСНИТЕЛЬНАЯ ЗАПИСКА", "TTitle")
    P("к курсовому проекту", "THead")
    P("по дисциплине «Программирование» / «Алгоритмы и структуры данных»", "Center")
    S.append(Spacer(1, 8 * mm))
    P("<b>Тема:</b> Разработка программного средства для визуализации<br/>"
      "и отслеживания сроков выполнения учебных задач<br/>на базе канбан-доски", "Center")
    S.append(Spacer(1, 10 * mm))
    P("Программа: KanbanTasks (язык C++, графическая библиотека Qt)", "Center")
    S.append(Spacer(1, 18 * mm))
    P("Выполнил: ______________________________", "Center")
    P("Группа: ________________________________", "Center")
    P("Проверил: ______________________________", "Center")
    S.append(Spacer(1, 22 * mm))
    P("2026", "Center")
    S.append(PageBreak())

    P("СОДЕРЖАНИЕ", "THead")
    toc = [
        "Введение",
        "1 Постановка задачи",
        "2 Структура программы",
        "3 Алгоритмы сортировки",
        "3.1 Сортировка пузырьком",
        "3.2 Сортировка вставками",
        "3.3 Сортировка всплытием",
        "4 Контроль сроков",
        "5 Результаты экспериментов (графики)",
        "6 Руководство пользователя",
        "Заключение",
        "Список использованных источников",
        "Приложение А Расположение функций сортировки в коде",
    ]
    for t in toc:
        P(t, "TOC")
    S.append(PageBreak())

    P("ВВЕДЕНИЕ", "H1")
    P("Учебный процесс связан с большим числом лабораторных работ, рефератов, "
      "контрольных и курсовых заданий. Студенту нужно видеть, какие работы ещё не начаты, "
      "какие выполняются и какие уже сданы, а также не пропускать календарные сроки. "
      "Канбан-доска — простой способ такой визуализации: три колонки отражают состояние работы.")
    P("Целью проекта является разработка несложного программного средства на языке C++ "
      "с оконным интерфейсом Qt, которое хранит учебные задачи, показывает их на канбан-доске, "
      "подсвечивает просроченные работы и упорядочивает список при помощи классических "
      "алгоритмов сортировки, изучаемых в вузе.")
    P("В программе намеренно использованы простые алгоритмы: сортировка пузырьком, "
      "сортировка вставками и сортировка всплытием (шейкерная). Они имеют квадратичную "
      "сложность и понятную блок-схему, что соответствует учебной постановке задачи.")

    P("1 ПОСТАНОВКА ЗАДАЧИ", "H1")
    P("Необходимо разработать приложение со следующими функциями:")
    P("– хранение учебной задачи (название, предмет, срок, статус, заметка);", "BodyNoInd")
    P("– отображение задач в колонках «Планируется», «В работе», «Готово»;", "BodyNoInd")
    P("– добавление, изменение, удаление и перемещение карточек;", "BodyNoInd")
    P("– подсветка просроченных задач и задач со сроком не более трёх дней;", "BodyNoInd")
    P("– сортировка массива задач пузырьком, вставками или всплытием;", "BodyNoInd")
    P("– сохранение и загрузка данных из текстового файла.", "BodyNoInd")
    P("Средства реализации: язык C++ (стандарт C++17), библиотека Qt Widgets, "
      "сборка CMake или Qt Creator (.pro). Исходные тексты размещены в каталоге src.")

    P("2 СТРУКТУРА ПРОГРАММЫ", "H1")
    data = [
        [Paragraph("Модуль", ss["TabHead"]),
         Paragraph("Файл", ss["TabHead"]),
         Paragraph("Назначение", ss["TabHead"])],
        [Paragraph("Точка входа", ss["TabCell"]),
         Paragraph("main.cpp", ss["TabCell"]),
         Paragraph("Создание QApplication и окна", ss["TabCell"])],
        [Paragraph("Задача", ss["TabCell"]),
         Paragraph("Task.h / Task.cpp", ss["TabCell"]),
         Paragraph("Поля карточки, расчёт дней до срока", ss["TabCell"])],
        [Paragraph("Доска", ss["TabCell"]),
         Paragraph("Board.h / Board.cpp", ss["TabCell"]),
         Paragraph("Список задач, файл, вызов сортировки", ss["TabCell"])],
        [Paragraph("Сортировки", ss["TabCell"]),
         Paragraph("Sort.h / Sort.cpp", ss["TabCell"]),
         Paragraph("Пузырёк, вставки, всплытие, сравнение", ss["TabCell"])],
        [Paragraph("Окно", ss["TabCell"]),
         Paragraph("MainWindow.*", ss["TabCell"]),
         Paragraph("Интерфейс канбана и кнопки", ss["TabCell"])],
    ]
    tab = Table(data, colWidths=[3.2 * cm, 4.2 * cm, 8.6 * cm])
    tab.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(tab)
    S.append(Spacer(1, 4 * mm))
    P("Данные хранятся в оперативной памяти в контейнере QVector&lt;Task&gt;. "
      "На диск они записываются строками вида id;название;предмет;yyyy-MM-dd;статус;заметка. "
      "Такой формат легко открыть в текстовом редакторе, что удобно для учебной работы.")
    S.append(img(figs["prog"]))
    cap("Рисунок 1 – Общая схема работы программы (ГОСТ 19.701-90)")
    P("На схеме использованы стандартные символы: овал — пуск и останов, прямоугольник — процесс, "
      "ромб — решение, параллелограмм — ввод-вывод. После обработки команды программа снова "
      "ждёт действие пользователя, пока окно не будет закрыто.")

    P("3 АЛГОРИТМЫ СОРТИРОВКИ", "H1")
    P("Все три алгоритма работают с одним массивом задач. Критерий задаёт пользователь: "
      "срок сдачи, название или предмет. Сравнение вынесено в функцию taskLess, поэтому "
      "сами циклы сортировки не зависят от типа поля.")
    S.append(img(figs["choice"]))
    cap("Рисунок 2 – Выбор алгоритма в функции Board::sortTasks")
    S.append(img(figs["cmp"]))
    cap("Рисунок 6 – Блок-схема функции сравнения taskLess")
    P("Сложность всех трёх методов в худшем и среднем случаях — O(n²). Для учебной канбан-доски "
      "число карточек невелико (десятки, редко сотни), поэтому квадратичные алгоритмы приемлемы "
      "и наглядны при защите проекта.")

    P("3.1 Сортировка пузырьком", "H2")
    P("На каждом проходе сравниваются соседние элементы. Если они стоят в неправильном порядке, "
      "выполняется обмен. После первого прохода наибольший элемент оказывается в конце массива, "
      "как «пузырёк», всплывший на поверхность. Далее проход повторяется для оставшейся части.")
    S.append(img(figs["bubble"]))
    cap("Рисунок 3 – Блок-схема сортировки пузырьком")
    P("В коде это функция bubbleSort файла src/Sort.cpp. Внешний цикл задаёт номер прохода i, "
      "внутренний — индекс j соседней пары. Условие обмена: taskLess(arr[j+1], arr[j], field).")

    P("3.2 Сортировка вставками", "H2")
    P("Массив мысленно делится на отсортированную левую часть и неотсортированную правую. "
      "Очередной элемент key берётся из правой части и сдвигается влево, пока не будет найдено "
      "его место. Метод хорошо ведёт себя на почти упорядоченных данных.")
    S.append(img(figs["ins"]))
    cap("Рисунок 4 – Блок-схема сортировки вставками")
    P("Реализация — insertionSort в src/Sort.cpp. Пока j ≥ 0 и key меньше A[j], элементы "
      "сдвигаются вправо, затем key записывается в освободившуюся позицию.")

    P("3.3 Сортировка всплытием", "H2")
    P("Сортировка всплытием реализована как шейкерная (cocktail sort) — двусторонний вариант "
      "пузырька. Сначала выполняется проход слева направо: максимальный элемент всплывает к правому "
      "краю. Затем проход справа налево: минимальный элемент «тонет» к левому краю. Границы left "
      "и right после каждого полупрохода сжимаются.")
    S.append(img(figs["float"]))
    cap("Рисунок 5 – Блок-схема сортировки всплытием")
    P("Функция floatSort находится в том же файле src/Sort.cpp. По числу сравнений метод близок "
      "к пузырьку, но на некоторых наборах делает меньше проходов за счёт движения в обе стороны.")

    cmp_tab = [
        [Paragraph("Алгоритм", ss["TabHead"]),
         Paragraph("Лучший", ss["TabHead"]),
         Paragraph("Средний", ss["TabHead"]),
         Paragraph("Худший", ss["TabHead"]),
         Paragraph("Память", ss["TabHead"])],
        [Paragraph("Пузырьком", ss["TabCell"]),
         Paragraph("O(n²)*", ss["TabCell"]),
         Paragraph("O(n²)", ss["TabCell"]),
         Paragraph("O(n²)", ss["TabCell"]),
         Paragraph("O(1)", ss["TabCell"])],
        [Paragraph("Вставками", ss["TabCell"]),
         Paragraph("O(n)", ss["TabCell"]),
         Paragraph("O(n²)", ss["TabCell"]),
         Paragraph("O(n²)", ss["TabCell"]),
         Paragraph("O(1)", ss["TabCell"])],
        [Paragraph("Всплытием", ss["TabCell"]),
         Paragraph("O(n²)*", ss["TabCell"]),
         Paragraph("O(n²)", ss["TabCell"]),
         Paragraph("O(n²)", ss["TabCell"]),
         Paragraph("O(1)", ss["TabCell"])],
    ]
    t2 = Table(cmp_tab, colWidths=[3.4 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 2.6 * cm])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(t2)
    cap("Таблица 1 – Асимптотическая сложность реализованных алгоритмов")
    P("* В учебной реализации нет флага «были ли обмены», поэтому лучший случай пузырька "
      "и всплытия тоже остаётся квадратичным. Для вставок лучший случай O(n) сохраняется: "
      "внутренний цикл сразу останавливается.")

    P("4 КОНТРОЛЬ СРОКОВ", "H1")
    P("Для каждой задачи вычисляется число дней между текущей датой и полем deadline. "
      "Если работа ещё не в колонке «Готово» и срок уже прошёл, карточка красится красным. "
      "Если до срока не больше трёх дней — жёлтым. Завершённые задачи подсвечиваются зелёным.")
    S.append(img(figs["dead"]))
    cap("Рисунок 7 – Блок-схема контроля сроков")

    P("5 РЕЗУЛЬТАТЫ ЭКСПЕРИМЕНТОВ", "H1")
    P("Чтобы сравнить алгоритмы не только по формулам, те же три метода были прогнаны "
      "на случайных целочисленных массивах разной длины (по 12 повторов). Учитывались "
      "число сравнений и число перестановок. Это имитирует сортировку карточек по сроку.")
    S.append(img(figs["g1"]))
    cap("Рисунок 8 – Среднее число сравнений")
    S.append(img(figs["g2"]))
    cap("Рисунок 9 – Среднее число перестановок")
    P("На случайных данных вставки делают меньше сдвигов, чем классический пузырёк. "
      "Всплытие по сравнениям близко к пузырьку, потому что за один «кадр» делает два прохода, "
      "но границы массива сужаются с двух сторон. Все кривые растут примерно как n², "
      "что совпадает с теорией.")
    S.append(img(figs["g3"]))
    cap("Рисунок 10 – Сопоставление O(n), O(n log n) и O(n²)")
    P("Для демонстрационного файла data/tasks.txt построено распределение по колонкам "
      "и по состоянию срока. Красная категория — просроченная работа «Курсовой проект (черновик)».")
    S.append(img(figs["g4"], w=12 * cm))
    cap("Рисунок 11 – Колонки демо-набора")
    S.append(img(figs["g5"], w=14 * cm))
    cap("Рисунок 12 – Сроки демо-набора")

    P("6 РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ", "H1")
    P("После запуска открывается окно «Канбан учебных задач». Сверху расположены кнопки "
      "добавления, изменения и удаления, а также открытие и сохранение файла. Справа выбираются "
      "поле сортировки и алгоритм, затем нажимается «Сортировать».")
    P("Карточку нужно выделить щелчком в любой колонке. Кнопки «В работу», «Готово» и «Назад» "
      "меняют статус (0, 1 или 2). Цвет карточки обновляется сразу. Файл можно сохранить через "
      "диалог Windows; кодировка UTF-8, разделитель полей — точка с запятой.")
    P("Сборка: открыть KanbanTasks.pro в Qt Creator либо выполнить cmake в каталоге build. "
      "Нужны Qt 5 или Qt 6 (модуль Widgets) и компилятор MinGW либо MSVC.")

    P("ЗАКЛЮЧЕНИЕ", "H1")
    P("Разработано программное средство на C++/Qt, которое показывает учебные задачи "
      "на канбан-доске и следит за сроками. Для упорядочивания списка реализованы три "
      "классических алгоритма квадратичной сортировки. Блок-схемы построены по ГОСТ 19.701-90, "
      "экспериментальные графики подтверждают ожидаемый рост трудоёмкости. Программа пригодна "
      "для демонстрации на защите курсового проекта и для собственного учёта лабораторных работ.")

    P("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "H1")
    lit = [
        "1. ГОСТ 19.701-90. ЕСПД. Схемы алгоритмов, программ, данных и систем. Обозначения условные и правила выполнения. – М.: Стандартинформ, 2010.",
        "2. ГОСТ 7.32-2017. Отчёт о научно-исследовательской работе. Структура и правила оформления. – М.: Стандартинформ, 2017.",
        "3. Кнут, Д. Искусство программирования. Т. 3. Сортировка и поиск. – М.: Вильямс, 2019.",
        "4. Шилдт, Г. C++: базовый курс. – М.: Вильямс, 2018.",
        "5. Бланшет, Ж., Саммерфилд, М. Qt 4: программирование GUI на C++. – М.: Кудиц-Образ, 2008.",
        "6. Кормен, Т., Лейзерсон, Ч., Ривест, Р., Штайн, К. Алгоритмы: построение и анализ. – М.: Вильямс, 2013.",
        "7. Павловская, Т. А. C/C++. Программирование на языке высокого уровня. – СПб.: Питер, 2021.",
        "8. Документация Qt 6. Widgets [Электронный ресурс]. URL: https://doc.qt.io/qt-6/qtwidgets-index.html (дата обращения: 28.10.2026).",
    ]
    for x in lit:
        P(x, "Lit")

    S.append(PageBreak())
    P("ПРИЛОЖЕНИЕ А", "THead")
    P("Расположение функций сортировки в исходном коде", "Center")
    S.append(Spacer(1, 4 * mm))
    loc = [
        [Paragraph("Что", ss["TabHead"]), Paragraph("Где в проекте", ss["TabHead"])],
        [Paragraph("Все алгоритмы", ss["TabCell"]),
         Paragraph("src/Sort.cpp — bubbleSort, insertionSort, floatSort, taskLess", ss["TabCell"])],
        [Paragraph("Объявления", ss["TabCell"]),
         Paragraph("src/Sort.h", ss["TabCell"])],
        [Paragraph("Выбор алгоритма по номеру", ss["TabCell"]),
         Paragraph("src/Board.cpp, функция Board::sortTasks", ss["TabCell"])],
        [Paragraph("Кнопка «Сортировать»", ss["TabCell"]),
         Paragraph("src/MainWindow.cpp, слот MainWindow::onSort", ss["TabCell"])],
        [Paragraph("Список алгоритмов в окне", ss["TabCell"]),
         Paragraph("comboAlgo: 0 пузырёк, 1 вставки, 2 всплытие", ss["TabCell"])],
        [Paragraph("Подсветка сроков", ss["TabCell"]),
         Paragraph("Task.cpp (isOverdue, isSoon) и fillList в MainWindow.cpp", ss["TabCell"])],
    ]
    t3 = Table(loc, colWidths=[5.2 * cm, 10.8 * cm])
    t3.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(t3)
    S.append(Spacer(1, 6 * mm))
    P("Комментарии с этими указателями добавлены непосредственно в перечисленные файлы, "
      "чтобы при показе кода преподавателю было видно, где находится функционал сортировки.", "BodyNoInd")

    doc.build(S, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return out


# ---------------------------------------------------------------------------
# Презентация
# ---------------------------------------------------------------------------
BLUE = RGBColor(0x1A, 0x3A, 0x5C)
ACCENT = RGBColor(0xC6, 0x28, 0x28)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x22, 0x22, 0x22)
LIGHT = RGBColor(0xF4, 0xF6, 0xF8)


def set_run(run, size=18, bold=False, color=DARK, font="Times New Roman"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_bar(slide, prs):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.18))
    sh.fill.solid()
    sh.fill.fore_color.rgb = BLUE
    sh.line.fill.background()
    bot = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, prs.slide_height - Inches(0.38),
                                 prs.slide_width, Inches(0.38))
    bot.fill.solid()
    bot.fill.fore_color.rgb = BLUE
    bot.line.fill.background()
    tf = bot.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.RIGHT
    r = tf.paragraphs[0].add_run()
    r.text = "KanbanTasks  ·  курсовой проект  ·  2026    "
    set_run(r, 11, False, WHITE)


def title_slide(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    bg = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BLUE
    bg.line.fill.background()
    band = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.7), prs.slide_width, Inches(3.3))
    band.fill.solid()
    band.fill.fore_color.rgb = WHITE
    band.line.fill.background()
    box = sl.shapes.add_textbox(Inches(0.6), Inches(1.9), Inches(12.1), Inches(2.9))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Канбан учебных задач"
    set_run(r, 36, True, BLUE)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Программное средство визуализации и контроля сроков\nна языке C++ (Qt Widgets)"
    set_run(r2, 18, False, DARK)
    foot = sl.shapes.add_textbox(Inches(0.6), Inches(5.3), Inches(12.1), Inches(1.5))
    tf = foot.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Алгоритмы: пузырёк, вставки, всплытие (шейкерная)\nБлок-схемы по ГОСТ 19.701-90\n2026"
    set_run(r, 16, False, WHITE)


def slide_header(prs, title):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    bg = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = LIGHT
    bg.line.fill.background()
    add_bar(sl, prs)
    cap = sl.shapes.add_textbox(Inches(0.5), Inches(0.28), Inches(12.3), Inches(0.55))
    p = cap.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = title
    set_run(r, 26, True, BLUE)
    return sl


def bullets(sl, items, top=1.05, size=18, left=0.55, width=12.3):
    box = sl.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(5.6))
    tf = box.text_frame
    tf.word_wrap = True
    for i, t in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = "•  " + t
        set_run(r, size, False, DARK)


def add_picture(sl, path, x, y, w):
    sl.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))


def build_pptx(figs):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    title_slide(prs)

    sl = slide_header(prs, "Цель и задачи")
    bullets(sl, [
        "Цель: программа учёта учебных работ на канбан-доске.",
        "Показать статусы: планируется / в работе / готово.",
        "Отслеживать сроки: просрочено и «скоро сдавать».",
        "Упорядочивать задачи простыми сортировками из курса программирования.",
        "Сохранять список в текстовый файл.",
    ])

    sl = slide_header(prs, "Что сделано в программе")
    bullets(sl, [
        "Язык C++, окно на Qt Widgets (не консоль).",
        "Карточка задачи: название, предмет, срок, заметка, колонка.",
        "Кнопки добавить / изменить / удалить / сдвинуть по доске.",
        "Красный — просрочено, жёлтый — до 3 дней, зелёный — готово.",
        "Файл data/tasks.txt, поля через точку с запятой.",
    ])

    sl = slide_header(prs, "Структура исходного кода")
    bullets(sl, [
        "src/Sort.cpp — весь функционал сортировки.",
        "src/Board.cpp, sortTasks() — выбор алгоритма 0 / 1 / 2.",
        "src/MainWindow.cpp, onSort() — кнопка в окне.",
        "src/Task.cpp — дни до срока, просрочка.",
        "Комментарии в этих файлах прямо указывают, куда смотреть.",
    ])

    sl = slide_header(prs, "Общая схема программы")
    add_picture(sl, figs["prog"], 2.4, 0.95, 8.4)

    sl = slide_header(prs, "Три алгоритма сортировки")
    bullets(sl, [
        "Пузырьком (bubbleSort): соседние пары, больший элемент всплывает в конец.",
        "Вставками (insertionSort): очередной элемент вставляется в левую часть.",
        "Всплытием (floatSort): шейкерная, проход вправо и влево.",
        "Сложность всех трёх: O(n²), доп. память O(1).",
        "Сортировка по сроку, названию или предмету (функция taskLess).",
    ])

    sl = slide_header(prs, "Блок-схема: пузырёк (ГОСТ 19.701-90)")
    add_picture(sl, figs["bubble"], 3.15, 0.9, 6.9)

    sl = slide_header(prs, "Блок-схема: вставки (ГОСТ 19.701-90)")
    add_picture(sl, figs["ins"], 3.15, 0.9, 6.9)

    sl = slide_header(prs, "Блок-схема: всплытие (ГОСТ 19.701-90)")
    add_picture(sl, figs["float"], 3.15, 0.9, 6.9)

    sl = slide_header(prs, "График: число сравнений")
    add_picture(sl, figs["g1"], 1.6, 1.0, 10.0)

    sl = slide_header(prs, "График: число перестановок")
    add_picture(sl, figs["g2"], 1.6, 1.0, 10.0)

    sl = slide_header(prs, "Теоретическая сложность")
    add_picture(sl, figs["g3"], 1.6, 1.0, 10.0)

    sl = slide_header(prs, "Контроль сроков на доске")
    add_picture(sl, figs["g5"], 0.5, 1.15, 6.3)
    add_picture(sl, figs["g4"], 7.0, 1.15, 5.6)

    sl = slide_header(prs, "Выводы")
    bullets(sl, [
        "Получено рабочее Qt-приложение канбана учебных задач.",
        "Сроки видны по цвету карточки, статусы — по трём колонкам.",
        "В коде три понятных квадратичных алгоритма сортировки.",
        "Блок-схемы оформлены по ГОСТ 19.701-90.",
        "Для защиты достаточно открыть Sort.cpp и это презентацию.",
    ])

    sl = slide_header(prs, "Спасибо за внимание")
    box = sl.shapes.add_textbox(Inches(0.7), Inches(2.2), Inches(12), Inches(3))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Вопросы?"
    set_run(r, 40, True, BLUE)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Демонстрация: KanbanTasks.exe\nКод сортировок: src/Sort.cpp"
    set_run(r2, 18, False, DARK)

    out = ROOT / "docs" / "Prezentatsiya.pptx"
    prs.save(str(out))
    return out


def main():
    print("Блок-схемы...")
    figs = draw_all_flowcharts()
    print("Графики...")
    g1, g2, g3, g4, g5 = make_graphs()
    figs["g1"], figs["g2"], figs["g3"], figs["g4"], figs["g5"] = g1, g2, g3, g4, g5
    print("PDF...")
    pdf = build_pdf(figs)
    print("PPTX...")
    pptx = build_pptx(figs)
    print("OK", pdf)
    print("OK", pptx)


if __name__ == "__main__":
    main()
