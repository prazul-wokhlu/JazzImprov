import os
import pickle
from flask import Flask
from flask_ask import Ask, statement, question
from flask_ask.models import _Response
app = Flask(__name__)
ask = Ask(app, '/')
from dlib_models import download_model, download_predictor, load_dlib_models
from main_copy import main
import portfolio_methods_copy as portfolio
from music21 import *
#from midi2audio import FluidSynth
from midi import play_audio
from create_playlist import create_pl, add_to_pl
import subprocess
import os.path



os.system("!improv_rnn_generate \
--config=chord_pitches_improv \
--run_dir='/content/drive/My Drive/Colab Notebooks/acode/randommusic/run_dir' \
--output_dir='/content/drive/My Drive/Colab Notebooks/acode/randommusic/outputs/output.mid' \
--num_outputs=1 \
--primer_melody='[57]' \
--backing_chords='Am7 Am7 Dm7 Dm7 Bdim7 E7b9 Am7 Am7 Cm7 F7 Bb Bb Bdim7 E7b9 Am7 Bdim7' \
--hparams='batch_size=128,rnn_layer_sizes=[128,128]' \
--render_chords")
####?????subprocess.call()

with open("playlist_names.pkl", mode="rb") as opened_file:
    database = pickle.load(opened_file)
desc=None
dbName=None
#set file to variable midi file
midi_file=None




@app.route('/')
def homepage():
    return "Cooper Smells"

@ask.launch
def start_skill():
    welcome_message = 'Hi! Would you like to generate or play a song?'
    download_model()
    download_predictor()
    load_dlib_models()
    #play randomly generated song and assign to variable
    return question(welcome_message)

@ask.intent("AddIntent")
def add_intent():
    global desc
    global dbname
    #takes picture to return name, descriptor
    name, desc = main(database)
    path = './playlists/{}/'.format(name)
    play_audio(midi_file)
###STOPPED HERE
    if "Unknown" not in name:
        face_msg = 'Hello {}'.format(name)
        #assign name to global variable
        dbname = name
        if os.path.exists(path):
            return question(face_msg+". Do you want to add the song to your playlist?")
        else:
            #creates folder with name
            create_pl(path)
            return question(face_msg+". Do you want to add the song to your playlist?")
    else:
        return question("What's your name?")

@ask.intent("YesIntent")
def yes_intent():
    global dbname
    global midi_file
    path = './playlist/{}/'.format(dbname)
    # add numbered folder with midi in playlist
    add_to_pl(path, midi_file)
    return question(dbname+", your song has been added. Would you like to do anything else?")


@ask.intent("NameIntent")
def assign_name(name,uk,german,cogworks):
    global database
    global desc
    global dbname

    if name is not None:
        dbname=name
    elif cogworks is not None:
        dbname=cogworks
    elif uk is not None:
        dbname=uk
    elif german is not None:
        dbname=german

    #print(name,uk,german,cogworks)
    database = portfolio.create_profile(desc, dbname, database)
    face_msg = 'Hello {}'.format(dbname)
    return question(face_msg + ". Do you want to add the song to your playlist?")

@ask.intent("PlayIntent")
def play_intent(name, song_number):
    path = './playlists/{}/'.format(name)
    allmidis=os.listdir(path)
    with open(path+'{}'.format(allmidis[song_number-1]),mode="rb") as f:
        play_audio(f)
    return question("Would you like to do anything else?")


@ask.intent("DisplayIntent")
def display_intent(name, song_number):
    path = './playlists/{}/'.format(name)
    allmidis = os.listdir(path)
    with open(path + '{}'.format(allmidis[song_number-1]), mode="rb") as f:
        c = converter.parse(f)
        c.show('musicxml.png')
    return question("Would you like to do anything else?")

@ask.intent("NoIntent")
def no_intent():
    bye_text = 'Okay, goodbye'
    with open("playlist_names.pkl", mode="rb") as opened_file:
        pickle.dump(database, opened_file)
    return statement(bye_text)


if __name__ == '__main__':
    app.run(debug=True)

