__author__ = 'axa'

#
#    +--ru             <---- корень
#      +--A
#      +--Б
#        +----Баринов Николай Сергеевич
#        +----Борондуков Степан Н.
#          +----Борондуков - Книга1.wpub
#          +----Борондуков - Книга2.wpub
#          +----Серия_1
#        +----Балуев К.К.
#          +----Серия_1
#             +---- Балуев 01 книга1.epub
#             +---- Балуев 02 книга2.epub
#             +---- Балуев 03 книга3.epub
#          +----Серия_2
#          +----Серия_3
#      +--В
#      +--Г

import os
from class_settings import Settings
from class_letter import Letter


class Library:
    #
    #
    def __init__(self, ss: Settings):
        global settings
        if ss is not None:
            settings: Settings = ss
        self.path = ""  # полный путь к корню библиотеки

        self.authorsCount = 0  # обнуляем счетчики для экземпляра класса
        self.booksCount = 0

        self.letters = []  # Массив объектов класса class_letter
        self.path = os.path.abspath(libRootPath)  # При инициализации передается путь к корню библиотеки
        letterFolderList = [f.path for f in os.scandir(self.path) if f.is_dir()]
        self.letters = [Letter(settings, l) for i, l in enumerate(letterFolderList)]
        pass

    # Разахивирует файлы обновления библиотеки
    def _extractBook(self, fromPath, toPath):
        pass

    # Перекодирует файлы из win1251 в utf-8
    def _win1251_utf8(self):
        pass

    # Добавляет в текущую библиотеку книги из updLib
    # Lib += updLib
    def __iadd__(self, other):
        pass

    def adjustBooks(self):
        pass

    def cleanUp(self):
        pass

    def countAutor(self):
        pass

    def countBook(self):
        pass


# --- unit tests---------------------------------------------------------------
def ut_class_library():
    ss = Settings()
    lib = Library(ss, "/media/axa/SSD-160/test/traum/epub.1711")
