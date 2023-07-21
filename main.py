from bs4 import BeautifulSoup
import requests
import openai
import random
from BOT_const import *


openai.api_key = api_key


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(model=model, messages=messages, temperature=0,)
    return response.choices[0].message["content"]


def get_links(page):
    links = []
    url = "https://miem.hse.ru/edu/ce/news/page" + str(page) + ".html"
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.text, 'html.parser')
    link = soup.find_all('h2', class_="first_child")
    for k in link:
        l = k.find('a', class_="link link_dark2 no-visited").get('href')
        if "https://miem.hse.ru/" in l:
            links.append(l)
    return links


def get_last_page():
    url = "https://miem.hse.ru/edu/ce/news/page1.html"
    pages = []
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.text, 'html.parser')
    pages_num = soup.find_all('a', class_="pages__page")
    for k in pages_num:
        pages.append(k.text.strip())  # массив всех страниц
    last_page = pages[-1]  # номер последней страницы
    return last_page


def get_page_and_link():
    flag = False
    while flag is False:
        cur_page = random.randint(1, int(get_last_page()))  # получаем рандомный номер страницы
        count_news = len(get_links(cur_page))
        if count_news !=0:
            flag = True
    page_links = get_links(cur_page) # получаем список ссылок на этой рандомной странице
    cur_news = random.randint(1, count_news)  # берем рандомную новость на первой странице, так как возможно, что на ней не 10 новостей, как обычно
    new_url = page_links[cur_news-1] # получаем ссылку этой новости
    return new_url


def make_message_for_user(url):
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.text, 'html.parser')
    try:
        title = soup.find('h1', class_="post_single").text
    except AttributeError:
        title = soup.find('h1', class_="post-title").text
    try:
        text = soup.find('div', class_="lead-in").text
    except AttributeError:
        try:
            text = soup.find('div', class_="first_child").text
        except AttributeError:
            try:
                text = soup.find_all('p', class_="text")
                k = []
                for p in text:
                    k.append(p.text)
                text = "".join([str(p) for p in k])
            except AttributeError:
                try:
                    text = soup.find('div', class_="post__text")
                except AttributeError:
                    try:
                        text = soup.find('div', class_="post__text").text.strip()
                    except AttributeError:
                        text = ""
    if len(text) == 0:
        return 0
    else:
        prompt2 = gpt_message + text
        sum = get_completion(prompt2)
        result = title + "\n" + sum + "\n" + "Читать подробнее: " + url
        return result