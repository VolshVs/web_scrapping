import os
import re

import requests
import json

from bs4 import BeautifulSoup
from fake_headers import Headers
from tqdm import trange

CURRENCY = ['€', '$']


def get_keywords(text):
    """Функция проверки по ключевому слову."""
    DESCRIPTION_KEYWORDS = "Django|Flask"
    result = re.search(DESCRIPTION_KEYWORDS, text)
    return result


def get_url():
    """Функция по запросу возвращает ссылку."""
    url_py = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    return url_py


def get_headers():
    """Функция по запросу возвращает сгенерируемые параметры."""
    headers_generator = Headers(os="win", browser="chrome").generate()
    return headers_generator


def get_data():
    """Функция парсит данные с заданного сайта
    и создает словари с этими данными."""
    main_response = requests.get(get_url(), headers=get_headers())
    main_html_data = main_response.content

    main_soup = BeautifulSoup(main_html_data, 'lxml')

    vacancy_list = main_soup.find('div', id="a11y-main-content")
    vacancies = vacancy_list.find_all('div', class_="vacancy-serp-item-body")

    vacancies_data_big = {}
    count = 0

    for vacancy_tag in vacancies:

        vacancy_link_tag = vacancy_tag.find('a', class_="bloko-link")
        vacancy_link = vacancy_link_tag['href']

        vacancy_response = requests.get(vacancy_link, headers=get_headers())
        vacancy_data = vacancy_response.content
        vacancy_soup = BeautifulSoup(vacancy_data, 'lxml')
        vacancy_text_tag = vacancy_soup.find(
            'div',
            {'data-qa': "vacancy-description"}
        )
        vacancy_text = vacancy_text_tag.text.strip()

        vacancy_title_tag = vacancy_tag.find(
            'span',
            class_="serp-item__title serp-item__title-link"
        )
        vacancy_title = vacancy_title_tag.text.strip()

        vacancy_salary_tag = vacancy_tag.find(
            'span',
            class_="bloko-header-section-2"
        )
        if vacancy_salary_tag:
            vacancy_salary = vacancy_salary_tag.text.strip()
        else:
            vacancy_salary = None

        vacancy_company_tag = vacancy_tag.find(
            'a',
            class_="bloko-link bloko-link_kind-tertiary"
        )
        vacancy_company = vacancy_company_tag.text.strip()

        vacancy_city_tag = vacancy_tag.find(
            'div',
            {'data-qa': "vacancy-serp__vacancy-address"}
        )
        if vacancy_city_tag:
            vacancy_city = vacancy_city_tag.text.strip().split(" ")[0]
        else:
            vacancy_city = None
        if get_keywords(vacancy_text):
            for el in trange(
                    0,
                    desc=f'Загрузка данных вакансии: {vacancy_title}'
            ):
                pass
            count += 1
            vacancies_data_small = {
                'vacancy_title': vacancy_title,
                'vacancy_salary': vacancy_salary,
                'vacancy_city': vacancy_city.replace(',', ''),
                'vacancy_company': vacancy_company,
                'vacancy_link': vacancy_link,
                'vacancy_text': vacancy_text
            }
            vacancies_data_big[
                f'{count}, {vacancy_title}'
            ] = vacancies_data_small
    return write_json(vacancies_data_big)


def write_json(vacancies_data):
    """Функция записи данных в json файл."""
    os.remove('data/vacancies.json')
    with open('data/vacancies.json', 'w') as json_file:
        json.dump(vacancies_data, json_file, indent=4)


def read_json():
    """Функция чтения json файла."""
    with open('data/vacancies.json', 'r') as json_file:
        print(json_file.read())


if __name__ == '__main__':
    get_data()
