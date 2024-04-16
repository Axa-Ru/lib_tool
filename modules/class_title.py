import re


class TitleObject:

    def __init__(self, s):
        self._s_org = s


class AuthorName:
    def __init__(self, name):
        self._name = name
        self._name_revised = name
        self._lang = self._check_lang(name)
        self._order_fio = "lfm"                         # По умолчанию порядок ФИО
                                                        # Все возможные (разумные) комбинации, полученные из metadata:
                                                        #     fml - ИОФ
                                                        #     fl  - ИФ
                                                        #     lfm - ФИО
                                                        #     lf  - ФИ
                                                        #     l   - Ф
        self._name_revised = self._clear_author_name(name)
        self._name_revised = self._parse_name(self._name_revised)

    # Возвращает очищенное имя автора, отформатированное по правилам
    def author_name(self):
        # Расставляет инициалы по правилам русского языка
        self._name_revised = re.sub(u' (\S) (\S)$', r' \1.\2.', self._name_revised)    # Две буквы инициалов
        self._name_revised = re.sub(u' (\S) ', r' \1. ', self._name_revised)           # Один инициал в середине
        self._name_revised = re.sub(u' (\S)$', r' \1.', self._name_revised)            # Один инициал в конце
        self._name_revised = re.sub(u' Дж$', r' Дж.', self._name_revised)              # Дж без точки в конце
        return self._name_revised


    # Возвращает True, если ФИО было скорректировано
    def author_has_changed(self):
        return bool(self._name != self._name_revised)

    def _clear_author_name(self, name):
        if bool(re.search(',', name)):                  # для начала определяем, есть ли в ФИО запятая
            self._order_fio = "lfm"                     # если ДА, то первое слово ФАМИЛИЯ
        name = re.sub(u'[—–-]', '-', name)              # заменяем все Дефисы в имени на один тип
        name = re.sub(u'[\'`’]', '\'', name)            # заменяем все Апострофы в имени на один тип
        name = re.sub(u'[”«»"“\.,=?_…:\n]', ' ', name)  # убираем все знаки пунктуации и переводы строк
        name = ' '.join(name.split()).title()           # Первую букву в верхний регистр
        return name

    def _check_lang(self, name):
        # Определяем язык по фамилии
        if bool(re.search('[а-яА-Я]', name)):
            return "ru"
        if bool(re.search('[a-zA-Z]', name)):
            return "en"
        return None

    # расставляем по порядку Фамилия, Имя, Отчество
    def _parse_name(self, name):
        name = self._clear_author_name(name)
        n_list = name.split()
        f_n = m_n = l_n = ""
        if self._lang == "ru":        # Русские имена
            # разбираем комбинации
            if len(n_list) == 1:         # только фамилия
                l_n = n_list[0]          # --- Иванов
            if len(n_list) == 2:     # имя фамилия
                if len(n_list[0]) == 1:  # --- И Иванов
                    l_n = n_list[1]
                    f_n = n_list[0]
                elif len(n_list[1]) == 1: # --- Иванов И
                    f_n = n_list[1]
                    l_n = n_list[0]
                else:
                    f_n = n_list[0]
                    l_n = n_list[1]
            if len(n_list) > 2:       # фамилия имя отчество
                if len(n_list[0]) + len(n_list[1]) == 2:  # --- И И Иванов
                    l_n = n_list[2]
                    f_n = n_list[0]
                    m_n = n_list[1]
                elif len(n_list[1]) + len(n_list[2]) == 2:  # --- Иванов И И
                    l_n = n_list[0]
                    f_n = n_list[1]
                    m_n = n_list[2]
                else:                      # --- Иванов Иван Иванович
                    l_n = n_list[2]
                    f_n = n_list[0]
                    m_n = n_list[1]
        else:                              # Английские имена
            if self._order_fio == "lfm":              # Ф,ИО
                n_list[0] = re.sub(u',', '', n_list[0])   # Убираем запятую
                if len(n_list) == 1:
                    l_n = n_list[0]
                if len(self._name) == 2:
                    l_n = n_list[0]
                    f_n = n_list[1]
                if len(self._name) > 2:
                    l_n = n_list[0]
                    f_n = n_list[1]
                    m_n = n_list[2]
            else:
                if len(self._name) == 1:
                    l_n = n_list[0]
                if len(self._name) == 2:
                    l_n = n_list[1]
                    f_n = n_list[0]
                if len(self._name) > 2:
                    l_n = n_list[2]
                    f_n = n_list[0]
                    m_n = n_list[1]
        n_list = [ l_n, f_n, m_n ]
        name = " ".join(n_list)
        return name

class Series:
    def __init__(self, str):
        self._series = str
        self._series_revised = self._revise_series(str)

    def _revise_series(self, str):
        str = re.sub(u'[—–-]', '-', str)              # заменяем все Дефисы в имени на один тип
        str = re.sub(u'[\'`’]', '\'', str)            # заменяем все Апострофы в имени на один тип
        str = re.sub(u'[”«»"“\.,=?_…:\n]', ' ', str)  # убираем все знаки пунктуации и переводы строк
        return str

    def get_series(self):
        return self._series_revised

    def has_changed(self):
        return bool(self._series != self._series_revised)



class Title:
    def __init__(self, str):
        self._title = str
        self._title_revised = self._revise_title(str)

    def _revise_title(self, str):
        str = re.sub(u'[—–-]', '-', str)  # заменяем все Дефисы в имени на один тип
        str = re.sub(u'[\'`’]', '\'', str)  # заменяем все Апострофы в имени на один тип
        str = re.sub(u'[”«»"“\.,=?_…:\n]', ' ', str)  # убираем все знаки пунктуации и переводы строк
        return str

    def get_series(self):
        return self._title_revised

    def has_changed(self):
        return bool(self._title != self._title)
