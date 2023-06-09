from tkinter import *
import time
import logging


class Messages(logging.Handler):
    """ Вывод сообщений

    Сообщения могут быть 3 типов: help, info, warn
    Сообщения более высоких уровней заменяют сообщения более низких.
    Для обратной замены должно пройти не менее 5 секунд от публикации
    сообщения более высокого уровня, иначе новое игнорируется.
    """
    # root = None  # Объект фрейма для вывода сообщений

    def __init__(self, root):
        super().__init__()
        self.message = StringVar()
        self.widget_mes = Message(root, width=370, anchor='w', textvariable=self.message)
        self.widget_mes.place(x=0, y=0)
        self.old_rating = 0
        self.rating = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']  # Текущий уровень сообщения
        self.time = 0  # Время последнего сообщения
        self.colors = ['#0000FF', '#000000', '#0000FF', '#FF0000', '#FF00FF']
    def write(self, message):
        # здесь можно реализовать вывод сообщения в нужное место с учетом важности
        arr = message.split(':')
        level, message = arr[0], arr[1]

        """ Вывод сообщения в поле сообщений """
        if level not in self.rating:
            return
        if self.rating.index(level) < self.old_rating:
            if self.time + 5 > time.time():
                return
        self.widget_mes.config(foreground=self.colors[self.rating.index(level)])
        self.message.set(message)
        self.time = time.time()
        self.old_rating = self.rating.index(level)



