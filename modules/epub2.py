import os
import posixpath
import tempfile
import shutil
import urllib.parse
from lxml import etree, html
from .myzipfile import ZipFile, is_zipfile, ZIP_DEFLATED, ZIP_STORED
from .utils import xstr, translate_series_index

ns_map = {
        'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
        'opf': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

class Epub2():
    def __init__(self, file):
        self.file = file
        self.opf = None
        self.content_root = None
        self.tree = None
        self.version = None
        self.cover_href = None
        self.cover_data = None
        
        if not is_zipfile(self.file):
            raise Exception('"{}" is not epub file.'.format(self.file))
        
        content = self._get_file_content('META-INF/container.xml')
        tree = etree.fromstring(content)
        self.opf = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns_map)[0]
        self.content_root = os.path.dirname(self.opf) + '/'
        if self.content_root == '/':
            self.content_root = ''
        content = self._get_file_content(self.opf)
        self.tree = etree.fromstring(content)
        self.version = self.tree.xpath('/opf:package/@version', namespaces=ns_map)[0]

    ########## Getters ##########
    def get_title(self):
        node = self._get('opf:metadata/dc:title')
        if node is not None:
            return xstr(node.text)
    
    def get_author_list(self):
        result = []
        node_list = self._get_all('opf:metadata/dc:creator[@opf:role="aut" or not(@opf:role)]')
        for node in node_list: result.append(xstr(node.text).strip())
        return result
   
    def get_series(self):
        retval = ''
        node = self._get('opf:metadata/opf:meta[@name="calibre:series"]')
        if node is not None:
            if 'content' in node.attrib:
                try:
                    retval = xstr(node.attrib['content'])
                except:
                    retval = ''
        return retval



    def get_series_index(self):
        node = self._get('opf:metadata/opf:meta[@name="calibre:series_index"]')
        if node is not None:
            if 'content' in node.attrib:
                si = xstr(node.attrib['content'])
                retval = translate_series_index(si)
            return retval

    def get_lang(self):
        node = self._get('opf:metadata/dc:language')
        if node is not None:
            return xstr(node.text)
    
    def get_tag_list(self):
        result = []
        node_list = self._get_all('opf:metadata/dc:subject')
        for node in node_list: result.append(xstr(node.text))
        return result

    def get_description(self):
        return xstr(self._get('opf:metadata/dc:description/text()'))

    def get_translator_list(self):
        result = []
        node_list = self._get_all('opf:metadata/dc:creator[@opf:role="trl"]')
        for node in node_list: result.append(xstr(node.text))
        return result

    def get_format(self):
        return 'epub'
    
    def get_format_version(self):
        return self.version

    def get_identifier(self):
         return  xstr(self._get('opf:metadata/dc:identifier/text()'))
         
    def get_cover_data(self):
        cover_id = None
        media_type = None
        href = None
        data = None

        node = self._get('opf:metadata/opf:meta[@name="cover"]')
        if node is not None:
            if 'content' in node.attrib: cover_id = node.attrib['content']
        if cover_id:
            node = self._get('opf:manifest/opf:item[@id="{0}"]'.format(cover_id))
            if node is not None:
                if 'href' in node.attrib: href = node.attrib['href']
                if 'media-type' in node.attrib: media_type = node.attrib['media-type']
            if href: data = self._get_file_content(self.content_root + urllib.parse.unquote(href))
        else:
            (href, media_type, data) = self._get_cover_from_first_element()
        return (href, media_type, data)

    def _get_cover_from_first_element(self):
        media_type = None
        href = None
        img_href = None
        data = None

        nodes = self._get_all('opf:manifest/opf:item')
        for node in nodes:
            if node is not None:
                if 'media-type' in node.attrib: 
                    if node.attrib['media-type'] == 'application/xhtml+xml':
                        media_type = node.attrib['media-type']
                        break

        if media_type:
            href = node.attrib['href'] 
            if href:
                content = self._get_file_content(self.content_root + urllib.parse.unquote(href))
                tree = html.fromstring(content)
                nodes = tree.xpath('//img')
                for node in nodes:
                    if 'src' in node.attrib:
                        img_href = node.attrib['src']
                        if img_href.lower().endswith(('.jpg', '.jpeg')): media_type = 'image/jpeg'
                        elif img_href.lower().endswith(('.png')): media_type = 'image/png'
                        else: media_type = None
                        break
                if not img_href:
                    nodes = tree.xpath('//image')
                    for node in nodes:
                        if 'xlink:href' in node.attrib:
                            img_href = node.attrib['xlink:href']
                            if img_href.lower().endswith(('.jpg', '.jpeg')): media_type = 'image/jpeg'
                            elif img_href.lower().endswith(('.png')): media_type = 'image/png'
                            else: media_type = None
                            break

                if media_type and img_href:
                    base_path = posixpath.join(self.content_root, os.path.dirname(href))
                    img_path = posixpath.normpath(posixpath.join(base_path, img_href))
                    data = self._get_file_content(img_path)
                    return (img_path, media_type, data)
        return (None, None, None)

    ########## Setters ##########
    def set_title(self, title):
        node = self._get('opf:metadata/dc:title')
        if node is None:
            meta_node = self._get('opf:metadata')
            node = self._sub_element(meta_node, 'dc:title')
        node.text = title

    def set_author_list(self, author_list):
        node_list = self._get_all('opf:metadata/dc:creator[@opf:role="aut" or not(@opf:role)]')
        for node in node_list: node.getparent().remove(node)
        meta_node = self._get('opf:metadata')
        for author in author_list:
            if author:
                node = self._sub_element(meta_node, 'dc:creator')
                node.attrib['{http://www.idpf.org/2007/opf}role'] = 'aut'
                node.text = author

    def set_series(self, series):
        node = self._get('opf:metadata/opf:meta[@name="calibre:series"]')
        if series:
            if node is None:
                meta_node = self._get('opf:metadata')
                node = self._sub_element(meta_node, 'opf:meta')
                node.attrib['name'] = 'calibre:series'
            node.attrib['content'] = series
        else:
            if node is not None:
                node.getparent().remove(node)
    
    def set_series_index(self, series_index):
        node = self._get('opf:metadata/opf:meta[@name="calibre:series_index"]')
        if series_index:
            if node is None:
                meta_node = self._get('opf:metadata')
                node = self._sub_element(meta_node, 'opf:meta')
                node.attrib['name'] = 'calibre:series_index'
            node.attrib['content'] = str(series_index)
        else:
            if node is not None:
                node.getparent().remove(node)

    def set_lang(self, lang):
        node = self._get('opf:metadata/dc:language')
        if node is None:
            meta_node = self._get('opf:metadata')
            node = self._sub_element(meta_node, 'dc:language')
        node.text = lang

    def set_tag_list(self, tag_list):
        node_list = self._get_all('opf:metadata/dc:subject')
        for node in node_list: node.getparent().remove(node)
        meta_node = self._get('opf:metadata')
        for tag in tag_list:
            if tag:
                node = self._sub_element(meta_node, 'dc:subject')
                node.text = tag
                node.tail = '\n'

    def set_translator_list(self, translator_list):
        node_list = self._get_all('opf:metadata/dc:creator[@opf:role="trl"]')
        for node in node_list: node.getparent().remove(node)
        meta_node = self._get('opf:metadata')
        for translator in translator_list:
            if translator:
                node = self._sub_element(meta_node, 'dc:creator')
                node.attrib['{http://www.idpf.org/2007/opf}:role'] = 'trl'
                node.text = translator

    def set_cover_data(self, href, media_type, data):
        (href, _, _) = self.get_cover_data()

        if href and data:
            self.cover_href = href
            self.cover_data = data

    ########## Service methods ##########
    def save(self):
        temp_dir = tempfile.mkdtemp(prefix='em')
        dest_file = os.path.join(temp_dir, os.path.basename(self.file))
        src_zip = ZipFile(self.file, mode='r')
        dest_zip = ZipFile(dest_file, mode='w')
        try:
            for f in src_zip.infolist():
                if f.filename == self.opf:
                    dest_zip.writestr(self.opf, etree.tostring(self.tree, encoding='utf-8',
                                      method='xml', xml_declaration=True, pretty_print=True))

                elif f.filename == self.content_root + urllib.parse.unquote(xstr(self.cover_href)):
                    if self.cover_data:
                        dest_zip.writestr(self.content_root + urllib.parse.unquote(self.cover_href), self.cover_data)
                elif f.filename == 'mimetype':
                    buf = src_zip.read(f)
                    dest_zip.writestr(f.filename, buf, ZIP_STORED)
                else:
                    buf = src_zip.read(f)
                    dest_zip.writestr(f.filename, buf, ZIP_DEFLATED)
            src_zip.close()
            dest_zip.close()
            shutil.copyfile(dest_file, self.file)
            shutil.rmtree(temp_dir)
        except Exception as e:
            src_zip.close()
            dest_zip.close()
            shutil.rmtree(temp_dir)
            raise Exception(repr(e))

    def _get_file_content(self, filename):
        zipfile = ZipFile(self.file)
        content = zipfile.read(filename)
        zipfile.close()
        return content

    def _get_all(self, xpath_str):
        return self.tree.xpath(xpath_str, namespaces=ns_map)

    def _get(self, xpath_str):
        node_list = self.tree.xpath(xpath_str, namespaces=ns_map)
        for node in node_list:
            return node

    def _sub_element(self, parent, name):
        ns, tag = name.split(':')
        return etree.SubElement(parent, etree.QName(ns_map[ns], tag))
