#!/usr/bin/python3
# coding=utf-8# -*- coding: utf-8 -*-

__author__ = 'axa'

import zipfile
import sys

sys.path.append('./modules')

from modules import g_var
from modules.class_letter import Letter
from modules.class_settings import Settings
from modules.utils import *
from modules.metadata import get_metadata
from modules.class_TitleBook import AuthorName, SeriesName, SeriesIndex, BookName


# sys.path.append('./')
# sys.path.append('/home/axa/Stuff/traum3/lib_tool')

# -----------------------------------------------------------
# Загружаем списки имён, отчеств, фамилий
# Делаем аналогичные списки с замененной буквой "ё" на "е"
# global array_yo_firstname, array_ye_firstname, \
#        array_yo_middlename, array_ye_middlename, \
#        array_yo_lastname, array_ye_lastname
def load_yeyo_arrays():
    with open(ss.s_yo_firstname) as file:
        g_var.array_yo_firstname = [row.strip() for row in file]
    g_var.array_ye_firstname = [row.replace('ё', 'е') for row in g_var.array_yo_firstname]

    with open(ss.s_yo_middlename) as file:
        g_var.array_yo_middlename = [row.strip() for row in file]
    g_var.array_ye_middlename = [row.replace('ё', 'е') for row in g_var.array_yo_middlename]

    with open(ss.s_yo_lastname) as file:
        g_var.array_yo_lastname = [row.strip() for row in file]
    g_var.array_ye_lastname = [row.replace('ё', 'е') for row in g_var.array_yo_lastname]
    return


# -----------------------------------------------------------
# Разворачиваем zip архивы и конвертируем в epub
def load_zips():
    if ss.a_unzip_archives:
        # По всем архивам, распаковываем
        for zip_root, dirs, files in os.walk(ss.s_upd_zip):
            for zip_fn in files:
                print(zip_root + '/' + zip_fn)
                with zipfile.ZipFile(zip_root + '/' + zip_fn, "r") as zip_ref:
                    zip_ref.extractall(ss.s_upd_fb2)
                    os.remove(zip_root + '/' + zip_fn)
                    fb2_to_epub()
    return


# -----------------------------------------------------------
# Конвертирую все книги fb2 в epub
def fb2_to_epub():
    # Конвертируем книги из win1251 в utf-8
    # xmllint --recover --format --encode "UTF-8" "$NB" -o "${NB}.utf8"
    for fb2_root, dirs, files in os.walk(ss.s_upd_fb2):
        for fb2_fn in files:
            print(fb2_root + '/' + fb2_fn)
            fb2_utf8_fn = fb2_fn[:-4] + '_utf8' + fb2_fn[-4:]
            cmd_to_utf8 = ss.e_xmllint + ' "' + fb2_root + '/' + fb2_fn + '" -o "' + fb2_root + '/' + fb2_utf8_fn + '"'
            os.system(cmd_to_utf8)
            os.remove(fb2_root + '/' + fb2_fn)
            # Читаем метаданные книги fb2
            fb2_meta = get_metadata(fb2_root + '/' + fb2_utf8_fn)
            # пропускаем ненужные языки
            lang = fb2_meta.lang
            if lang not in ss.a_skip_lang:
                # Берем первого автора
                # author = fb2_meta.author_list[0]
                author = AuthorName(' '.join(fb2_meta.author_list[0]))
                series = SeriesName(fb2_meta.series)
                series_index = SeriesIndex(str(fb2_meta.series_index))
                if len(series.get_value()) == 0:
                    series_index.set_value("-")
                book_name = BookName(fb2_meta.title)
                title = author.get_author_last_name() + ' ' + series_index.get_value() + ' '  + book_name.get_value()
                dest_path = ss.s_lib_exp + '/' + lang + '/' + author.get_value()[0] + '/' + author.get_value() + '/' + series.get_value()
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                # Вызов команды конвертации
                print(lang, title)
                cmd_fb2_epub = ss.e_fb2_epub + ' "' + fb2_root + '/' + fb2_utf8_fn + '" ' + '"' + dest_path + '/' + title + '.epub' + '"'
                os.system(cmd_fb2_epub)
    return


