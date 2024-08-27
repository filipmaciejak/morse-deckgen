#!/bin/python

import random
import subprocess

from genanki import Deck, Model, Note, Package

WORD_FILE_NAME = 'words.txt'
OUTPUT_FILE_NAME = 'output.apkg'
OUTPUT_MEDIA_FORMAT = 'mp3'

DECK_ID = random.randrange(1 << 30, 1 << 31)
DECK_NAME = 'Morse Code'
DECK_ARGS = [DECK_ID, DECK_NAME]

MODEL_ID = random.randrange(1 << 30, 1 << 31)
MODEL_NAME = 'Simple Model'
MODEL_ARGS = [MODEL_ID, MODEL_NAME]
MODEL_KWARGS = {
    'fields':[
        {'name': 'Answer'},
        {'name': 'Recording'}
    ],
    'templates':[
        {
            'name': 'Card 1',
            'qfmt': 'What does this say?<br>{{Recording}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}'
        }
    ]
}

TEMP_DIR = '/tmp/morse-deckgen-data'

CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789'

CHARDICT = {
    'period': '.',
    'comma': ',',
    'question_mark': '?',
    'apostrophe': '\'',
    'exclamation_point': '!',
    'slash': '/',
    'open_parenthesis': '(',
    'close_parenthesis': ')',
    'colon': ':',
    'semicolon': ';',
    'double_dash': '=',
    'plus': '+',
    'minus': '-',
    'underscore': '_',
    'quotation_mark': '"',
    'dollar_sign': '$',
    'at': '@'
}


def load_words_from_file(filename: str) -> dict[str, str]:
    words = dict()
    with open(filename) as file:
        for line in file.readlines():
            word = line.strip()
            if len(word) > 1:
                words['word_' + word] = word
    return words


def generate_audio(input:str, filename: str) -> None:
    assert filename.endswith('.wav')
    cmd = ['cwwav', '--output', f'{filename}']
    subprocess.run(cmd, input=bytes(input, 'utf-8'))


def convert_media_file(input_filename: str, output_filename: str) -> None:
    if input_filename == output_filename:
        return
    cmd = ['ffmpeg', '-i', input_filename, output_filename]
    subprocess.run(cmd)


def create_note(word_id: str, word_text:str, model: Model) -> Note:
    note = Note(
        model=model,
        fields=[word_text, f'[sound:{word_id}.{OUTPUT_MEDIA_FORMAT}]']
    )
    return note


def main():
    data = dict()
    data.update({'char_' + c: c for c in CHARSET})
    data.update(CHARDICT)
    data.update(load_words_from_file(WORD_FILE_NAME))

    deck = Deck(*DECK_ARGS)
    model = Model(*MODEL_ARGS, **MODEL_KWARGS)

    media_files = []
    subprocess.run(['mkdir', f'{TEMP_DIR}'])
    for key, value in data.items():
        filepath = f'{TEMP_DIR}/{key}'
        generate_audio(value, filepath + '.wav')
        convert_media_file(filepath + '.wav', filepath + '.' + OUTPUT_MEDIA_FORMAT)
        media_files.append(filepath + '.' + OUTPUT_MEDIA_FORMAT)
        note = create_note(key, value, model)
        deck.add_note(note)
    package = Package(deck)
    package.media_files = media_files
    package.write_to_file(OUTPUT_FILE_NAME)
    subprocess.run(['rm', '-rf', f'{TEMP_DIR}'])


if __name__ == '__main__':
    main()

