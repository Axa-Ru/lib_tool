__author__ = 'axa'

import os
import class_book
import shutil
import binascii
import logging
import re
from utils import cleanSeriesName
from modules import g_var


class Autor:
    fName = ""
    mName = ""
    lName = ""

    def __init__(self, path=''):
        # path:    При инициализации передается путь к автору
        # если path пустой, то реинициализация существующего объекта
        if path != '':  # иначе это новый
            self._path = path
            # Указатели для реализации двунаправленного списка
            self._next = None  # Указатель на следующий объект
            self._prev = None  # Указатель на предыдущий объект

        self._changed = False  # 1 - параметры Автора были изменены, нужно переименовать каталог.
        self._deleted = False  # 1 - Автор должен быть удален
        self._idx = None  # Индекс, использую для отладки

        # Получаем букву и текущее имя автора
        self._letter, self._author = os.path.split(self._path)
        # Исправленное имя автора и текущее имя автора - одно и то же
        self._revised_autor = self._author

        self._seriesList = []  # список серий
        self._seriesHash = []  # crc32 "очищенных" серий

        self._bookList = []  # список книг
        self._bookHash = []  # crc32 "очищенных" названий книг
        # храню их отдельно от книг, потому, что так удобно их сравнивать
        self._bookDup = {}  # словарь со списком дубликатов
        self._indexBookForDelete = []  # список индексов self._bookList книг для удаления

        self._booksCount = 0  # количество книг у автора
        self._seriesCount = 0  # количество серий у автора

        # Загружаем все книги
        for dirname, subshere, fileshere in os.walk(self._path):
            for fname in fileshere:
                curBook = class_book.Book(os.path.join(dirname, fname), self._author)
                self._bookList.append(curBook)
                try:
                    self._bookHash.append(binascii.crc32(str.encode(curBook.clearName)))
                except:
                    logging.error('Ошибка открытия файла в каталоге: %s', dirname)
                    quit()
        self._booksCount = len(self._bookList)

        # Вытаскиваем из списка книг все серии. Название серии есть в классе "class_book",
        # но тут мы сохраним список названий серий без повторов (дубликатов)
        self._seriesList = [book._seriesName for book in self._bookList]
        self._seriesList = set(self._seriesList)
        try:
            self._seriesList.remove('')  # Удаляем пустые серии ( для книг без серий )
        except KeyError:
            pass  # Если таких книг не было то возникает исключение. Просто игнорируем.
        self._seriesCount = len(self._seriesList)
        # посчитаем хэши серий
        self._seriesHash = [binascii.crc32(str.encode(seriesName)) for seriesName in self._seriesList]
        pass

    def adjustAutorName(self):
        self._revised_autor = re.sub(u'[—–-]', '-', self._revised_autor)  # заменяем все Дефисы в имени на один тип
        self._revised_autor = re.sub(u'[\'`’]', '\'',
                                     self._revised_autor)  # заменяем все Апострофы в имени на отдин тип
        self._revised_autor = re.sub(u'[”«»"“\.,=?_…:\n]', ' ',
                                     self._revised_autor)  # убираем все знаки пунктуации и переводы строк
        self._revised_autor = ' '.join(self._revised_autor.split()).title()  # Первую букву в верхний регистр
        # Расставляет инициалы по правилам русского языка
        self._revised_autor = re.sub(u' (\S) (\S)$', r' \1.\2.', self._revised_autor)
        self._revised_autor = re.sub(u' (\S) ', r' \1. ', self._revised_autor)
        self._revised_autor = re.sub(u' (\S)$', r' \1.', self._revised_autor)
        self._revised_autor = re.sub(u' Дж$', r' Дж.', self._revised_autor)
        return self._revised_autor

    def adjustYoAutorName(self):
        fio = self._revised_autor
        fio = fio.replace('.', ' ').split(' ')
        l_fio = len(fio)
        if fio[0] in g_var.array_ye_lastname:
            index = g_var.array_ye_lastname.index(fio[0])
            fio[0] = g_var.array_yo_lastname[index]

        if l_fio > 1 and fio[1] in g_var.array_ye_firstname:
            index = g_var.array_ye_firstname.index(fio[1])
            fio[1] = g_var.array_yo_firstname[index]

        if l_fio > 2 and fio[2] in g_var.array_ye_middlename:
            index = g_var.array_ye_middlename.index(fio[2])
            fio[2] = g_var.array_yo_middlename[index]

        self._revised_autor = ' '.join(fio)
        return self._revised_autor

    def autor_name(self):
        return self._author

    def revised_autor_name(self):
        return self._revised_autor

    # Заменяет Автора в названиях книг
    def replaceBooksAuthorName(self, newAutorName=''):
        if newAutorName == '':
            dest = self._path
            newAutorName = os.path.split(dest)[1]
        else:
            dest = self._letter + '/' + newAutorName

        autorLastName = newAutorName.split()[0]
        for book in self._bookList:
            book.adjustBookName(autorLastName)

        if not (os.path.isdir(dest)):
            os.rename(self._path, dest)  # переименовываем автора
            logging.info('Переименовываю: %s -> %s', self._author, newAutorName)
            self._author = newAutorName
            self._path = dest
        self.__init__('')

    # Исправляет названия серий книг.
    def adjustBookSeriesName(self):
        if not self._deleted:
            # sl = [book._seriesName for book in self._bookList]
            # sl = set(sl)
            # try:
            #     sl.remove('')   # Удаляем пустые серии ( для книг без серий )
            # except KeyError:
            #     pass            # Если таких книг не было то возникает исключение. Просто игнорируем.
            # for oldSeriesName in sl:
            for oldSeriesName in self._seriesList:
                newSeriesName = cleanSeriesName(oldSeriesName)
                if newSeriesName != oldSeriesName:
                    self._changed = True
                    newSeriesPath = self._path + '/' + newSeriesName
                    oldSeriesPath = self._path + '/' + oldSeriesName
                    logging.info('Переименовываю %s -> %s', oldSeriesPath, newSeriesPath)
                    if not os.path.isdir(newSeriesPath):
                        os.makedirs(newSeriesPath)
                    for file in os.listdir(oldSeriesPath):
                        path = os.path.join(oldSeriesPath, file)
                        # перемещаем в новый каталог только те книги, что новее
                        shutil.move(path, newSeriesPath)
                    shutil.rmtree(oldSeriesPath)
            if self._changed:
                self.__init__('')  # Просто переинициилизируем объект

    # Исправляет номера серии книг
    def adjustBookSeriesNumber(self):
        pass  # Ничего делать специально не нужно При вызове следующего метода автоматом обновится номер серии

    # Исправляет названия книг
    def adjustBookName(self):
        if not self._deleted:
            for book in self._bookList:
                book.adjustBookName()
            if self._changed:
                self.__init__('')  # Просто переинициилизируем объект

    # Обновляем epub информацию
    def updateEpubInfo(self):
        if not self._deleted:
            for book in self._bookList:
                book.updateEpubInfo()

    def isPresentBook(self, bookClearName):
        # проверяет есть ли книга с названием bookClearName
        # если есть, то возвращает True, если нет, то False
        return binascii.crc32(str.encode(bookClearName)) in self._bookHash

    def deleteBook(self, i):
        # удаляет книгу с индексом i
        self._bookList[i].deleteBook()  # удаляем книгу с диска
        logging.info('Удаляю -> %s', self._bookList[i]._path)
        self._bookList.pop(i)  # удаляем книгу из списка
        self._bookHash.pop(i)  # удаляем hash книги из списка

    def findDupBooks(self):
        # Ищет книги с одинаковым названием внутри одного автора
        for x, crc in enumerate(self._bookHash):
            if crc in self._bookDup:
                self._bookDup[crc].append(x)
            else:
                self._bookDup[crc] = [x]
        self._bookDup = {crc: self._bookDup[crc] for crc in self._bookDup if len(self._bookDup[crc]) > 1}

    def delDupBooks(self):
        # Удаляет одинаковые книги внутри одного автора по следующим критериям
        # выбирается для удаления книга меньшего размера
        self.findDupBooks()
        for bds in self._bookDup:  # проходим по словарю дубликатов
            bd = self._bookDup.get(bds)
            while len(bd) > 1:  # проходим по всем дубликатам одной книги
                b0 = self._bookList[bd[0]]
                b1 = self._bookList[bd[1]]
                if b0 > b1:  # если первая книга по размеру больше второй, то в словаре
                    bd[0], bd[1] = bd[1], bd[0]  # дубликатов меняем индексы книг местами
                # индекс 0 указывает на книгу, которую нужно физически удалить с диска
                self._indexBookForDelete.append(bd[0])
                self._bookDup.get(bds).pop(0)  # удалить из списка дубликатов
        self._indexBookForDelete.sort(reverse=True)
        for i in self._indexBookForDelete:
            self.deleteBook(i)
            # self._bookList[i].deleteBook()
            # self._bookList.pop(i)
        self._bookDup = {}
        self._indexBookForDelete = []

    def printDup(self):
        print(self._bookDup)

    # Если не последний элемент списка однофомильцев - возвращает True
    def isLastInHomonimChain(self):
        if self._next is None:
            return False
        else:
            return True

    def isEmptyHomonimChain(self):
        if self._prev is None and self._next is None:
            return True
        else:
            return False

    # печатает все книги и индексы
    def ut_printBooks(self):
        for book in self._bookList:
            print(book._path, '| Серия:', book._series, '| Фамилия:', book._autorLN, '| Название', book._bookName)


