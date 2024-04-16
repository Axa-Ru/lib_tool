import sys
import pathlib
import datetime
import os
import re
import logging
import shutil


def xstr(string):
    if string is None:
        return ''
    else:
        return str(string)


def str_to_list(s):
    if s:
        s = s.strip()
    result = []
    for x in s.split(','):
        result.append(x.strip())

    return result


def person_sort_name(name, first_delimiter=' '):
    n = name.split()
    if len(n) > 0:
        n.insert(0, n.pop())
        if len(n) == 1:
            return n[0]
        elif len(n) > 1:
            return n[0] + first_delimiter + ' '.join(n[1:])
        return ''
    else:
        return ''


def replace_keywords(s, m):
    def expand_keyword(s, key, val):
        if s.count(key) > 0:
            return s.replace(key, val), True if val else False
        return s, False

    def expand_all(s, m):

        expanded = False

        sorted_m = {}
        for k in sorted(m, key=len, reverse=True):
            sorted_m[k] = m[k]

        for key in sorted_m:
            s, ok = expand_keyword(s, key, sorted_m[key])
            expanded = expanded or ok

        if not expanded:
            return ''

        return s

    b_open = -1
    b_close = -1

    # Hack - I do not want to write real parser
    # s = s.replace(r'\{', chr(1)).replace(r'\}', chr(2))

    for i, sym in enumerate(s):
        if sym == '{':
            b_open = i
        elif sym == '}':
            b_close = i
            break
    if b_open >= 0 and b_close > 0 and b_open < b_close:
        s = replace_keywords(s[0:b_open] + expand_all(s[b_open + 1:b_close], m) + s[b_close + 1:], m)
    else:
        s = expand_all(s, m)

    return s


def split_ext(path):
    for ext in ['.fb2.zip']:
        if path.lower().endswith(ext):
            return ext
    return os.path.splitext(path)[1]


def replace_bad_symbols_(path):
    bad_symbols = '<>:"|*?'
    for s in bad_symbols:
        path = path.replace(s, '')
    return path


def normalize_path(path):
    def remove_illegal(s):
        illegal = '<>?:"*'
        for c in illegal:
            s = s.replace(c, '')
        return s

    def normalize_part(s: str) -> str:
        s = s.strip()
        if s.endswith('.'):
            s = s[0:-1]

        return remove_illegal(s)

    path = re.sub(r'\.+', '.', path)
    path = re.sub(r'\\+', r'\\', path)
    path = re.sub(r'\/+', '/', path)
    path = path.replace(r'\\', r'\\\\')

    p = pathlib.Path(path)
    clean_p = []

    if p.is_absolute():
        start = 1
        clean_p.append(p.anchor)
    else:
        start = 0
    for part in p.parts[start:]:
        clean_p.append(normalize_part(part))

    return str(pathlib.Path(*clean_p))


def get_file_creation_time(file):
    time = None
    if sys.platform == 'win32':
        time = os.path.getctime(file)
    elif sys.platform == 'darwin':
        time = os.stat(file).st_birthtime
    else:
        time = os.path.getctime(file)

    return datetime.datetime.fromtimestamp(time).isoformat()


def get_file_modified_time(file):
    time = os.stat(file).st_mtime
    return datetime.datetime.fromtimestamp(time).isoformat()


def roman_to_arabic(roman):
    s = roman.upper()
    integers = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
    result = 0
    for i, c in enumerate(roman):
        if i + 1 < len(roman) and integers[roman[i]] < integers[roman[i + 1]]:
            result -= integers[roman[i]]
        else:
            result += integers[roman[i]]
    return str(result)


def translate_series_index(s):
    try:
        index = int(s)    # пробуем int
    except:
        try:              # пробуем float
            index = int(float(s))
        except:
            try:
                index = roman_to_arabic(s)
            except:       # ничего не получилось
                index = 0
    return index

# -----------------------------------------------------------
#  функция очищает Имя автора от грязных символов
# (кавычки, знаки препинания многоточия и т.д. )
def cleanAuthorName(inStr: object) -> object:
    AuthorName = inStr
    # AuthorName = AuthorName.replace(Sufix, '')      #  Убирает из фамилии автора метку " [0001]" новых дабавленных авторов
    AuthorName = re.sub(u'[—–-]', '-', AuthorName)  # заменяем все Дефисы в имени на один тип
    AuthorName = re.sub(u'[\'`’]', '\'', AuthorName)  # заменяем все Апострофы в имени на один тип
    AuthorName = re.sub(u'[”«»"“\.,=?_…:\n]', ' ', AuthorName)  # убираем все знаки пунктуации и переводы строк
    AuthorName = ' '.join(AuthorName.split()).title()  # Первую букву в верхний регистр
    # Расставляет инициалы по правилам русского языка
    AuthorName = re.sub(u' (\S) (\S)$', r' \1.\2.', AuthorName)
    AuthorName = re.sub(u' (\S) ', r' \1. ', AuthorName)
    AuthorName = re.sub(u' (\S)$', r' \1.', AuthorName)
    AuthorName = re.sub(u' Дж$', r' Дж.', AuthorName)
    return AuthorName


# -----------------------------------------------------------
def look_series_from_filename(s):
    s_ar = ['', '']
    regex = r"(\[(.+)\])"
    matches = re.finditer(regex, s)
    for matchNum, match in enumerate(matches, start=1):
        s1 = match.group()
        s1 = s1[1:-1]
        series = s1.split()
        index = translate_series_index(series.pop()[0:2])
        series = ' '.join(series)
        s_ar = [series, index]
    return s_ar


