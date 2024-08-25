#!/bin/python

import random
import subprocess

from genanki import Deck, Model, Note, Package

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

words = [
    'the',
    'be',
    'to',
    'of',
    'and',
    'in',
    'that',
    'have',
    'it',
    'for',
    'not',
    'on',
    'with',
    'he',
    'as',
    'you',
    'do',
    'at',
    'this',
    'but',
    'his',
    'by',
    'from',
    'they',
    'we',
    'say',
    'her',
    'she',
    'or',
    'an',
    'will',
    'my',
    'one',
    'all',
    'would',
    'there',
    'their',
    'what',
    'so',
    'up',
    'out',
    'if',
    'about',
    'who',
    'get',
    'which',
    'go',
    'me',
    'when',
    'make',
    'can',
    'like',
    'time',
    'no',
    'just',
    'him',
    'know',
    'take',
    'people',
    'into',
    'year',
    'your',
    'good',
    'some',
    'could',
    'them',
    'see',
    'other',
    'than',
    'then',
    'now',
    'look',
    'only',
    'come',
    'its',
    'over',
    'think',
    'also',
    'back',
    'after',
    'use',
    'two',
    'how',
    'our',
    'work',
    'first',
    'well',
    'way',
    'even',
    'new',
    'want',
    'because',
    'any',
    'these',
    'give',
    'day',
    'most',
    'us'
]

data = [] # (display name, input, file name)
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
    
    display_name = note_data[0]
    audio_generator_input = note_data[1]
    file_name = note_data[2]

    file_path = f'{TEMP_DIR}/{file_name}'
    
    # generate audio file
    subprocess.run(['cwwav', '--output', f'{file_path}.wav'], input=bytes(audio_generator_input, 'utf-8'))
    
    # convert the audio from wav to mp3
    subprocess.run(['ffmpeg', '-i', f'{file_path}.wav', f'{file_path}.mp3'])
    
    # add file to media_files
    media_files.append(f'{file_path}.mp3')
    
    # create a note
    note = Note(
        model=my_model,
        fields=[display_name, f'[sound:{file_name}.mp3]']
    )
    
    my_deck.add_note(note)

my_package = Package(my_deck)
my_package.media_files = media_files

my_package.write_to_file('output.apkg')

subprocess.run(['rm', '-rf', f'{TEMP_DIR}'])

