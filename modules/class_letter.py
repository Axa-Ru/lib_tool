# import time
from class_autor import *
from utils import *
from class_settings import Settings
from modules import g_var

__author__ = 'axa'


class Letter:
    _settings = None
    _authorsCount = 0
    _seriesCount = 0
    _booksCount = 0

    def __init__(self, ss: Settings, letterPath=''):
        self._settings = ss
        if letterPath != '':
            self._letterPath = letterPath
        self._authors = [Autor(self._letterPath + '/' + authorName) for authorName in os.listdir(self._letterPath)]
        self._authorsCount = len(self._authors)
        self._seriesCount = 0
        self._booksCount = 0
        for a in self._authors:
            self._seriesCount += a._seriesCount
            self._booksCount += a._booksCount
        self._fullName = [a._author for a in self._authors]
        self._homonym = {}  # словарь со списком однофамильцев

    # Проверяет есть ли в списке автор с указанным именем?
    def getAuthorIndex(self, authorName):
        retval = -1
        for idx, autor in enumerate(self._authors):
            if autor._author == authorName:
                retval = idx
                break
        return retval

    # Удаляет автора с диска и из списка
    def markForDeleteAuthor(self, authorName):
        retval = False
        for idx, author in enumerate(self._authors):
            if author._author == authorName:
                author._deleted = True
                retval = True
                break
        return retval

    # удаляет Авторов помеченных на удаление и авторов у которых нет книг
    # удаляет пустые каталоги внутри авторов
    def deleteEmptyAuthors(self):
        i = 0
        deleted_autors = 0
        deleted = False
        while i < len(self._authors):
            author = self._authors[i]
            if author._deleted or not author._bookList:
                try:
                    shutil.rmtree(author._path)
                    deleted_autors += 1
                except FileNotFoundError:
                    logging.error('Ошибка! Уже где то был удален: %s', author._path)
                self._authors.pop(i)
                deleted = True
            else:
                i += 1
        if deleted:
            self.__init__(self._settings)
        return deleted_autors

    # Переносит все книги от autorName1 в автора autorName2 и помечает autorName1, как удаленный
    def moveBooksToAuthor(self, authorName1, authorName2):
        duplicated_book = 0
        i1 = self.getAuthorIndex(authorName1)
        i2 = self.getAuthorIndex(authorName2)
        if i1 == -1 or i2 == -1:
            return False
        author1 = self._authors[i1]
        author2 = self._authors[i2]

        sd = set(author1._bookHash) & set(author2._bookHash)  # преобразуем списки в множества и получаем
        # пересечения - hash одинаковых названий книг.
        for i in sd:
            i1 = author1._bookHash.index(i)
            i2 = author2._bookHash.index(i)
            book1 = author1._bookList[i1]
            book2 = author2._bookList[i2]
            if book1._size <= book2._size:  # удаляем меньшую из одинаковых книг
                author1.deleteBook(i1)
            else:
                author2.deleteBook(i2)
            duplicated_book += 1

        # все оставшиеся книги перемещаем из author1 в author2
        logging.info('Объединяю: %s -> %s', author1._author, author2._author)
        for src_dir, dirs, files in os.walk(author1._path):
            dst_dir = src_dir.replace(author1._path, author2._path, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.move(src_file, dst_dir)

        self.markForDeleteAuthor(authorName1)
        author2.replaceBooksAuthorName()
        author2.__init__('')  # переинициализируем атрибуты объекта

        return duplicated_book

    # тоже самое что и moveBooksToAutor но сделано через перегрузку операторов autorName2 += autorName1
    def __iadd__(self, other):
        self.moveBooksToAuthor(self, other)

    # Исправляет имя автора (название каталога), если необходимо
    def adjustBooks(self):
        duplicated_autor = duplicated_book = 0
        for idx, author in enumerate(self._authors):  # цикл по всем авторам внутри этой буквы
            if author._deleted is False:
                author.delDupBooks()  # Сначала удаляем дубликаты книг

                # Если требуется, заменяем букву "е" на "ё"
                if self._settings.a_ye_yo:
                    author.adjustYoAutorName()

                # Проверяем и правим, если необходимо фамилию автора
                # correctName = cleanNameString(author._author)
                author.adjustAutorName()

                if author.autor_name() != author.revised_autor_name():
                    # корректировка произошла. ФИО автора поменялось
                    if self.getAuthorIndex(author.revised_autor_name()) == -1:
                        # Дубликата автора нет. Просто переименовываем автора
                        # сначала переименовываем все книги
                        author.replaceBooksAuthorName(author.revised_autor_name())
                    else:  # Есть дубликат автора с правильным ФИО
                        duplicated_autor += 1
                        # переносим все книги в него и удаляем старый дубликат автора
                        # с диска и из списка авторов
                        self.moveBooksToAuthor(author.autor_name(), author.revised_autor_name())
                # Проверяем и, при необходимости правим номера серий
                author.adjustBookSeriesNumber()
                # Проверяем и, при необходимости названия книг
                author.adjustBookName()
                # Проверяем и, при необходимости, правим названии серии
                author.adjustBookSeriesName()
                # Обновляем epub информацию
                if self._settings.b_update_epub_info:
                    author.updateEpubInfo()
                author.__init__('')  # Просто переинициилизируем объект

        # Удаляем список авторов, помеченных как удаленные.
        duplicated_book = self.deleteEmptyAuthors()
        return duplicated_autor, duplicated_book

    def mergeSameAutors(self):
        duplicated_autors = 0
        # Ищет авторов с одинаковыми фамилиями
        # Это просто однофамильцы. Нужно будет проверить их на одинаковость.
        homonim = {}  # Временный словарь со списком однофамильцев
        # {"lastname1" : [Author1, Author2, Author3], ....}
        for x, fullName in enumerate(self._fullName):
            lastName = fullName.partition(' ')[0]
            if lastName in homonim:
                homonim[lastName].append(self._authors[x])
            else:
                homonim[lastName] = [self._authors[x]]
        # Удаляем из словаря всех авторов, которые встречаются только один раз
        homonim = {lastName: homonim[lastName] for lastName in homonim if len(homonim[lastName]) > 1}

        # Создаем связанные списки одинаковых авторов.
        # Под одним ключем (Фамилией) могут содержаться разные авторы
        #         +----------+       +----------+
        #         |  _next---+------>|  _next---+--->
        #     <---+--_prev   |<------+--_prev   |
        #         +----------+       +----------+

        for lastName in homonim:  # по всем однофамильцам
            authors = homonim[lastName]
            # # debug -------------------------------------------
            # # Для отладки напечатаем авторов с индексами
            # for i, Ai in enumerate(authors):
            #     Ai._idx = i
            #     print(Ai._idx, Ai._autor)
            # # -------------------------------------------------
            for i, Ai in enumerate(authors):  # двойной цикл по i и j
                for j, Aj in enumerate(authors):
                    if j < i:  # исключаем повторные сравнения
                        if isSameAutor(Ai, Aj):  # Это один и тот же автор
                            linkSameAutors(Ai, Aj)
                            # ut_PrintLinkChain(Ai)

        # Объединяем связанных авторов
        for lastName in homonim:  # по всем однофамильцам
            authors = homonim[lastName]
            for Ai in authors:
                if Ai._next is not None:
                    Aj = Ai._next
                    if Ai._author < Aj._author:
                        self.moveBooksToAuthor(Ai._author, Aj._author)
                        unLinkAutor(Ai)
                    else:
                        self.moveBooksToAuthor(Aj._author, Ai._author)
                        unLinkAutor(Aj)
                    duplicated_autors += 1
        return duplicated_autors

    def cleanUp(self):
        for A in self._authors:
            removeEmptyFolders(A._path)
        self.deleteEmptyAuthors()

    # возвращает число авторов, серий, книг
    def statistic(self):
        authors = series = book = 0
        for A in self._authors:
            authors += 1

        self.deleteEmptyAuthors()

    # Проверяет авторов с неверным порядком фамилии-имени-отчества
    def checkFirstName(self):
        for idx, autor in enumerate(self._authors):  # цикл по всем авторам внутри этой буквы
            pass

    # unit tests
    def ut_printLinks(self, autors):
        print('--------------------------------------------------')
        for x, Ax in enumerate(autors):
            if Ax._next is None:
                print(x, Ax._autor, '-> None')
            else:
                print(x, Ax._idx, '->', Ax._next._idx)

    def ut_printAllBooks(self):
        for x, Ax in enumerate(self._authors):
            print('---------------------------------------------------------------------------------------')
            Ax.ut_printBooks()
