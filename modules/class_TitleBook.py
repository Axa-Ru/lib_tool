import re

class ElementTitle:
    def __init__(self, s: str):
        self.present_str = self.correct_str = s
        self.clear()

    def clear(self) -> str:
        self.correct_str = re.sub(u'/', '-', self.correct_str)  # Слэш запрещен во многих файловых системах
        self.correct_str = re.sub(u'[—–-]+', '-', self.correct_str)  # заменяем все Дефисы в имени на один тип
        self.correct_str = re.sub(u'[\'`’]', '\'', self.correct_str)  # заменяем все Апострофы в имени на один тип
        self.correct_str = re.sub(u'[”«»"“\.,=?_…:\n]+', ' ',
                                  self.correct_str)  # убираем все знаки пунктуации и переводы строк
        self.correct_str = re.sub(u'\*', '#', self.correct_str)  # Звездочка запрещена во многих файловых системах
        self.correct_str = re.sub(u'#+', '#', self.correct_str)  # Звездочка запрещена во многих файловых системах
        self.correct_str = re.sub(' +', ' ', self.correct_str).strip()  # заменяем множественные пробелы на одиночный
        self.correct_str = re.sub('\.+', '.', self.correct_str).strip('\.')  # заменяем множественные точки
        return self.correct_str

    def is_changed(self):
        return False if self.present_str == self.correct_str else True

    def get_value(self):
        return self.correct_str

    def set_value(self, value):
        self.correct_str = value


class AuthorName(ElementTitle):
    # Определения глобальных переменных класса
    array_yo_firstname = array_ye_firstname = None
    array_yo_middlename = array_ye_middlename = None
    array_yo_lastname = array_ye_lastname = None
    array_firstname = None
    # Пути к спискам имен, отчеств, фамилий
    s_yo_firstname = s_yo_middlename = s_yo_lastname = s_firstname = ''

    @staticmethod
    def load_names_arrays(first_name_yo_dict_path, middle_name_yo_dict_path, last_name_yo_dict_path, first_name_dict_path):
        ''' Загружаем списки имён, отчеств, фамилий
            Делаем аналогичные списки с замененной буквой "ё" на "е" '''
        AuthorName.s_yo_firstname = first_name_yo_dict_path
        AuthorName.s_yo_middlename = middle_name_yo_dict_path
        AuthorName.s_yo_lastname = last_name_yo_dict_path

        with open(AuthorName.s_yo_firstname) as file:
            AuthorName.array_yo_firstname = [row.strip() for row in file]
        AuthorName.array_ye_firstname = [row.replace('ё', 'е') for row in AuthorName.array_yo_firstname]

        with open(AuthorName.s_yo_middlename) as file:
            AuthorName.array_yo_middlename = [row.strip() for row in file]
        AuthorName.array_ye_middlename = [row.replace('ё', 'е') for row in AuthorName.array_yo_middlename]

        with open(AuthorName.s_yo_lastname) as file:
            AuthorName.array_yo_lastname = [row.strip() for row in file]
        AuthorName.array_ye_lastname = [row.replace('ё', 'е') for row in AuthorName.array_yo_lastname]

        with open(AuthorName.s_firstname) as file:
            AuthorName.array_firstname = [row.strip() for row in file]

        return

    def __init__(self, s: str = ''):
        super().__init__(s)

    def clear(self) -> str:
        super().clear()
        # Первую букву в верхний регистр
        self.correct_str = ' '.join(self.correct_str.split()).title()
        # Расставляем инициалы по правилам русского языка
        self.correct_str = re.sub(u' (\S) (\S)$', r' \1.\2.', self.correct_str)
        self.correct_str = re.sub(u' (\S) ', r' \1. ', self.correct_str)
        self.correct_str = re.sub(u' (\S)$', r' \1.', self.correct_str)
        self.correct_str = re.sub(u' Дж$', r' Дж.', self.correct_str)
        return self.correct_str

    '''  Заменяет в в ФИО букву "е" на "ё" '''
    def replace_yeyo(self):
        fio = self.correct_str
        fio = fio.replace('.', ' ').split(' ')
        l_fio = len(fio)
        if fio[0] in AuthorName.array_ye_lastname:
            index = AuthorName.array_ye_lastname.index(fio[0])
            fio[0] = AuthorName.array_yo_lastname[index]

        if l_fio > 1 and fio[1] in AuthorName.array_ye_firstname:
            index = AuthorName.array_ye_firstname.index(fio[1])
            fio[1] = AuthorName.array_yo_firstname[index]

        if l_fio > 2 and fio[2] in AuthorName.array_ye_middlename:
            index = AuthorName.array_ye_middlename.index(fio[2])
            fio[2] = AuthorName.array_yo_middlename[index]

        self.correct_str = ' '.join(fio)
        return self.correct_str

    def get_author_last_name(self):
        return self.correct_str.split()[0]


