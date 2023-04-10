import os
import pickle
import sys

import tensorflow_hub as hub
from tensorflow_text import SentencepieceTokenizer  # required

from constants import DATA_DIR


def main():
    model = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual/3')

    pickle_path = os.path.join(DATA_DIR, 'sections.pkl')

    with open(pickle_path, 'rb') as infile:
        sections = pickle.load(infile)

    for section in sections:
        section.embedding = model([section.description]).numpy()[0]

        for sub_section in section.sub_sections:
            sub_section.embedding = model([section.description]).numpy()[0]

            for item in sub_section.items:
                item.embedding = model([section.description]).numpy()[0]

    save_path = os.path.join(DATA_DIR, 'sections_with_embedding.pkl')

    with open(save_path, 'wb+') as outfile:
        pickle.dump(sections, outfile)

    print('Done!')


if __name__ == '__main__':
    sys.exit(main())
