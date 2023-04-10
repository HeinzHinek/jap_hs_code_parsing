import glob
import os.path
import pickle
import sys
from dataclasses import dataclass
from typing import Optional

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


@dataclass
class Row:
    hs_code: Optional[str]
    suffix: Optional[str]
    description: Optional[str]

    def __post_init__(self):
        if self.hs_code is np.nan or (type(self.hs_code) is str and self.hs_code.strip() == ''):
            self.hs_code = None
        else:
            self.hs_code = self.hs_code.strip()

        if self.suffix is np.nan or (type(self.suffix) is str and self.suffix.strip() == ''):
            self.suffix = None
        else:
            self.suffix = self.suffix.strip()

        if self.description is np.nan or \
                (type(self.description) is str and self.description.strip() == ''):
            self.description = None
        else:
            self.description = self.description.strip()

    @property
    def is_section(self):
        return self.hs_code is not None and len(self.hs_code) == 5 and self.suffix is None

    @property
    def is_sub_section(self):
        return self.hs_code is not None and len(self.hs_code) == 7 and self.suffix is None

    @property
    def is_item(self):
        return self.suffix is not None and self.description is not None

    @property
    def is_caption(self):
        return self.hs_code is None and self.suffix is None and self.description is not None

    @property
    def parsed_code(self):
        parts = self.hs_code.split('.')

        assert len(parts) == 2

        if self.is_section:
            assert all(len(part) == 2 for part in parts)
            return tuple(parts)
        elif self.is_sub_section or self.is_item:
            assert len(parts[0]) == 4 and len(parts[1]) == 2
            return tuple([parts[0][:2], parts[0][2:], parts[1]])

        raise RuntimeError('Unexpected value')


def parse_csv_path(csv_path):
    df = pd.read_csv(csv_path, dtype=str, index_col=0)

    sections = []

    curr_section = None
    for idx, row_ in df.iterrows():
        row = Row(**row_.to_dict())

        if row.is_section or not curr_section:
            if row.is_item:
                prev_row = Row(**df.loc[idx - 1].to_dict())
                if prev_row.is_caption:
                    section = MainSection(row.parsed_code[:2], prev_row.description)
                else:
                    section = MainSection(row.parsed_code[:2], row.description)
                curr_section = section
                sections.append(section)
                sub_section = SubSection(row.parsed_code, row.description)
                section.sub_sections.append(sub_section)
                item = Item(sub_section.code, row.suffix, row.description)
                sub_section.items.append(item)
                continue

            if row.is_sub_section:
                prev_row = Row(**df.loc[idx - 1].to_dict())
                if prev_row.is_caption:
                    section = MainSection(row.parsed_code[:2], prev_row.description)
                else:
                    section = MainSection(row.parsed_code[:2], row.description)
                curr_section = section
                sections.append(section)
                sub_section = SubSection(row.parsed_code, row.description)
                section.sub_sections.append(sub_section)
                continue

            if not row.is_section:
                # initial file rows only
                continue

            if not row.description:
                curr_section = None
                continue

            curr_section = MainSection(row.parsed_code, row.description)
            sections.append(curr_section)
            continue

        if row.is_sub_section:
            sub_section = SubSection(row.parsed_code, row.description)
            curr_section.sub_sections.append(sub_section)
            continue

        if row.is_item:
            if not curr_section.sub_sections:
                prev_row = Row(**df.loc[idx - 1].to_dict())
                if prev_row.is_caption:
                    sub_section = SubSection(row.parsed_code, prev_row.description)
                else:
                    sub_section = SubSection(row.parsed_code, row.description)
                curr_section.sub_sections.append(sub_section)

            sub_section = curr_section.sub_sections[-1]
            item = Item(sub_section.code, row.suffix, row.description)
            sub_section.items.append(item)
            continue

        if row.is_caption:
            # TODO: handle these
            continue

    return sections


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
