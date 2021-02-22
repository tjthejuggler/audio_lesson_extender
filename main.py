from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from os import path
import os
import genanki
import time
import re
#make it not have to create the chunks if we dont want chunks created/exported


#import audiodiff
#9 - needs checked
#6 transcription needs edited
#maybe language detection to find when the chime is
bell = 2
cwd = os.getcwd()
createTranscription = False
makeMod = False
createChunks = False
onlyCertainLessons = True
specific_foldernames = ['06chunks']
make_anki = True


def create_output_file(filename, output_lines):
	with open(filename + '.txt', 'w') as f:
		for item in output_lines:
			f.write("%s\n" % item)

deck_model = genanki.Model(
	163335419,
	'Simple Model With Hint',
	fields=[
		{'name': 'Question'},
		{'name': 'Answer'},
		{'name': 'Hint'},
		{'name': 'URL'},
		{'name': 'Audio'},
	],
	templates=[
		{
			'name': 'Card 1',
			'qfmt': '{{Question}}{{#Hint}}<br>{{hint:Hint}}{{/Hint}}',
			'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br><a href={{URL}}>video</a>{{Audio}}',
		},
		{
			'name': 'Card 2',
			'qfmt': '{{Answer}}{{#Hint}}<br>{{hint:Hint}}{{/Hint}}',
			'afmt': '{{FrontSide}}<hr id="answer">{{Question}}<br><a href={{URL}}>video</a>{{Audio}}',
		}
	])

def create_anki_deck(my_deck, all_audio_files, deckName):
	my_package = genanki.Package(deck)
	my_package.media_files = all_audio_files
	my_package.write_to_file(deckName+'.apkg')

def create_anki_note(word, translation, hint, tag, url, all_audio_files, mp3_name, chunks_foldername):
	all_audio_files.append(cwd+'/'+chunks_foldername+'/'+mp3_name)
	my_note = genanki.Note(
		model=deck_model,
		tags=[tag],
		fields=[word + ' ('+str(round(time.time()))+')', translation, hint, url, '[sound:'+mp3_name+']'])
	return my_note, all_audio_files
#add on to chunk names so they are more individualistic
def create_anki(filename, chunks_foldername, bell, deckName, chunk_filename_prefix): #get rid of the [0], [1] stuff
	file = open( cwd+"/transcriptions/"+filename+"_transcription.txt", "r")
	lines = file.readlines()
	file.close()
	all_audio_files = []
	for i in range(len(lines)):
		if ' - ' in lines[i]:
			line = lines[i]
			mp3_number = bell + ((i+1)*3)
			tag = 'Turkish101'+filename.split(' - ')[2]
			mp3_name = chunk_filename_prefix+'chunk'+str(mp3_number)+'.mp3'			
			split_line = line.split(' - ')
			foreign_word = split_line[0].strip('\n')
			foreign_word = re.sub(r'[^\w\s]','',foreign_word)
			translation = split_line[1]
			hint = ""
			if len(split_line) > 2:
				hint = split_line[2]
			url = ' '
			print(chunks_foldername)
			note, all_audio_files = create_anki_note(foreign_word, translation, hint, tag, url, all_audio_files, mp3_name, chunks_foldername)
			deck.add_note(note)
	create_anki_deck(deck, all_audio_files, deckName)

for filename in os.listdir(cwd+'/sources'):
	print(filename)
	filename_num = filename.split(' - ')[2].split('.')[0]
	deckName = 'wordpower101_'+filename_num
	deck = genanki.Deck(round(time.time()), deckName)
	chunks_foldername = filename.split('.mp3')[0]+"chunks"
	print(chunks_foldername.split(' - ')[2])
	if onlyCertainLessons:
		if chunks_foldername.split(' - ')[2] not in specific_foldernames:
			continue
	print(chunks_foldername)
	if chunks_foldername == 'Learn Turkish - Word Power 101 - 07chunks':
		bell = 3
		print('in 7')
	else:
		bell = 2
	#if createChunks:
	if not os.path.exists(cwd+'/'+chunks_foldername):
		os.makedirs(cwd+'/'+chunks_foldername)

	sound = AudioSegment.from_file(cwd+'/sources/'+filename, format="mp3")

	chunks = split_on_silence(
		sound,

		# split on silences longer than 1000ms (1 sec)
		min_silence_len=550,

		# anything under -16 dBFS is considered silence
		silence_thresh=-36, 

		# keep 200 ms of leading/trailing silence
		keep_silence=700
	)

	# now recombine the chunks so that the parts are at least 90 sec long
	target_length = 90 * 1000
	output_chunks = chunks[0] + chunks[1] + chunks[2]
	print(len(chunks))
	full_transcription = []
	current_transcription_line = ''
	#for chunk in chunks[1:]:
	chunk_filename_prefix = 'wp101'+filename.split('.mp3')[0].split(' - ')[2]
	if chunk_filename_prefix.startswith('wp10110'):
		chunk_filename_prefix = 'wp101010'
	if chunk_filename_prefix.startswith('wp10111'):
		chunk_filename_prefix = 'wp101011'		
	for i, chunk in enumerate(chunks):	
		if createChunks:
			chunk.export(cwd+'/'+chunks_foldername+"/"+chunk_filename_prefix+"chunk{0}.mp3".format(i), format="mp3")
	chunk_count = len([name for name in os.listdir('.') if os.path.isfile(name)])
	if makeMod or createTranscription:
		for i in range(chunk_count):
			sound = AudioSegment.from_mp3(cwd+'/'+chunks_foldername+"/"+chunk_filename_prefix+"chunk{0}.mp3".format(i))
			sound.export("transcript.wav", format="wav")
			AUDIO_FILE = "transcript.wav"
			if i > bell:
				output_chunks += sound
				if (i - bell) % 3 != 1:
					output_chunks += sound
					short_silence = AudioSegment.silent(duration=sound.duration_seconds*1000)
					output_chunks += short_silence
					if (i - bell) % 3 != 0:
						if createTranscription:
							r = sr.Recognizer()
							with sr.AudioFile(AUDIO_FILE) as source:
								audio = r.record(source)  # read the entire audio file    
								try:              
									transcription = r.recognize_google(audio, language="tr-TR")
								except:
									transcription = '???'
								print('tr', transcription)
								current_transcription_line =  transcription + ' - ' + current_transcription_line + ' - no hint'
								full_transcription += [current_transcription_line] 
								current_transcription_line = ''
				else:
					long_silence = AudioSegment.silent(duration=sound.duration_seconds*2000)
					output_chunks += long_silence
					if createTranscription:
						r = sr.Recognizer()
						with sr.AudioFile(AUDIO_FILE) as source:
							audio = r.record(source)  # read the entire audio file    
							try:              
								transcription = r.recognize_google(audio, language="en-EN")
							except:
								transcription = '???'
							print('en', transcription)
							current_transcription_line = transcription
	if createTranscription:
		create_output_file(cwd+"/transcriptions/"+filename+"_transcription", full_transcription)
	if makeMod:          
		output_chunks.export(cwd+"/mods/"+filename+"_mod.mp3", format="mp3")
	if make_anki:
		create_anki(filename, chunks_foldername, bell, deckName, chunk_filename_prefix)
