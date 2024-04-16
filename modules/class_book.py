# coding=utf-8
__author__ = 'axa'
import tempfile

#from ebooklib import epub
import re
import os
import shutil
import fileinput
from utils import cleanBookName
import logging

""" Изначально книга находится в каталоге новых поступлений
    тип исходной книги fb2, epub
    В процессе обработки
    1. Конвертируем книгу из win1251 в utf8
    2. Конвертируем fb2->epub
    3. даем название
        "автор [number|-] название_книги"
    4 Если существует в библиотеке такой автор, то
      перемещаем книгу в целевую библиотеку
      Если это новый автор, то перемещаем книгу в новое дерево,
      для просмотра вручную и принятия решения

"""
"""
Структура названия книги:
    Autor_Last_Name [-|DD] Book_Name< (some_description)>< [СИ]>.epub
    ---------------  ----  --------- -------------------   ----
            |          |       |            |                |
            |          |       |            |                +--- СамИздат
            |          |       |            |
            |          |       |            +--- информация о книге
            |          |       |                 (сборник|рассказы)
            |          |       |
            |          |       +----- Название книги
            |          |
            |          +------ Дефис (-) или 2-цифровой номер серии
            |
            +---- Фамилия автора
"""



class Book():
#class Book(epub.EpubBook):
    def __init__(self, path, orgAutorDir=''):
        # Передается <путь к книге>, <фамилия автора>
        # В процессе разбора названия книги исправляет Фамилию автора, серию, Название книги.

        self._changed = False  # 1 - параметры книги были изменены, нужно переименовать файл.
        self._deleted = False  # 1 - должна быть книга удалена.

        self._path = path  # Полный путь книги (файла)
        self._size = os.stat(self._path).st_size  # размер книги
        self._dir, self._presentBookName = os.path.split(path)  # Каталог, где лежит книга, Имя файла

        # разбиваем строку на список [Имя, НомерСерии, Название]
        splitedBookName = re.split(r'( - )|( \d+ )', self._presentBookName)
        splitedBookName = [x for x in splitedBookName if x is not None]
        try:
            self._seriesNum = splitedBookName[1].strip()
        except IndexError:
            print('Ошибка разбора имени книги:', path)
            print('Поправьте название и перезапустите снова')
            quit()
        # self._series = str(self._seriesNum).isdigit()

        tail, parentDir = os.path.split(self._dir)
        if orgAutorDir == parentDir:  # Книга не входит в серию
            self._series = False
            tail, self._autor = os.path.split(self._dir)
            self._seriesName = ''
        else:
            self._series = True  # Книжка входит в серию, но
            if not str(self._seriesNum).isdigit():  # если номер серии не присвоен
                self._seriesNum = 0  # устанавливаем номер серии равным 0
            self._seriesNum = int(self._seriesNum)  # Вытаскиваема номер книги в серии
            tail, self._seriesName = os.path.split(self._dir)  # название серии
            tail, self._autor = os.path.split(tail)  # ФИО автора

        self._autorLN = self._autor.split(' ')[0]  # Вытаскиваем Фамилию Автора из названия каталога
        # и сравниваем с фамилией автора в имени
        self._bookName = ''.join(splitedBookName[2:])
        self._bookName = re.sub('.epub', '', self._bookName)  # Название книги, без "epub"
        self._bookName = cleanBookName(self._bookName)  # Почистил название книги
        self._clearBookName = re.sub(u'[Ёё]+', u'е', self._bookName)  # очищенное название книги (убраны все знаки
        # препинания, скобки, кавычки, переведено в
        # нижний регистр
        self._clearBookName = re.sub(u'[ \[\]\(\)”«»"“\.,=—?_…–:-;]', '', self._clearBookName)
        self._clearBookName = self._clearBookName.lower().strip()

    # конвертирует книгу в epub
    def convert2epub(self):
        pass

    # перемещает книгу в целевое дерево книг
    def moveBookToSter(self):
        pass

    # Проверяет и исправляет, при необходимости, названия книг
    def adjustBookName(self, newAutorLN=''):
        if newAutorLN != '':
            self._autorLN = newAutorLN

        # Нужно ли исправить полное название книги?
        if self.isSeries:
            newPresentBookName = '%s %02d %s.epub' % (self._autorLN, self._seriesNum, self._bookName)
        else:
            newPresentBookName = '%s - %s.epub' % (self._autorLN, self._bookName)

        # Название книги скорректировал ось и не соответствует имени файла, будем переименовывать
        if not newPresentBookName == self._presentBookName:
            dst = self._dir + '/' + newPresentBookName
            if os.path.exists(dst):
                # Ошибка. Должно быть было решено на уровне класса "class_autor"
                logging.error("Ошибка алгоритма. Такой файл есть -> %s", dst)
            else:
                os.rename(self._path, dst)
                logging.info('Переименовываю: %s -> %s', self._presentBookName, newPresentBookName)
                self._presentBookName = newPresentBookName
                self._path = dst
                self._changed = True

    # обновляет информацию внутри книги epub
    def updateEpubInfo(self):
        forceEpubInfo = True
        if self._changed or forceEpubInfo:
            dir_org = os.getcwd()  # сохраняем текущий каталог
            work_cat = tempfile.mkdtemp()
            os.chdir(work_cat)  # и переходим в рабочий
            work_path = work_cat + '/' + self._presentBookName
            shutil.move(self._path, work_path)
            os.system('unzip "' + self._presentBookName + '"')
            shutil.rmtree(self._presentBookName, ignore_errors=True)
            for line in fileinput.input(work_cat + '/OEBPS/content.opf', inplace=True):
                i = line.find('<dc:title>')
                if i != -1:
                    preffix = line[:i]
                    # обновляем название книги
                    line = preffix + '<dc:title>' + self._bookName + '</dc:title>\n'
                i = line.find('<dc:creator opf:role="aut">')
                if i != -1:
                    preffix = line[:i]
                    # обновляем автора книги
                    line = preffix + '<dc:creator opf:role="aut">' + self._autorLN + '</dc:creator>\n'
                print(line, end='')
            os.system('zip -r "' + self._presentBookName + '" *')
            shutil.move(work_path, self._path)
            shutil.rmtree(work_cat)
            os.chdir(dir_org)

    def deleteBook(self):
        try:
            os.remove(self._path)
        except FileNotFoundError:
            logging.error('Ошибка! Уже был удален файл: %s', self._path)

    @property
    def bookPath(self):
        return self._path

    @property
    def presentName(self):
        return self._presentBookName

    @property
    def bookName(self):
        return self._bookName

    @property
    def clearName(self):
        return self._clearBookName

    @property
    def seriesNum(self):
        return self._seriesNum

    @property
    def seriesName(self):
        return self._seriesName

    @property
    def autor(self):
        return self._autor

    @property
    def autorLN(self):
        return self._autorLN

    @property
    def isSeries(self):
        return self._series

    @property
    def bookSize(self):
        return self._size

    # Перегрузка операторов сравнения
    def __lt__(self, other):  # x < y
        if self._size < other._size:
            return True
        else:
            return False

    def __le__(self, other):  # x ≤ y
        if self._size <= other._size:
            return True
        else:
            return False

    def __eq__(self, other):  # x == y
        if self._size == other._size:
            return True
        else:
            return False

    def __ne__(self, other):  # x != y
        if self._size != other._size:
            return True
        else:
            return False

    def __gt__(self, other):  # x > y
        if self._size > other._size:
            return True
        else:
            return False

    def __ge__(self, other):  # x ≥ y
        if self._size >= other._size:
            return True
        else:
            return False
