#!/bin/python3

from class_TitleBook import AuthorName, SeriesName, SeriesIndex, BookName

#
#  Тестирование классов
#
def test_class_title():
    # инициализируем пути к спискам ФИО
    AuthorName.load_names_arrays('/home/axa/Stuff/book/lib_tool/profiles/firstname.yo',
                               '/home/axa/Stuff/book/lib_tool/profiles/middlename.yo',
                                 '/home/axa/Stuff/book/lib_tool/profiles/lastname.yo',
                                 '/home/axa/Stuff/book/lib_tool/profiles/firstname.txt')

    def print_tst_case_autor(s: str, a: AuthorName):
        print('\n=====================    Тестируем класс AuthorName')
        print('было       :', s)
        print('стало      :', a.get_value())
        print('фамилия    :', a.get_author_last_name())
        print('поправлено :', a.is_changed())
        print('\n')

    def print_tst_case_series(s: str, sn: SeriesName):
        print('=====================    Тестируем класс SeriesName')
        print('было       :', s)
        print('стало      :', sn.get_value())
        print('поправлено :', sn.is_changed())
        print('\n')

    def print_tst_case_book(s: str, bn: BookName):
        print('=====================    Тестируем класс BookName')
        print('было       :', s)
        print('стало      :', bn.get_value())
        print('поправлено :', bn.is_changed())
        print('\n')

    def print_tst_case_index(s: str, si: SeriesIndex):
        print('=====================    Тестируем класс SeriesIndex')
        print('было       :', s)
        print('стало      :', si.get_value())
        print('поправлено :', si.is_changed())
        print('\n')


    s = 'О`брайан’ А    Дж'
    author = AuthorName(s)
    print_tst_case_autor(s, author)

    s = 'Аксенов Федор Семенович'
    author = AuthorName(s)
    print_tst_case_autor(s, author)

    author.replace_yeyo()
    print_tst_case_autor(s, author)

    s = "Вот --- ”«»\"\"\"\"“.,=?_…:  так—–-аЯ \nсерия..."
    series = SeriesName(s)
    print_tst_case_series(s, series)

    s = "есть такая\n\n\n работа —–- родину:*#^===&&? защищать    (Сборник)"
    book_name = BookName(s)
    print_tst_case_book(s, book_name)

    s = "Государство\n\n\n Солнца (с иллюстрациями В.Милашевского)   (Сб)"
    book_name = BookName(s)
    print_tst_case_book(s, book_name)

    s = "3"
    series_index = SeriesIndex(s)
    print_tst_case_index(s, series_index)

    s = ""
    series_index = SeriesIndex(s)
    print_tst_case_index(s, series_index)

    s = "03"
    series_index = SeriesIndex(s)
    print_tst_case_index(s, series_index)

    s = "XI"
    series_index = SeriesIndex(s)
    print_tst_case_index(s, series_index)

    s = "dsxi"
    series_index = SeriesIndex(s)
    print_tst_case_index(s, series_index)


if __name__ == '__main__':
    test_class_title()
