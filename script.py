#!/bin/python

import random
import subprocess

from genanki import Deck, Model, Note, Package

WORD_FILE_NAME = 'words.txt'
OUTPUT_FILE_NAME = 'output.apkg'

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


def load_words(filename: str) -> list[str]:
    words = []
    with open(filename) as file:
        for line in file.readlines():
            word = line.strip()
            if len(word) > 1:
                words.append(word)
    return words


def generate_audio(input:str, filename: str) -> None:
    assert filename.endswith('.wav')
    cmd = ['cwwav', '--output', f'{filename}']
    subprocess.run(cmd, input=bytes(input, 'utf-8'))


def convert_media_file(input_filename: str, output_filename: str) -> None:
    cmd = ['ffmpeg', '-i', input_filename, output_filename]
    subprocess.run(cmd)


def main():
    words = load_words(WORD_FILE_NAME)
    data = [] # (word id, word text)
    for c in CHARSET:
        data.append(('char_' + c, c))
    for key, value in CHARDICT.items():
        data.append(('char_' + key, value))
    for word in words:
        data.append(('word_' + word, word))
    deck = Deck(*DECK_ARGS)
    model = Model(*MODEL_ARGS, **MODEL_KWARGS)
    media_files = []
    subprocess.run(['mkdir', f'{TEMP_DIR}'])
    for note_data in data:
        word_id = note_data[0]
        word_text = note_data[1]
        filepath = f'{TEMP_DIR}/{word_id}'
        generate_audio(word_text, filepath + '.wav')
        convert_media_file(filepath + '.wav', filepath + '.mp3')
        media_files.append(filepath + '.mp3')
        note = Note(
            model=model,
            fields=[word_text, f'[sound:{word_id}.mp3]']
        )
        deck.add_note(note)
    package = Package(deck)
    package.media_files = media_files
    package.write_to_file(OUTPUT_FILE_NAME)
    subprocess.run(['rm', '-rf', f'{TEMP_DIR}'])


if __name__ == '__main__':
    main()

