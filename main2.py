#this uses existing chunks and either 
#makes individual lessons either for tr or en speakers,
#either in order or random
#either inidividual lessons or all combined
#optional length
#it also outputs transcripts it gets from current transcripts
import random
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

cwd = os.getcwd()


should_be_random = True
should_be_individual_lessons = False #make this be a list of 
max_words = 10000
output_transcript = True

def add_silences_to_word_pair(first_word, second_word):
	word_list_to_return = []
	long_silence = AudioSegment.silent(duration=second_word.duration_seconds*2000)
	short_silence = AudioSegment.silent(duration=second_word.duration_seconds*1000)
	word_list_to_return = first_word + long_silence + second_word + short_silence + second_word + long_silence + second_word + short_silence + second_word
	return word_list_to_return

def get_word_list(learner_type,this_subdir_num,file_number):
	word_list_to_return = []
	chunks_foldername = 'Learn Turkish - Word Power 101 - '+this_subdir_num+'chunks'
	chunk_filename_prefix = 'wp101'+ this_subdir_num
	if chunk_filename_prefix.startswith('wp10110'):
		chunk_filename_prefix = 'wp101010'
	if chunk_filename_prefix.startswith('wp10111'):
		chunk_filename_prefix = 'wp101011'	
	first_word = AudioSegment.from_mp3(cwd+'/'+chunks_foldername+"/"+chunk_filename_prefix+"chunk"+str(file_number)+".mp3")
	second_word = AudioSegment.from_mp3(cwd+'/'+chunks_foldername+"/"+chunk_filename_prefix+"chunk"+str(file_number+1)+".mp3")
	if learner_type != 'en':
		temp = second_word
		second_word = first_word
		first_word = temp
	return add_silences_to_word_pair(first_word, second_word)

def get_transcript(learner_type,this_subdir_num,i):
	transcript_line_to_return = ''
	file = open( cwd+"/transcriptions/Learn Turkish - Word Power 101 - "+this_subdir_num+".mp3_transcription.txt", "r")
	lines = file.readlines()
	file.close()
	#if learner_type == 'en':
	transcript_line_to_return = lines[i]
	print(transcript_line_to_return)
	return transcript_line_to_return

def create_output_file(filename, output_lines):
	with open(filename + '.txt', 'w') as f:
		for item in output_lines:
			f.write("%s" % item)

def main():
	output_audio_list_of_word_lists = []
	learner_type = 'en'
	full_transcript = []

	for subdirs, dirs, files in os.walk(cwd):		
		for subdir in subdirs.split('\n'):
			if 'chunks' in subdir:
				print('subdir', subdir)
				this_subdir_num = subdir.split(' - ')[2].split('chunks')[0]
				print('this_subdir_num',this_subdir_num)
				if this_subdir_num == '07':
					this_folders_bell_number = 3
				else:
					this_folders_bell_number = 2
				print(this_folders_bell_number)
				this_path, this_dirs, this_files = next(os.walk(subdir))
				file_count = len(this_files)
				print(file_count)
				this_folders_post_bell_file_count = file_count - (this_folders_bell_number+1)
				print('this_folders_post_bell_file_count',this_folders_post_bell_file_count)
				print('this_folders_post_bell_file_count/3',this_folders_post_bell_file_count/3)
				for i in range (int(this_folders_post_bell_file_count/3)):
					file_number = (this_folders_bell_number+1)+(i*3)
					print('file_number', file_number)
					output_audio_list_of_word_lists += [get_word_list(learner_type,this_subdir_num,file_number)]
					full_transcript.append(get_transcript(learner_type,this_subdir_num,i))
					if len(output_audio_list_of_word_lists) > 300:
						break
					print('export_audio',len(output_audio_list_of_word_lists))
	audio_and_transcript_zipped = list(zip(output_audio_list_of_word_lists, full_transcript))
	if should_be_random:
		random.shuffle(audio_and_transcript_zipped)
	output_audio_list_of_word_lists, full_transcript = zip(*audio_and_transcript_zipped)
	print('len(output_audio_list_of_word_lists)', len(output_audio_list_of_word_lists))
	rand_num = str(random.randint(0, 100000))
	create_output_file(cwd+"/stranscriptions/"+rand_num+"_stranscription", full_transcript[:-160])
	print('transcript created')
	export_audio = AudioSegment.silent(duration=2000)
	for item in output_audio_list_of_word_lists[:-160]:
		export_audio += item

	print('export_audio', export_audio)
	export_audio.export(cwd+"/smods/"+rand_num+"_smod.mp3", format="mp3")

for i in range(5):
	main()
	