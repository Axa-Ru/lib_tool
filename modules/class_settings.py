#!/usr/bin/python3
# coding=utf-8

__author__ = 'axa'
ver = "v2402"

import os
import configparser
import datetime

class Settings:
    """
    Класс хранения установок.
    Все переменные определяются в соответствующих переменных файла ".ini"
    Описание смотри в файле ./doc/lib_tool.odt
    """

    aDeleteAfterAdd: bool  # Удаляет книгу после добавления в библиотеку
    aRewriteLog: bool      # Перезаписывает старый Log file
    aUpdateEpubInfo: bool  # Перезаписывает информацию об авторе в epub.
    aFb2epub: bool         # Конвертирует из fb2 в epub (не реализовано)
    aAppend: bool          # Добавляет книги из "AppendRoot"
    aProcessLibrary: bool  # Обрабатывает пакетно всю библиотеку.
                           # Удобно применять при слиянии нескольких библиотек и
                           # после ручной правки библиотеки
    aShowCover: bool       # включает показ обложки в epub

    # Секция описывает правила преобразования имен авторов и названий книг
    nCapitalizeDir: bool    # Первую букву каждого слова в названии директории
                            # переводит в верхний регистр
    nAdjustBookName: bool   # Удаляет из названия книги лишние пробелы,
                            # запрещенные символы (,!?'"`)
    nAdjustAuthorName: bool # Приводит названия авторов к нормальному виду
                            #    Иванов И.А.
                            #    Иванов Иван Андреевич
                            #    Иванов Иван А.

    def __init__(self, ini="traum.ini"):
        if not os.path.exists(ini): print('Cant open "%s" File ' % ini); quit()
        config = configparser.ConfigParser()
        config.read(ini)
        # [Exec]
        self.e_fb2_epub = config.get('Exec', 'e_fb2_epub')
        self.e_xmllint = config.get('Exec', 'e_xmllint')

        # [Store]
        self.s_lib_version = config.get('Store', 's_lib_version')
        self.s_lib_root = config.get('Store', 's_lib_root')
        self.s_lib = config.get('Store', 's_lib')
        self.s_lib_ru = config.get('Store', 's_lib_ru')
        self.s_lib_en = config.get('Store', 's_lib_en')
        self.s_upd_zip = config.get('Store', 's_upd_zip')
        self.s_upd_epub = config.get('Store', 's_upd_epub')
        self.s_upd_fb2 = config.get('Store', 's_upd_fb2')
        self.s_lib_exp = config.get('Store', 's_lib_exp')
        self.s_lib_exp_en = config.get('Store', 's_lib_exp_en')
        self.s_lib_exp_ru = config.get('Store', 's_lib_exp_ru')
        self.s_tmp_dir = config.get('Store', 's_tmp_dir')
        self.s_yo_firstname = config.get('Store', 's_yo_firstname')
        self.s_yo_middlename = config.get('Store', 's_yo_middlename')
        self.s_yo_lastname = config.get('Store', 's_yo_lastname')
        self.s_len_series = config.getint('Store', 's_len_series')
        self.s_len_title = config.getint('Store', 's_len_title')

        self.s_log = config.get('Store', 's_log')
        now = datetime.datetime.now()
        self.log_file = f"{self.s_log:s}-{now.day}-{now.hour}-{now.minute}.log"

        # [LibAction]
        self.a_process_library = config.getboolean('LibAction', 'a_process_library')
        self.a_process_letter_en = config.get('LibAction', 'a_process_letter_en')
        self.a_process_letter_ru = config.get('LibAction', 'a_process_letter_ru')
        self.a_unzip_archives = config.getboolean('LibAction', 'a_unzip_archives')
        self.a_convert2epub = config.getboolean('LibAction', 'a_convert2epub')
        self.a_append_new_book = config.getboolean('LibAction', 'a_append_new_book')
        self.a_ye_yo = config.getboolean('LibAction', 'a_ye_yo')
        self.a_merge_same_autor = config.getboolean('LibAction', 'a_merge_same_autor')
        self.a_rewrite_log = config.getboolean('LibAction', 'a_rewrite_log')
        self.a_delete_after_add = config.getboolean('LibAction', 'a_delete_after_add')
        self.a_skip_lang = config.get('LibAction', 'a_skip_lang').split(',')
        self.a_add_epubs = config.getboolean('LibAction', 'a_add_epubs')

        # [BookInfo]
        self.b_update_epub_info = config.getboolean('BookInfo', 'b_update_epub_info')
        self.b_show_cover = config.getboolean('BookInfo', 'b_show_cover')
        self.b_capitalize_dir_words = config.getboolean('BookInfo', 'b_capitalize_dir_words')
        self.b_adjust_book_name = config.getboolean('BookInfo', 'b_adjust_book_name')
        self.b_adjust_author_name = config.getboolean('BookInfo', 'b_adjust_author_name')
        self.b_adjust_lang = config.getboolean('BookInfo', 'b_adjust_lang')
        self.b_adjust_series = config.getboolean('BookInfo', 'b_adjust_series')
        pass
