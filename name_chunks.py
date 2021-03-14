# import random
import os
import shutil

#make a copy of the invoice to work with

# from pydub import AudioSegment
# from pydub.silence import split_on_silence

cwd = os.getcwd()

def get_this_bell(num):
	to_return = 2
	if num == 7:
		to_return = 3
	return to_return

def get_transcript(transcription_name):
	file = open(cwd+"/transcriptions/"+transcription_name, "r")
	lines = file.readlines()
	file.close()
	return lines

def create_named_file(folder_num, file_num_to_name, name, language):
	print(str(file_num_to_name), name)
	chunks_folder_name = cwd+"/Learn Turkish - Word Power 101 - "+"{0:0=2d}".format(folder_num)+"chunks/"
	chunks_file_name = "wp1010"+str(folder_num)+"chunk"+str(file_num_to_name)+".mp3"
	src = chunks_folder_name + chunks_file_name
	dst = cwd+"/"+language+"/"+name+".mp3"
	shutil.copy(src,dst)

def main():
	for i in range(2,12):
		file_num_to_name = get_this_bell(i) + 1
		transcription_name = "Learn Turkish - Word Power 101 - "+"{0:0=2d}".format(i)+".mp3_transcription.txt"
		transcription = get_transcript(transcription_name)
		for line in transcription:
			split_line = line.split(' - ')
			create_named_file(i, file_num_to_name, split_line[1], 'en')
			file_num_to_name += 1
			create_named_file(i, file_num_to_name, split_line[0], 'tr')
			file_num_to_name += 2

main()