class BookName(ElementTitle):
    def __init__(self, s: str = ''):
        super().__init__(s)

    def clear(self) -> str:
        super().clear()
        self.correct_str = re.sub('{', '(', self.correct_str)  # Заменяем фигурные скобки на круглые
        self.correct_str = re.sub('}', ')', self.correct_str)
        self.correct_str = re.sub('\. ', '.', self.correct_str).strip()  # Убираем пробел после точки
        self.correct_str = re.sub(' - ', '-',
                                  self.correct_str).strip()  # Убираем пробелы вокруг дефиса в названии книги
        self.correct_str = re.sub('\.\)', ')', self.correct_str).strip()  # Убираем точку перед скобкой в названии книги
        self.correct_str = re.sub(u'\([СсБбОоРрНнИиКк]+\)', '(СБ)',
                                  self.correct_str).strip()  # заменяем "(сборник)" на "(СБ)"
        self.correct_str = re.sub(u'\(с иллюстрациями [А-ЯЁа-яё \.]+\)', '(ИЛЛ)',
                                  self.correct_str).strip()  # заменяем на "(ИЛЛ)"
        self.correct_str = re.sub('\[.+\]', '', self.correct_str)  # Убираем все квадратные скобки и все внутри их
        self.correct_str = self.correct_str.strip()
        # self.correct_str = self.correct_str.capitalize()

        if not self.correct_str:      # Если название книги пустое, то
            self.correct_str = 'TitleUnknown'

        return self.correct_str


class SeriesName(ElementTitle):
    def __init__(self, s: str = ''):
        super().__init__(s)

    def clear(self) -> str:
        super().clear()
        self.correct_str = re.sub(u'[—–-]+', '-', self.correct_str)  # Заменяем все длинные дефисы на нормальный: —–-
        self.correct_str = re.sub(u' - ', '-', self.correct_str)  # Убираем пробелы вокруг дефиса
        self.correct_str = re.sub(u'[”«»"“,=?_…:]', '',
                                  self.correct_str)  # Убираем из названия все "грязные" символы : ”«»"“\,=?_…:
        # self.correct_str = ' '.join(self.correct_str.split())
        self.correct_str = re.sub('\n', ' ', self.correct_str)  # Убираем все переводы строк
        self.correct_str = re.sub('\.+', '.', self.correct_str)  # заменяем множественные точки
        self.correct_str = re.sub(' \.', '.', self.correct_str)  # убираем пробел перед точкой
        self.correct_str = re.sub(' +', ' ', self.correct_str)  # заменяем множественные пробелы
        self.correct_str = re.sub(u'[\[({] ', '(', self.correct_str)  # Заменяем любые виды скобок на круглые
        self.correct_str = re.sub(u' [\])}]', ')', self.correct_str)
        # self.correct_str = re.sub(u'С\.е\.к\.р\.е\.т','Секрет', self.correct_str)
        # self.correct_str = re.sub(u'S\.t\.a\.l\.k\.e\.r','Stalker', self.correct_str)
        # self.correct_str = re.sub(u'W\.i\.t\.c\.h','W.i.t.c.h', self.correct_str)
        # self.correct_str = re.sub(u'п\.о\.э\.т','поэт', self.correct_str)
        # self.correct_str = re.sub(u'С\.и\.л\.в\.е\.р','С.и.л.в.е.р', self.correct_str)
        # self.correct_str = re.sub(u'S\.e\.c\.t\.o\.r','S.e.c.t.o.r', self.correct_str)
        # self.correct_str = re.sub(u'Z\.o\.n\.a','Z.o.n.a', self.correct_str)
        # self.correct_str = re.sub(u'S\.w\.a\.l\.k\.e\.r','S.w.a.l.k.e.r', self.correct_str)
        # self.correct_str = re.sub(u'','', self.correct_str)
        self.correct_str = re.sub(u'\.$', r'', self.correct_str)  # Убираем точку в конце названия серии
        self.correct_str = self.correct_str.capitalize()  # Первый символ строки - в верхний регистр
        return self.correct_str


class SeriesIndex(ElementTitle):
    def _roman_to_arabic(self, s: str) -> int:
        roman = s.upper()
        integers = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
        result = 0
        for i, c in enumerate(roman):
            if i + 1 < len(roman) and integers[roman[i]] < integers[roman[i + 1]]:
                result -= integers[roman[i]]
            else:
                result += integers[roman[i]]
        return result

    def __init__(self, s: str = '-'):
        super().__init__(s)
        self.correct_str = '-'
        try:
            i = int(s)           # пробуем int
        except ValueError:
            try:                 # пробуем float
                i = int(float(s))
            except ValueError:
                try:             # пробуем римские цифры
                    i = self._roman_to_arabic(s)
                except KeyError:
                    i = 0
        self.correct_str =  f"{i:02d}"

    def set_value(self, s: str):
        self.correct_str = s
