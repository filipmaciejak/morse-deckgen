#!/bin/python

import random
import subprocess

from genanki import Deck, Model, Note, Package

WORD_FILE_NAME = 'words.txt'

DECK_ID = random.randrange(1 << 30, 1 << 31)
DECK_NAME = 'Morse Code'

MODEL_ID = random.randrange(1 << 30, 1 << 31)
MODEL_NAME = 'Simple Model'

TEMP_DIR = '/tmp/morse-deckgen-data'

charset = 'abcdefghijklmnopqrstuvwxyz0123456789'

chardict = {
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

words = []
with open(WORD_FILE_NAME) as word_file:
    for line in word_file.readlines():
        if len(line) > 1:
            words.append(line)

data = [] # (code name, input / display name, file name)
for c in charset:
    data.append((c, c, 'char_' + c))
for key, value in chardict.items():
    data.append((key, value, 'char_' + key))
for word in words:
    data.append((word, word, 'word_' + word))

my_deck = Deck(
    DECK_ID,
    DECK_NAME
)

my_model = Model(
    MODEL_ID,
    MODEL_NAME,
    fields=[
        {'name': 'Answer'},
        {'name': 'Recording'}
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': 'What does this say?<br>{{Recording}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}'
        }
    ]
)

media_files = []
subprocess.run(['mkdir', f'{TEMP_DIR}'])
for note_data in data:
    
    code_name = note_data[0]
    raw_text = note_data[1]
    file_name = note_data[2]

    file_path = f'{TEMP_DIR}/{file_name}'
    
    # generate audio file
    subprocess.run(['cwwav', '--output', f'{file_path}.wav'], input=bytes(raw_text, 'utf-8'))
    
    # convert the audio from wav to mp3
    subprocess.run(['ffmpeg', '-i', f'{file_path}.wav', f'{file_path}.mp3'])
    
    # add file to media_files
    media_files.append(f'{file_path}.mp3')
    
    # create a note
    note = Note(
        model=my_model,
        fields=[raw_text, f'[sound:{file_name}.mp3]']
    )
    
    my_deck.add_note(note)

my_package = Package(my_deck)
my_package.media_files = media_files

my_package.write_to_file('output.apkg')

subprocess.run(['rm', '-rf', f'{TEMP_DIR}'])

