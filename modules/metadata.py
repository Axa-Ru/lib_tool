from lxml import etree
import hashlib
from .exceptions import BadFormat, UnknownFormatException
from .fb2 import Fb2
from .epub2 import Epub2
from .epub3 import Epub3
from .fb2genres import fb2genres
from .exceptions import BadLanguage
from .utils import str_to_list, replace_keywords, split_ext, normalize_path


def _get_ebook(file):
    ebook = None

    if file.lower().endswith(('.fb2')):
        ebook = Fb2(file)

    elif file.lower().endswith('.epub'):
        ebook = Epub2(file)
        if ebook.version[:1] == '3':
            ebook = Epub3(file)
    else:
        raise UnknownFormatException

    return ebook


def get_metadata(file):
    ebook = _get_ebook(file)
    meta = Metadata()

    # meta.identifier = ebook.get_identifier()
    meta.title = ebook.get_title()
    meta.author_list = ebook.get_author_list()
    meta.series = ebook.get_series()
    meta.series_index = ebook.get_series_index()
    meta.lang = ebook.get_lang()
    # meta.description = ebook.get_description()
    meta.tag_list = ebook.get_tag_list()
    # meta.translator_list = ebook.get_translator_list()
    # (meta.cover_file_name, meta.cover_media_type, meta.cover_image_data) = ebook.get_cover_data()
    # meta.format = ebook.get_format()
    # meta.format_version = ebook.get_format_version()
    # meta.file = file
    # meta.file_created = get_file_creation_time(file)
    # meta.file_modified = get_file_modified_time(file)

    # Get publish info for FB2
    # if meta.format == 'fb2':
    #     meta.publish_info.title = ebook.get_publish_title()
    #     meta.publish_info.publisher = ebook.get_publish_publisher()
    #     meta.publish_info.city = ebook.get_publish_city()
    #     meta.publish_info.year = ebook.get_publish_year()
    #     meta.publish_info.series = ebook.get_publish_series()
    #     meta.publish_info.series_index = ebook.get_publish_series_index()
    #     meta.publish_info.isbn = ebook.get_publish_isbn()

    return meta


def set_metadata(file, meta):
    ebook = _get_ebook(file)

    ebook.set_title(meta.title)
    ebook.set_author_list(meta.author_list)
    ebook.set_series(meta.series_count)
    ebook.set_series_index(meta.series_index)
    ebook.set_lang(meta.lang)
    ebook.set_tag_list(meta.tag_list)
    ebook.set_translator_list(meta.translator_list)
    ebook.set_cover_data(meta.cover_file_name, meta.cover_media_type, meta.cover_image_data)

    # Set publish info for FB2
    if meta.format == 'fb2':
        ebook.set_publish_title(meta.publish_info.title)
        ebook.set_publish_publisher(meta.publish_info.publisher)
        ebook.set_publish_city(meta.publish_info.city)
        ebook.set_publish_year(meta.publish_info.year)
        ebook.set_publish_series(meta.publish_info.series_count)
        ebook.set_publish_series_index(meta.publish_info.series_index)
        ebook.set_publish_isbn(meta.publish_info.isbn)

    ebook.save()


class PublishInfo:
    def __init__(self):
        self.title = None
        self.publisher = None
        self.year = None
        self.city = None
        self.series = None
        self.series_index = None
        self.isbn = None

    def __str__(self):
        result = []
        for key in self.__dict__.keys():
                result.append('{0}: {1}'.format(key, self.__dict__[key]))

        return '[' + ', '.join(result) + ']'

