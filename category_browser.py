import os
import pickle

import streamlit as st

from constants import DATA_DIR


with open(os.path.join(DATA_DIR, 'sections.pkl'), 'rb') as infile:
    sections = pickle.load(infile)
    sections = sorted(sections, key=lambda x: x.code)


for sec in sections:
    with st.expander(f'{".".join(sec.code)} {str(sec.description)}', expanded=False):
        for subsec in sec.sub_sections:
            st.write(f'{".".join(subsec.code)} {str(subsec.description)}')
            for item in subsec.items:
                st.markdown(f'____{".".join(item.code) + " " + item.suffix}: {str(item.description)[:30]}')