# если есть хотя бы одна одинаковая книга возвращает True
# в противном случае возвращает False
def isSameAutor(autor1, autor2):
    SameAuthor = False
    # Если есть хотя бы одна одинаковая книга - значит это один и тот же автор
    sd = set(autor1._bookHash) & set(autor2._bookHash)  # преобразуем списки в множества
    # и получаем пересечения - hash одинаковых книг.
    if len(sd) != 0:
        SameAuthor = True

    ss = set(autor1._seriesHash) & set(autor2._seriesHash)  # аналогично, проверяем серии
    if len(ss) != 0:
        SameAuthor = True

    return SameAuthor


# Проверяет связан ли уже Autor1 -> Autor2?
# Если да, то возвращает True, нет - False
def isLinked(A1: Autor, A2: Autor):
    # Проматываем Autor2 в начало списка
    while A2._prev:
        A2 = A2._prev
    # Теперь в обратую сторону и проверяем на равенство
    while A2._next:
        if A1 == A2:
            return True
        A2 = A2._next
    return False


# Присоединяем Autor1 -> Autor2
def linkSameAutors(A1: Autor, A2: Autor):
    if not isLinked(A1, A2):
        # Проматываем Autor1 в конец списка
        while A1._next:
            A1 = A1._next
        # Проматываем Autor2 в начало списка
        while A2._prev:
            A2 = A2._prev
        # нужно проверить не будет ли закольцованности.
        A1._next = A2
        A2._prev = A1


# Удаляет autor из списка
def unLinkAutor(autor: Autor):
    if autor._next and not autor._prev:  # первый в цепочке
        b = autor._next
        b._prev = autor._next = None
    if not autor._next and autor._prev:  # последний в цепочке
        a = autor._prev
        a._next = autor._prev = None
    if autor._next and autor._prev:  # в середине цепочки
        a = autor._prev
        b = autor._next
        a._next = b
        b._prev = a
    if not autor._next and not autor._prev:  # не включен в цепочку - последний объект списка
        pass


# --- unit tests---------------------------------------------------------------
def ut_ClassAutor(autorPath):
    tAutor = Autor(autorPath)
    totalBooks = len(tAutor._bookList)
    for x in range(0, totalBooks):
        print(x, '\t', tAutor._bookHash[x], ' \t' + tAutor._bookList[x].clearName)
    tAutor.findDupBooks()
    tAutor.printDup()
    tAutor.delDupBooks()
    tAutor.printDup()


def ut_PrintLinkChain(a: Autor):
    # Проматываем Autor1 в начало списка
    while a._prev:
        a = a._prev
    print(a._idx, end="")
    while a._next:
        a = a._next
        print(' ->', a._idx, end="")
    print('')