class Metadata:
    def __init__(self):
        self.identifier = None
        self.title = None
        self.author_list = []
        self.author_sort_list = []
        self.translator_list = []
        self.series = None
        self.series_index = None
        self.tag_list = []
        self.description = None
        self.lang = None
        self.format = None
        self.format_version = None
        self.cover_image_data = None
        self.cover_file_name = None
        self.cover_media_type = None
        self.file = None
        self.publish_info = PublishInfo()
        self.file_created = None
        self.file_modified = None

    def author_list_to_string(self):
        return ', '.join(self.author_list) if self.author_list else []

    def translator_list_to_string(self):
        return ', '.join(self.translator_list) if self.translator_list else []

    def tag_list_to_string(self):
        return ', '.join(self.tag_list) if self.tag_list else []

    def tag_description_list_to_string(self, lang='ru'):
        if lang not in ('ru', 'en'):
            raise BadLanguage('Only ru and en languages supports')
        result = []
        tree = etree.fromstring(fb2genres, parser=etree.XMLParser())
        xpath_str = '//fbgenrestransfer/genre/subgenres/subgenre[@value="{}"]/genre-descr[@lang="{}"]/@title'
        for tag in self.tag_list:
            node = tree.xpath(xpath_str.format(tag, lang))
            try:
                result.append(str(node[0]))
            except IndexError:
                result.append(tag)
        return ', '.join(result)

    def set_author_list_from_string(self, s):
        self.author_list = str_to_list(s)

    def set_translator_list_from_string(self, s):
        self.translator_list = str_to_list(s)

    def set_tag_list_from_string(self, s):
        self.tag_list = str_to_list(s)

    def get_filename_by_pattern(self, filename_pattern, author_pattern, padnum=2):
        d = { '#Title': '', '#Series': '', '#Abbrseries': '',
              '#Number': '', '#Padnumber': '',
              '#Author': '', '#Authors': '', '#Translator': '', '#Atranslator': '', '#Atranslators':'',
              '#Bookid': '', '#Md5': ''
            }

        d['#Title'] = self.title
        d['#Author'] = self._get_authors_by_pattern(author_pattern, short=True)
        d['#Authors'] = self._get_authors_by_pattern(author_pattern, short=False)
        d['#Bookid'] = self.identifier

        if self.series:
            d['#Series'] = self.series
            abbr = ''.join(w[0] for w in self.series.split())
            d['#Abbrseries'] = abbr

            if self.series_index:
                d['#Number'] = str(self.series_index)
                d['#Padnumber'] = str(self.series_index).strip().zfill(padnum)

        if len(self.translator_list) > 0:
            try:
                d['#Translator'] = self.translator_list[0].split()[-1]
            except:
                d['#Translator'] = ''
        d['#Atranslator'] = self._get_translators_by_pattern(author_pattern, short=True)
        d['#Atranslators'] = self._get_translators_by_pattern(author_pattern, short=False)

        with open(self.file, 'rb') as f:
            data = f.read()
            d['#Md5'] = hashlib.md5(data).hexdigest()

        cases_d = {}
        for key, value in d.items():
            cases_d[key.lower()] = value.lower()
            cases_d[key.upper()] = value.upper()
        d.update(cases_d)

        file_ext = split_ext(self.file)
        result = replace_keywords(filename_pattern, d).strip() + file_ext 
 
        return normalize_path(result)


    def _get_authors_by_pattern(self, pattern, short=True):
        if len(self.author_list) == 0:
            return ''

        if short and len(self.author_list) > 1:
            if self.lang == 'ru':
                return replace_keywords(pattern, self._get_person_dict(self.author_list[0])) + ' и др'
            else:
                return replace_keywords(pattern, self._get_person_dict(self.author_list[0])) + ', et al'
        else:
            result = []
            for author in self.author_list:
                result.append(replace_keywords(pattern, self._get_person_dict(author)))
            return ', '.join(result)


    def _get_translators_by_pattern(self, pattern, short=True):
        if len(self.translator_list) == 0:
            return ''

        if short and len(self.translator_list) > 1:
            if self.lang == 'ru':
                return replace_keywords(pattern, self._get_person_dict(self.translator_list[0])) + ' и др'
            else:
                return replace_keywords(pattern, self._get_person_dict(self.translator_list[0])) + ', et al'
        else:
            result = []
            for translator in self.translator_list:
                result.append(replace_keywords(pattern, self._get_person_dict(translator)))
            return ', '.join(result)


    def _get_person_dict(self, person):
        d = { '#f': '', '#m': '', '#l': '', '#fi': '', '#mi':'' }
 
        person_parts = person.split()
        if len(person_parts) == 3:
            d['#f'] = person_parts[0]
            d['#m'] = person_parts[1]
            d['#l'] = person_parts[2]
        elif len(person_parts) == 2:
            d['#f'] = person_parts[0]
            d['#l'] = person_parts[1]
        else:
            d['#l'] = person

        if len(d['#f']) > 0:
            d['#fi'] = d['#f'][0] + '.'
        if len(d['#m']) > 0: 
            d['#mi']= d['#m'][0] + '.'
        return d

    def __str__(self):
        result = []
        for key in self.__dict__.keys():
            if key == 'cover_image_data':
                if self.__dict__[key] is not None:
                    result.append('{0}: {1}'.format(key, '<binary_data>')) 
                else:
                    result.append('{0}: {1}'.format(key, 'None')) 
            else:
                result.append('{0}: {1}'.format(key, self.__dict__[key]))

        return '[' + ', '.join(result) + ']'

    
    

