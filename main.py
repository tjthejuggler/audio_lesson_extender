from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import os
#import audiodiff
#2,7,8,9,10,11 - needs checked
#maybe language detection to find when the chime is
bell = 2
cwd = os.getcwd()
createTranscription = False
makeMod = False
createChunks = False
onlyCertainLessons = True
specific_foldernames = ['02chunks']
make_anki = True


def create_output_file(filename, output_lines):
	with open(filename + '.txt', 'w') as f:
		for item in output_lines:
			f.write("%s\n" % item)



deckName = lines[0].replace(' ','_')

deck = genanki.Deck(round(time.time()), deckName)

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

def create_anki_deck(my_deck, all_audio_files):
	my_package = genanki.Package(deck)
	my_package.media_files = all_audio_files
	my_package.write_to_file(deckName+'.apkg')

def create_anki_note(word, translation, hint, tag, url, all_audio_files, mp3_name, chunks_foldername):
	all_audio_files.append(cwd+'/'+chunks_foldername+'/'+mp3_name)
	my_note = genanki.Note(
		model=deck_model,
		tags=[tag],
		fields=[word + ' ('+str(round(time.time()))+')', translation, hint, url, '[sound:'+audio_file+']'])
	return my_note, all_audio_files
	
def create_anki(filename, chunks_foldername, bell): #get rid of the [0], [1] stuff
	file = open( cwd+"/transcriptions/"+filename+"_transcription.txt", "r")
	lines = file.readlines()
	file.close()
	all_audio_files = []
	for i in range((bell+1), len(lines)):
		if ' - ' in lines[i]:
			line = lines[i]
			split_line = line.split(' - ')
			foreign_word = split_line[0].strip('\n')
			foreign_word = re.sub(r'[^\w\s]','',foreign_word)
			translation = split_line[1]
			hint = ""
			if len(split_line) > 2:
				hint = split_line[2]
			note, all_audio_files = create_anki_note(foreign_word, translation, hint, tag, url, all_audio_files, mp3_name, chunks_foldername)
			deck.add_note(note)

	create_anki_deck(deck, all_audio_files)

for filename in os.listdir(cwd+'/sources'):
	chunks_foldername = filename.split('.mp3')[0]+"chunks"
	print(chunks_foldername.split(' - ')[2])
	if onlyCertainLessons:
		if chunks_foldername.split(' - ')[2] not in specific_foldernames:
			continue
	print(chunks_foldername)
	if chunks_foldername == 'Learn Turkish - Word Power 101 - 07chunks':
		bell = 3
		print('in 7')
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
	for i, chunk in enumerate(chunks):
		if createChunks:
			chunk.export(cwd+'/'+chunks_foldername+"/chunk{0}.mp3".format(i), format="mp3")
		sound = AudioSegment.from_mp3(cwd+'/'+chunks_foldername+"/chunk{0}.mp3".format(i))
		sound.export("transcript.wav", format="wav")
		AUDIO_FILE = "transcript.wav"
		if i > bell:
			output_chunks += chunk
			if (i - bell) % 3 != 1:
				output_chunks += chunk
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
		create_anki(filename, chunks_foldername, bell)
