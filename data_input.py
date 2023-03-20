# Набор классов для создания различных элементов ввода данных.
# Классы используют виджеты tkinter

import re
from tkinter import *


class DataInput:
    """ Базовый класс

     В зависимости от типа принимаемых данных создает объект (виджет)
     нужного подкласса с переданными параметрами.
     Валидирует ввод, запускает переданную функцию по определенному событию.

     """

    def widget_event(self, event):
        """ Определяет одно (нужное для работы) событие и выполняет функцию назначенную при создании объекта"""
        return self.func_event(event)

    @classmethod
    def CreateInput(cls, root, type='str', x=0, y=0, width=20, length=30, func_event=None, black_list='',
                    value=None, cast=[]):
        """ Общий интерфейс для всех типов полей ввода

        Параметры:
        root - родительский виджет
        type - тип поля текстом
        x, y - координаты на родительском виджета
        width - ширина виджета в символах
        length - ограничение по длине
        func_event - функция, обрабатывающая нажатие Enter (или другое событие ввода)
        black_list - список запрещенных символов (для строк)
        value - значение при инициализации
        cast - список значений для ComboBox

        """
        # Установка параметров
        cls.root = root
        cls.type = type
        cls.x = x
        cls.y = y
        cls.width = width
        cls.length = length
        cls.func_event = func_event
        cls.black_list = black_list
        cls.value = value
        cls.cast = cast
        cls.obj = None  # Сюда сохраняем объект виджета

        if type == 'int':
            return FieldInt()

    # Источник: https: // pythonstart.ru / osnovy / classmethod - staticmethod - python
class FieldInt(DataInput):
    """ Ввод целых чисел

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    func_event - функция, обрабатывающая нажатие Enter


    """

    def __init__(self):
        super().__init__()

        check = (self.root.register(self.is_valid), "%P")  # Назначаем функцию валидации

        en = Entry(self.root, width=self.width, validate="key", validatecommand=check)
        en.place(x=self.x, y=self.y)

        en.bind('<Return>', self.func_event)  # Ловим нажатие Enter

    def is_valid(self, val):
        """ Пускает только целое число или пустую строку """
        print(val)
        if not val:
            return True  # Строка может быть пустой

        if len(val) > self.length:
            return False  # Недопустимая длина

        return bool(re.fullmatch(r'\d+', val))  # Строка состоит только из цифр


class FieldStr(FieldInt):
    """ Ввод строк

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    black_list - список запрещенных символов
    func_event - функция, обрабатывающая нажатие Enter

    """

    def is_valid(self, val):
        """ Пропускает строку с заданными параметрами """

        for i in self.black_list:
            if i in val:
                return False  # Содержит символы из черного списка

        if len(val) > self.length:
            return False  # Недопустимая длина строки

        return True


class FieldFloat(FieldInt):
    """ Ввод числа с плавающей точкой

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    func_event - функция, обрабатывающая нажатие Enter

    """

    def is_valid(self, val):
        """ Пускает целое число, дробное, пустую строку """

        if not val:
            return True  # Строка может быть пустой

        if len(val) > self.length:
            return False  # Недопустимая длина

        return bool(re.fullmatch(r'^\d+(?:[\.,]\d*)?$', val))  # Пропускает целые и дробные числа


