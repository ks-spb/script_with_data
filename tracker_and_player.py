# ---------------------------------------------------------------------------
# Модуль для записи и воспроизведения событий мыши и клавиатуры
# ---------------------------------------------------------------------------

from time import sleep
from tkinter import *
from tktooltip import ToolTip
from pynput.mouse import Listener as MouseListener, Controller as mouse_Controller, Button as Btn
from pynput.keyboard import Listener as KeyboardListener, Controller as kb_Controller, Key
import pyautogui, pyperclip, keyboard

from threading import Thread

from settings import settings


kb = kb_Controller()
mouse = mouse_Controller()

class Tracker:

    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data = None  # Ссылка на класс с данными о скрипте

    def __init__(self, root):
        self.root = root  # Ссылка на главное окно программы
        self.single = False  # Для определения клика мыши, одинарный или двойной
        self.ctrl_pressed = False  # Инициализация флага нажатия клавиши ctrl
        self.listener_mouse = None  # Слушатель мыши
        self.listener_kb = None  # Слушатель клавиатуры
        self.is_listening = False  # Слушатели выключены

        # Кнопки управления записью
        self.icon1 = PhotoImage(file="icon/record.png")
        self.icon2 = PhotoImage(file="icon/stop.png")

        record_button = Button(command=self.rec_btn, image=self.icon1, width=100, height=34)
        record_button.place(x=12, y=settings.win_h - 43)
        ToolTip(record_button, msg="Запись скрипта", delay=0.5)

        stop_button = Button(command=self.stop_btn, image=self.icon2, width=100, height=34)
        stop_button.place(x=137, y=settings.win_h - 43)
        ToolTip(stop_button, msg="Останова записи", delay=0.5)

    def rec_btn(self):
        """ Обработка нажатия кнопки записи """
        # Запуск слушателя мыши
        self.listener_mouse = MouseListener(on_click=self.on_click)
        self.listener_mouse.start()

        # Запуск слушателя клавиатуры
        self.listener_kb = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        self.listener_kb.start()

        self.is_listening = True  # Слушатели включены

    def stop_btn(self):
        """ Обработка нажатия кнопки стоп """
        if self.data.script_started:
            # Остановка выполнения скрипта
            self.data.script_started = False
            return
        if self.is_listening:
            # Остановка записи
            self.listener_mouse.stop()
            # self.listener_mouse.join()
            self.listener_kb.stop()
            # self.listener_kb.join()
            self.is_listening = False

    def single_click(self, args):
        """ Фиксация 1 клика, запускается по таймеру и отменяется, если есть клик второй """
        if self.single:
            self.to_export(cmd='MouseClickLeft', val=[args[0], args[1], ''], des='')
        self.single = False

    def to_export(self, **kwargs):
        """ Добавление команды в список """
        self.data.make_command(**kwargs)  # Добавляем команду
        self.display_commands.out_commands()  # Обновляем список

    def on_click(self, *args):
        """ Клик мыши любой нопкой"""
        if not self.is_listening:
            return
        x = args[0]
        y = args[1]
        button = args[2]
        pressed = args[3]
        if button == button.left and pressed:
            if not self.single:
                self.single = True
                self.root.after(300, lambda: self.single_click(args))
            else:
                self.to_export(cmd='MouseClickDouble', val=[args[0], args[1], ''], des='')
                self.single = False

        if button == button.right and pressed:
            # Отправляем на создание объекта команды и запись
            self.to_export(cmd='MouseClickRight', val=[args[0], args[1]], des='')

    def on_press(self, key=None):
        if not self.is_listening:
            return
        # Получаем название клавиши одним словом или буквой
        print(key)
        try:
            out = key.char
        except:
            out = str(key)[4:]
        # Отправляем на создание объекта команды и запись
        # TODO периодически возникают ошибки при неправильны названиях клавиш
        # TODO как-то предотвратить запись комбинаций остановки записи
        self.to_export(cmd='KeyDown', val=[out], des='')
        if key == Key.esc and self.ctrl_pressed:
            # Выход из программы при нажатии ctrl+esc
            self.stop_btn()
            return False
        elif key == Key.ctrl:
            self.ctrl_pressed = True

    def on_release(self, key):
        if not self.is_listening:
            return
        # Получаем название клавиши одним словом или буквой
        try:
            out = key.char
        except:
            out = str(key)[4:]
        # Отправляем на создание объекта команды и запись
        self.to_export(cmd='KeyUp', val=[out], des='')
        if key == Key.ctrl:
            self.ctrl_pressed = False


class Player:
    """ Воспроизведение события мыши или клавиатуры """

    def __init__(self, root, run_script):
        """ Принимает ссылку на главное окно и функцию, которую нужно запустить для выполнения скрипта """
        self.root = root
        self.run_script = run_script  # Функи выполнения скрипта
        self.icon3 = PhotoImage(file="icon/play.png")

        play_button = Button(
            command=lambda: root.after(3000, self.run_thread), image=self.icon3, width=100, height=34)

        play_button.place(x=262, y=settings.win_h - 43)
        ToolTip(play_button, msg="Выполнение скрипта", delay=0.5)

    def run_thread(self):
        """ Запусск функции выполнения скрипта в отдельном потоке """
        new_thread = Thread(target=self.run_script)  # Создаём поток
        new_thread.start()  # Запускаем поток

    def run_command(self, cmd, val, des=None):
        """ Выполняет одну команду для мыши или клавиатуры

        Принимает команду и параметры. Для каждого события свои.
        Обрабатывает команды (cmd):
        MouseClickLeft, MouseClickDouble, MouseClickRight,
        KeyDown, KeyUp, Write

        """
        if cmd[:3] == 'Mou':
            # Команда мыши
            mouse.position = (val[0], val[1])  # Ставим указатель в нужную позицию
            if cmd == 'MouseClickLeft':
                # Клик левой копкой мыши
                mouse.press(Btn.left)
                mouse.release(Btn.left)

            elif cmd == 'MouseClickDouble':
                # Двойной клик
                mouse.click(Btn.left, 2)

            else:
                # Клик правой копкой мыши
                mouse.press(Btn.right)
                mouse.release(Btn.right)

        elif cmd[:3] == 'Key':
            # Подготовка к распознаванию как отдельных символов, так и специальных клавиш
            insert = val[0]
            if len(insert) == 1:
                insert = f"'{insert}'"
            else:
                insert = f"Key.{insert}"

            if cmd == 'KeyDown':
                # Нажать клавишу
                exec(f"kb.press({insert})")
            else:
                # Отпустить клавишу
                exec(f"kb.release({insert})")

        else:
            # печатает используя костыли
            # с помощью tkinter копируем в буфер обмена, а потом Ctrl+v
            try:
                mem = self.root.clipboard_get()
            except:
                mem = ''
            self.root.clipboard_clear()
            self.root.clipboard_append(val[0])
            kb.press(Key.ctrl)
            kb.press('v')
            kb.release('v')
            kb.release(Key.ctrl)
            sleep(0.2)  # Без паузы видимо успевает очистить раньше, чем вставить
            self.root.clipboard_clear()