# -----------------------------------------------------------
# добавляем книги из каталога epub
def epub_to_epub():
    for book_root, dirs, files in os.walk(ss.s_upd_epub):
        for book in files:
            print(book_root + '/' + book)
            try:
                epub_meta = get_metadata(book_root + '/' + book)
            except:
                continue
            # title = book_meta.title
            lang = epub_meta.lang
            lang = lang.lower()[0:2] if lang else 'unk'
            # Пропускаем ненужные языки
            if lang not in ss.a_skip_lang:
                # в author записывается без всякой системы
                try:
                    s = epub_meta.author_list[0]
                except:
                    s = 'Unknown'
                if not s or s == 'N/A':
                    s = 'Unknown'
                author = AuthorName(s)
                series = SeriesName(epub_meta.series)
                series_index = SeriesIndex(str(epub_meta.series_index))
                if len(series.get_value()) == 0 and series_index.get_value() == '00':
                    # Попытаемся получить название и номер серии из названия книги
                    series_array = look_series_from_filename(book)
                    series.set_value(series_array[0])
                    series_index.set_value(series_array[1])
                if len(series.get_value()) == 0:
                    series_index.set_value("-")
                book_name = BookName(epub_meta.title)

                # Если название книги слишком длинное - то укорачиваем его.
                # Нужно перенсти это в класс BookName
                # if len(title) > ss.s_len_title:
                #     title = title.split('.')[0][0:ss.s_len_title]
                # title_divider = ' - ' if not series else ' %02d ' % int(series_index)
                # title = author[0] + title_divider + title
                # l = author_full_name[0]

                title = author.get_author_last_name() + ' ' + series_index.get_value() + ' '  + book_name.get_value()
                dest_path = ss.s_lib_exp + '/' + lang + '/' + author.get_value()[0] + '/' + author.get_value() + '/' + series.get_value()
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                # Переместим файл
                mv_book(book_root + '/' + book, dest_path + '/' + title + '.epub')
                print(lang, title)


# -----------------------------------------------------------
if __name__ == '__main__':
    ss = Settings()
    logging.basicConfig(filename=ss.log_file, level=logging.INFO)
    # Сначала конвертируем и обрабатываем отдельные файлы fb2 и epub
    # if ss.a_convert2epub:
    #     fb2_to_epub()
    if ss.a_add_epubs:
        epub_to_epub()
    # Раскрываем и конвертируем архивы книг по одному
    load_zips()

    # exit(1)

    # Добавляем в библиотеку вновь прибывшие книги
    if ss.a_append_new_book:
        print("Добавляю русские книги")
        mv3books(ss.s_lib_exp_ru, ss.s_lib_ru)
        print("Добавляю английские книги")
        mv3books(ss.s_lib_exp_en, ss.s_lib_en)

    if ss.a_process_library:
        author_count = series_count = books_count = 0
        duplicated_authors = duplicated_books = 0
        # Цикл по всем русским буквам
        for index, letter in enumerate(ss.a_process_letter_ru):
            processCatalog = ss.s_lib_ru + '/' + letter
            if os.path.isdir(processCatalog):  # проверяем, что существует каталог
                logging.info('Обрабатываю -> %s', processCatalog)
                print('Обрабатываю ->', processCatalog)

                l1 = Letter(ss, processCatalog)

                if ss.b_adjust_book_name:
                    duplicated_authors, duplicated_books = l1.adjustBooks()
                if ss.b_adjust_author_name:
                    duplicated_authors += l1.mergeSameAutors()

                l1.cleanUp()

                author_count += l1._authorsCount
                series_count += l1._seriesCount
                books_count += l1._booksCount

        print("Русские книги")
        print("  Удалено:")
        print("     дубликатов авторов - ", duplicated_authors)
        print("     дубликатов книг - ", duplicated_books)
        print("Всего Авторов: ", author_count)
        print("Серий: ", series_count)
        print("Книг: ", books_count)

        author_count = series_count = books_count = 0
        # Цикл по всем английским буквам
        for index, letter in enumerate(ss.a_process_letter_en):
            processCatalog = ss.s_lib_en + '/' + letter
            if os.path.isdir(processCatalog):  # проверяем, что существует каталог
                logging.info('Обрабатываю -> %s', processCatalog)
                print('Обрабатываю ->', processCatalog)
                l1 = Letter(ss, processCatalog)

                if ss.b_adjust_book_name:
                    l1.adjustBooks()
                if ss.b_adjust_author_name:
                    l1.mergeSameAutors()
                l1.cleanUp()

                author_count += l1._authorsCount
                series_count += l1._seriesCount
                books_count += l1._booksCount

        print("Английские книги")
        print("Авторов: ", author_count)
        print("Серий: ", series_count)
        print("Книг: ", books_count)
