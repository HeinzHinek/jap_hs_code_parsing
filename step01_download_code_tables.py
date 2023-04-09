import os
import re
import sys
from urllib.request import Request
from urllib.request import urlopen

import pandas as pd
from bs4 import BeautifulSoup as BS

from constants import SECTION_CSV_DIR

ENTRY_URL = 'https://www.customs.go.jp/tariff/2023_04_01/index.htm'
SECTION_LINK_REGEX = r'^data\/j_\d+\.htm$'
SECTION_LINK_BASE = 'https://www.customs.go.jp/tariff/2023_04_01/'


def get_soup_from_url(url):
    req = Request(url)
    html_page = urlopen(req).read()

    soup = BS(html_page, 'html.parser')

    return soup


def get_section_links():
    soup = get_soup_from_url(ENTRY_URL)

    link_stubs = soup.find_all('a', href=re.compile(SECTION_LINK_REGEX))

    urls = []
    for stub in link_stubs:
        url = f'{SECTION_LINK_BASE}{stub["href"]}'
        urls.append(url)

    return urls


def get_section_df(url):
    soup = get_soup_from_url(url)

    table = soup.find('table', attrs={'name': 'TV'})

    assert table is not None

    rows = table.find_all('tr')

    data = []
    for row in rows:
        cols = row.find_all('td')

        assert len(cols) == 4

        hs_code = cols[1].string
        suffix = cols[2].string
        description = cols[3].string

        data.append({
            'hs_code': hs_code,
            'suffix': suffix,
            'description': description.strip(),
        })

    df = pd.DataFrame(data, dtype=str)

    return df


def main():
    section_urls = get_section_links()

    for url in section_urls:
        print(f'Processing URL: {url}...')

        section_no = int(url.split('_')[-1].split('.')[0])

        section_df = get_section_df(url)

        file_name = f'section_{section_no:03d}.csv'
        save_path = os.path.join(SECTION_CSV_DIR, file_name)

        if not os.path.isdir(SECTION_CSV_DIR):
            os.makedirs(SECTION_CSV_DIR)

        section_df.to_csv(save_path)

    print('Done!')


if __name__ == '__main__':
    sys.exit(main())
