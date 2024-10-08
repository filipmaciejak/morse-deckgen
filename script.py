#!/bin/python

import random
import subprocess
from tempfile import TemporaryDirectory
from tqdm import tqdm

from genanki import Deck, Model, Note, Package

from cwwav_wrapper import main as cwwav


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


def generate_audio_wav(input: str, filename: str) -> None:
    assert filename.endswith('.wav')
    cwwav(output=filename, input=input)


def generate_audio(input: str, filename: str) -> None:
    if filename.endswith('.wav'):
        generate_audio_wav(input, filename)
        return
    filename_wav = '.'.join(filename.split('.')[:-1]) + '.wav'
    generate_audio_wav(input, filename_wav)
    convert_media_file(filename_wav, filename)


def convert_media_file(input_filename: str, output_filename: str) -> None:
    if input_filename == output_filename:
        return
    cmd = ['ffmpeg', '-i', input_filename, output_filename]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_note(filename: str, word_text:str, model: Model) -> Note:
    note = Note(
        model=model,
        fields=[word_text, f'[sound:{filename}]']
    )
    return note


def main():
    data = dict()
    data.update({'char_' + c: c for c in CHARSET})
    data.update(CHARDICT)
    data.update(load_words_from_file(WORD_FILE_NAME))

    deck = Deck(*DECK_ARGS)
    model = Model(*MODEL_ARGS, **MODEL_KWARGS)

    with TemporaryDirectory() as dir:
        media_files = []
        for key, value in tqdm(data.items()):
            filename = f'{key}.{OUTPUT_MEDIA_FORMAT}'
            filepath = f'{dir}/{filename}'
            generate_audio(value, filepath)
            media_files.append(filepath)
            note = create_note(filename, value, model)
            deck.add_note(note)
        package = Package(deck)
        package.media_files = media_files
        package.write_to_file(OUTPUT_FILE_NAME)


if __name__ == '__main__':
    main()