# -----------------------------------------------------------
def cleanSeriesName(inStr):
    BookSeries = inStr
    BookSeries = re.sub(u'[—–-]', '-', BookSeries)  # Заменяем все длинные дефисы на нормальный: —–-
    BookSeries = re.sub(u' - ', '-', BookSeries)  # Убираем пробелы вокруг дефиса
    BookSeries = re.sub(u'[”«»"“\,=?_…:]', '', BookSeries)  # Убираем из названия все "грязные" символы : ”«»"“\,=?_…:
    # BookSeries = ' '.join(BookSeries.split())
    BookSeries = re.sub('\n', ' ', BookSeries)  # Убираем все переводы строк
    BookSeries = re.sub('\.+', '.', BookSeries)  # заменяем множественные точки
    BookSeries = re.sub(' \.', '.', BookSeries)  # убираем пробел перед точкой
    BookSeries = re.sub(' +', ' ', BookSeries)  # заменяем множественные пробелы
    BookSeries = re.sub(u'[\[({] ', '(', BookSeries)  # Заменяем любые виды скобок на круглые
    BookSeries = re.sub(u' [\])}]', ')', BookSeries)
    # BookSeries = re.sub(u'С\.е\.к\.р\.е\.т','Секрет', BookSeries)
    # BookSeries = re.sub(u'S\.t\.a\.l\.k\.e\.r','Stalker', BookSeries)
    # BookSeries = re.sub(u'W\.i\.t\.c\.h','W.i.t.c.h', BookSeries)
    # BookSeries = re.sub(u'п\.о\.э\.т','поэт', BookSeries)
    # BookSeries = re.sub(u'С\.и\.л\.в\.е\.р','С.и.л.в.е.р', BookSeries)
    # BookSeries = re.sub(u'S\.e\.c\.t\.o\.r','S.e.c.t.o.r', BookSeries)
    # BookSeries = re.sub(u'Z\.o\.n\.a','Z.o.n.a', BookSeries)
    # BookSeries = re.sub(u'S\.w\.a\.l\.k\.e\.r','S.w.a.l.k.e.r', BookSeries)
    # BookSeries = re.sub(u'','', BookSeries)
    BookSeries = re.sub(u'\.$', r'', BookSeries)  # Убираем точку в конце названия серии
    BookSeries = BookSeries.capitalize()  # Первый символ строки - в верхний регистр
    return BookSeries


def cleanBookName(inStr):
    BookName = inStr
    BookName = re.sub(u'[—–-]', '-', BookName)  # Заменяем все длинные дефисы на нормальный: —–-
    BookName = re.sub(u'[”«»"“\,=?_…:\'|]', '', BookName)  # Убираем из названия все "грязные" символы : ”«»"“\,=?_…:
    BookName = re.sub(u'\*', '#', BookName)  # Звездочка запрещена во многих файловых системах
    BookName = re.sub(u'\/', '-', BookName)  # Слэш запрещен во многих файловых системах
    BookName = re.sub(u' !', '!', BookName)  # Убираем пробел перед восклицательным знаком
    BookName = re.sub('\{', '(', BookName)  # Заменяем фигурные скобки на круглые
    BookName = re.sub('\}', ')', BookName)
    BookName = re.sub('\n', ' ', BookName)  # Убираем все переводы строк
    BookName = re.sub('\.+', '.', BookName).strip('\.')  # заменяем множественные точки
    BookName = re.sub(' +', ' ', BookName).strip()  # заменяем множественные пробелы
    BookName = re.sub('\. ', '.', BookName).strip()  # Убираем пробел после точки
    BookName = re.sub(' - ', '-', BookName).strip()  # Убираем пробелы вокруг дефиса в названии книги
    BookName = re.sub('\.\)', ')', BookName).strip()  # Убираем точку перед скобкой в названии книги
    BookName = re.sub(u'\([Cс]борник\)', 'СБ', BookName).strip()  # заменяем "(сборник)" на "(СБ)"
    BookName = re.sub('\[.+\]', '', BookName)  # Убираем все квадратные скобки и все внутри их
    BookName = BookName.strip()
    # BookName = BookName.capitalize()
    return BookName


def removeEmptyFolders(path, removeRoot=False):
    if not os.path.isdir(path):
        return
    # Удалим пустые папки внутри автора
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath, True)
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        logging.info('Removing empty folder: %s', path)
        os.rmdir(path)


NOACTION = 0
ADDED = 1
REPLACED = 2


def mv_book(src_file, dst_file):
    retval = NOACTION
    if os.path.exists(dst_file):
        if os.stat(src_file).st_size > os.stat(dst_file).st_size:  # Новый файл больше,
            os.remove(dst_file)
            logging.info("Удаляю: %s", dst_file)
            retval = REPLACED
        else:  # Новый файл меньше
            os.remove(src_file)  # Удаляем его и ничего не переносим
            logging.info("Удаляю: %s", src_file)
    if os.path.exists(src_file):
        logging.info("Перемещаю книгу: %s", src_file)
        shutil.move(src_file, dst_file)  # переносим его в библиотеку
        retval = ADDED
    return retval


# -----------------------------------------------------------
# Перемещает книги из одного дерева в другое.
# Считаю, если книга имеет больший размер, то это более свежая версия.
# В целевом дереве сохраняется книга большего размера
# Если параметр SaveOldBook == True, то вместо стирания старая версия переименовывается в .old
def mv3books(from_tree, to_tree):
    books_added = 0
    books_replaced = 0
    for src_dir, dirs, files in os.walk(from_tree):
        dst_dir = src_dir.replace(from_tree, to_tree)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            action = mv_book(src_file, dst_file)
            if action == ADDED:
                books_added += 1
            if action == REPLACED:
                books_replaced += 1
    print("Добавлено книг: ", books_added)
    print("Заменено книг: ", books_replaced)