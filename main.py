# -*- coding: utf-8 -*-

import sys
import os
from bs4 import BeautifulSoup
import codecs
import requests
import pdfkit


BASEURL = 'https://novelmania.com.br'
novel_name = sys.argv[1]

NEXT_CHAPTER_SELECTOR = 'a[title="Próximo capítulo"]'
CHAPTER_SELECTOR = 'div > ol > li > a'
VOLUME_SELECTOR = '#accordion > div > div.card-header'
CONTENT_CHAPTER_SELECTOR = 'div#chapter-content'
FRONT_PAGE_IMAGE_SELECTOR = 'body > div.novelmania > main > section > div.novel-head.pt-3 > div > div > div.col-md-4.text-center.text-md-left > div.novel-img > img'

HTML_SUFIX = '''
        </body>
    </html>
    '''
HTML_PREFIX = '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=0.5" />
        <title>Document</title>
    </head>
    <body>
        <div
        class="text"
        id="chapter-content"
        style="
            font-size: medium;
        "
        >
    '''


def create_front_page(url):
    front =f'''
        
        <p style="page-break-after: always;">
        <img
        style="width:100%"
            src="{url}"
        />
        </p>
  

    '''
    return front

def get_html_text(url: str):
    r = requests.get(url)
    return r.text
    

def parseHTML(html_txt:str):
    if sys.stdout.encoding is None:
        os.putenv("PYTHONIOENCODING", 'UTF-8')
    
        os.execv(sys.executable, ['python']+sys.argv)

    return  BeautifulSoup(html_txt, 'html.parser')

def make_url_title_with_name(name, base_url='https://novelmania.com.br/novels/'):
    return f'{base_url}{name}'


def get_soup_title(name:str):
    url_title = make_url_title_with_name(name.replace(' ', '-').lower())
    soup_title = parseHTML(get_html_text(url_title))
    return soup_title

def get_first_url_link(soup_title:BeautifulSoup):
   

    first_title = soup_title.select(CHAPTER_SELECTOR)[0]['href']
    return first_title

def get_all_url_link(soup_title:BeautifulSoup):

    first_title = [link['href'] for link in  soup_title.select(CHAPTER_SELECTOR)]
    return first_title


def get_all_volumes(soup_title:BeautifulSoup):

    first_title = [(link.text.strip(), link['id']) for link in  soup_title.select(VOLUME_SELECTOR)]
    return first_title

def get_all_url_link_by_volume(soup_title:BeautifulSoup, volume , id):

    volume_list = soup_title.select_one(f'div#expand-{id}')

    chap_list = {}

    for link in  volume_list.select(CHAPTER_SELECTOR):
        title_volume = link.select_one('strong')
        chap_list[title_volume.text] = BASEURL+link['href']
    
    return chap_list


def make_chapter_text_from_link(url):
    
    soup_chapter = parseHTML(get_html_text(url))
    chapter_text:BeautifulSoup = soup_chapter.select_one(CONTENT_CHAPTER_SELECTOR)

    return f'{chapter_text}'


def make_pdf_from_html_text(html_text, output='chapter.pdf', css=''):
    out = f'{HTML_PREFIX} {html_text} {HTML_SUFIX}'
    print(output)
    pdfkit.from_string(out, f'{output}', css=css)



def get_image_url(soup_title: BeautifulSoup):
    url_image = soup_title.select_one(FRONT_PAGE_IMAGE_SELECTOR)
    return create_front_page(url_image['src'])

def make_chapter_text_from_volume(name):
    soup_title = get_soup_title(novel_name)
    volume_list = get_all_volumes(soup_title)

    for volume in volume_list:
        out_text = get_image_url(soup_title)
        chapter_list = get_all_url_link_by_volume(soup_title, volume[0],volume[1])
        for chapter_name in chapter_list.keys():
            chapter_text = make_chapter_text_from_link(chapter_list[chapter_name])
            out_text += f' \n\n {chapter_text}'
        print('Crerating ', volume[0])
        make_pdf_from_html_text(out_text,f'./dist/{name}-{volume[0]}.pdf'.replace(' ','_'), './styles/novel.css')
        print('End of ', volume[0])
        with open(f'./temp/{name}-{volume[0]}.html'.replace(' ','_'), 'a') as File:
            File.write(out_text)


    #return soup_chapter.select_one(CONTENT_CHAPTER_SELECTOR)



""" 
soup_title = get_soup_title(novel_name)
volume_list = get_all_volumes(soup_title)
chapter_list = get_all_url_link_by_volume(soup_title, volume_list[0][0],volume_list[0][1])
chapter_6 = make_chapter_text_from_link(chapter_list['Capítulo 6: Lobby de Deus (2)']) """
print(make_chapter_text_from_volume(novel_name))
