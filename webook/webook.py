
# core imports
import re
import os
from os.path import join as pjoin
import shutil
import urllib
import urllib.request
import urllib.parse
import xml.etree.cElementTree as ET
from xml.dom import minidom
import argparse
import tempfile
import uuid
from distutils.dir_util import copy_tree
import subprocess

# 3rd party imports
import bs4
from bs4 import BeautifulSoup as Soup


############################################################
# helper functions
############################################################
def which(program):
    """works like unix which"""
    # stolen from https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

############################################################
# Globals
############################################################
# WEBSITE = 'http://shinsekai.cadet-nine.org/'
ROOT = pjoin(os.path.split(os.path.abspath(__file__))[0], '..')
soup = Soup('', 'lxml')
TEMPLATE_FOLDER = pjoin(ROOT, "book_templates/epub")


############################################################
# EBook Class
############################################################
class EBook:
    TEMPLATE_FOLDER = pjoin(ROOT, "book_templates/epub")
    """An ebook basically consists of a bunsh of html files usually one pr chapter
    and a table of content that describes the relationship between the chapters"""

    def __init__(self, url, out_file='book.epup', title=None, 
            workers=5, run=True):
        if not url.startswith('http'):
            url = f'http://{url}'

        self.url = url
        self.out_file = out_file
        self.input_title = title
        self.workers = workers

        self.toc_dict = {}
        self.output_dir_obj = tempfile.TemporaryDirectory()
        self.output_dir = self.output_dir_obj.name
        copy_tree(pjoin(self.TEMPLATE_FOLDER), self.output_dir)

        self.ns = 'http://www.daisy.org/z3986/2005/ncx/'
        ET.register_namespace('', self.ns)
        self.toc_path = self.get_path("toc.ncx")
        self.toc = ET.parse(open(self.toc_path)).getroot()
        # self.nav_point_root = self.toc.find(f'{{{self.ns}}}navMap/{{{self.ns}}}navPoint')
        self.nav_point_root = self.toc.find(f'{{{self.ns}}}navMap')
        self.current_nav_point = self.nav_point_root
        self.play_order = 1

        self.content_path = self.get_path("content.opf")
        self.content = Soup(open(self.content_path), 'html.parser')
        self.content_manifest_tag = self.content.find('manifest')
        self.content_spine_tag = self.content.find('spine')

        ## TODO: parse notes and other optional stuff
        # variables expected to be scraped by self.scrape
        self.title = None
        self.first_name = None
        self.last_name = None
        self.cover_path = None

        # self.update('titlepage', self.title)
        if run:
            for progress in self.run():
                pass
            
    def run(self):
        scrape = self.scrape(self.url, self.workers)
        for progress in scrape:
            yield progress

        if self.first_name:
            self.update_author(self.first_name, self.last_name)
        if self.input_title:  # user specified title > scraped title
            self.title = self.input_title
        self.update_title(self.title)
        self.add_cover(self.cover)
        self.save(self.out_file)

    def update_title(self, title):
        self.toc.find(f'{{{self.ns}}}docTitle/{{{self.ns}}}text').text = title
        self.nav_point_root.find(f'{{{self.ns}}}navPoint/{{{self.ns}}}navLabel/{{{self.ns}}}text').text = title
        self.content.find('package').find('metadata').find('dc:title').string = title

    def update_author(self, first_name, last_name=None):
        creator = self.content.find('package').find('metadata').find('dc:creator')
        if last_name is None:
            creator.string = first_name
            creator.attrs['opf:file-as'] = first_name
        elif first_name is not None:
            creator.string = f"{first_name} {last_name}"
            creator.attrs['opf:file-as'] = f"{first_name}, {last_name}"

    def add_cover(self, cover_req):
        """cover_req can be either a url or a request"""
        # TODO jpg hardcoded, should alter files accordingly if not jpg!
        if cover_req is None:
            cover_req = 'https://vignette.wikia.nocookie.net/uncyclopedia/images/c/cf/Trollface.jpg'
        with open(self.get_path('cover.jpg'), 'wb') as cover_file:
            data = urllib.request.urlopen(cover_req).read()
            cover_file.write(data)

    def save(self, out_file):
        out_file_name, out_file_ext = os.path.splitext(out_file)
        epub_file = f'{out_file_name}.epub'
        open(self.content_path, 'w').write(self.content.prettify())
        # et_to_file(self.toc, self.toc_path)
        with open(self.toc_path, 'w') as toc_file:
            #  toc_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
            #  toc_file.write('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\n')
            #  toc_file.write('"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n\n')
            rough_string = ET.tostring(self.toc, encoding='unicode')
            rough_string = ''.join(map(str.strip, rough_string.split('\n')))
            toc_file.write(minidom.parseString(rough_string).toprettyxml("  "))
        os.unlink(self.get_path('page_template.xhtml'))

        # zip output_folder and rename it to epup_file
        tmp_file_name = str(uuid.uuid4())[:10]
        shutil.make_archive(tmp_file_name, 'zip', self.output_dir)
        os.rename(f'{tmp_file_name}.zip', epub_file)
        # TODO: test this works!!!
        if out_file_ext != '.epub':
            self.change_ebook_format(epub_file, out_file)
        self.output_dir_obj.cleanup()  # remove temporary directory

    def get_path(self, *path):
        return pjoin(self.output_dir, *path)

    def _append_soup_tag(self, target, name, text='', args=None):
        if args is None:
            args = {}
        _tag = soup.new_tag(name, **args)
        if text:
            _tag.string = text
        target.append(_tag)

    def update(self, name, heading, parent=None):
        """ updates content and table of content, needs to be called by scrape
        to add chapters, sections ect. to the Table of Content.
        If a section should be nested below another section the 'name' from
        previous evocations can be used
        """
        # if parent=None, then use last parent
        if parent is not None:
            if isinstance(parent, str):
                parent = self.toc_dict[parent]
            self.current_nav_point = parent

        # update table of content
        self.play_order += 1
        args = {"id" : f"navPoint-{self.play_order}", "playOrder" : str(self.play_order)}
        elm = ET.SubElement(self.current_nav_point, "navPoint", **args)
        nav_label = ET.SubElement(elm, "navLabel")
        ET.SubElement(nav_label, "text").text = heading
        ET.SubElement(elm, "content", src="{}.xhtml".format(name))
        self.toc_dict[name] = elm

        # update content
        args={'href' : "{}.xhtml".format(name), 'id' : name, 'media-type' : "application/xhtml+xml"}
        self._append_soup_tag(self.content_manifest_tag, "item", args=args)
        self._append_soup_tag(self.content_spine_tag, 'itemref', args={'idref' : name})

    def write_html(self, text, name, header=None):
        """ method needs to be called by scrape each evocation creates a
        '{name}.xhtml' file. 
        """

        if header is None:
            header = name
        html_file = open(self.get_path(f'{name}.xhtml'), 'w')

        chapter_soup = Soup(open(self.get_path('page_template.xhtml')), 'lxml')
        body_tag = chapter_soup.find('body')
        self._append_soup_tag(body_tag, "h3", header)
        if isinstance(text, str):
            body_tag.append(soup.new_tag('div', text))
        elif isinstance(text, bs4.element.ResultSet):
            for tag in text:
                body_tag.append(tag)
        elif isinstance(text, bs4.element.Tag):
            body_tag.append(text)
        else:
            raise ValueError("chapter_tag must be either string, bs4.element.Tag or bs4.element.ResultSet")
        html_file.write(chapter_soup.prettify())
    
    def scrape(self, url, workers):
        """
        the parse functions arbstract corotine , that needs to be in the subclass
        it should set self.total before beeing primed and yeild 'the current'
        progrees
        """
        pass

    def change_ebook_format(self, epub_file, out_file, delete_epub=True):
        if not hasattr(self, 'ebook_convert'):
            self.ebook_convert = self.__get_ebook_convert_path()
        subprocess.call((self.ebook_convert, epub_file, out_file), 
                         stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if delete_epub:
            os.unlink(epub_file)

    @staticmethod
    def __get_ebook_convert_path():
        ebook_convert = which('ebook-convert')
        if ebook_convert is None:
            import platform
            if platform.system() == 'Darwin':
                ebook_convert = "/Applications/calibre.app/Contents/console.app/Contents/MacOS/ebook-convert"
            #  elif platform.system() == "Windows":
            #  elif platform.system() == "Linux":
            if not os.path.exists(ebook_convert):
                EnviromentError("ebook-convert is not in your path")
        return ebook_convert



