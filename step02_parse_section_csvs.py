import glob
import os.path
import pickle
import sys

import numpy as np
import pandas as pd

from constants import SECTION_CSV_DIR, DATA_DIR
from objects import MainSection, SubSection, Item


def get_csv_paths():
    return sorted(list(glob.glob(os.path.join(SECTION_CSV_DIR, '*.csv'))))


def parse_6_digit_code(hs_code_str):
    hs_code_str = hs_code_str.strip()
    assert len(hs_code_str) == 7
    code1_2, code_3 = hs_code_str.split('.')
    code1 = code1_2[:2]
    code_2 = code1_2[2:]

    return code1, code_2, code_3


def parse_csv_path(csv_path):
    df = pd.read_csv(csv_path, dtype=str, index_col=0)

    df['is_section'] = ~df['hs_code'].isna() & df['suffix'].isna()
    df['is_subsection_caption'] = df['hs_code'].isna() & df['suffix'].isna()
    df['is_suffix'] = ~df['suffix'].isna()

    df['hs_code'] = df['hs_code'].ffill()

    df['hs_code'] = df['hs_code'].apply(lambda x: x.strip() if type(x) == str else x)
    df['hs_code'] = df['hs_code'].apply(lambda x: x if x else np.nan)
    df = df[~df['hs_code'].isna() | ~df['suffix'].isna()]

    df['is_main_section'] = df['is_section'] & df['hs_code'].apply(lambda x: '.' in x and x.index('.') == 2)

    main_sections = []
    df_main = df[df['is_main_section'] == True]
    for _, row in df_main.iterrows():
        hs_code = row['hs_code']
        assert len(hs_code) == 5
        code = tuple(hs_code.split('.'))
        main_sections.append(MainSection(code, row['description']))

    sub_sections = []
    df_sub = df[df['is_section'] & ~df['is_main_section']]
    for _, row in df_sub.iterrows():
        code = parse_6_digit_code(row['hs_code'])
        sub_sections.append(SubSection(code, row['description']))

    items = []
    df_item = df[df['is_suffix']]
    for _, row in df_item.iterrows():
        code = parse_6_digit_code(row['hs_code'])
        items.append(Item(code, row['suffix'], row['description']))

    main_section_map = dict((x.code, x) for x in main_sections)
    sub_section_map = dict((x.code, x) for x in sub_sections)

    for item in items:
        sub_section = sub_section_map.get(item.code)

        if not sub_section:
            sub_section = SubSection(item.code, item.description)
            sub_sections.append(sub_section)
            sub_section_map[item.code] = sub_section

        sub_section.items.append(item)

    for sub_section in sub_sections:
        main_section = main_section_map[sub_section.code[:2]]
        main_section.sub_sections.append(sub_section)

    # TODO: make sense of captions and fill them as categories or something similar

    return main_sections


def main():
    csv_paths = get_csv_paths()

    all_sections = []
    for csv_path in csv_paths:
        sections_part = parse_csv_path(csv_path)
        all_sections.extend(sections_part)

    pickle_path = os.path.join(DATA_DIR, 'sections.pkl')
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)

    with open(pickle_path, 'wb+') as outfile:
        pickle.dump(all_sections, outfile)

    print('Done!')


if __name__ == '__main__':
    sys.exit(main())
