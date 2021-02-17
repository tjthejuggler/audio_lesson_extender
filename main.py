from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import os
import audiodiff

#maybe language detection to find when the chime is
bell = 0
cwd = os.getcwd()

def create_output_file(filename, output_lines):
    with open(filename + '.txt', 'w') as f:
        for item in output_lines:
            f.write("%s\n" % item)


for filename in os.listdir(cwd+'/sources'):
    sound = AudioSegment.from_file(cwd+'/sources/'+filename, format="mp3")
    chunks = split_on_silence(
        sound,

        # split on silences longer than 1000ms (1 sec)
        min_silence_len=450,

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
        if bell == 0:
            chunk.export("chunk{0}.mp3".format(i), format="mp3")
            if audiodiff("chunk{0}.mp3".format(i), "bell.mp3"):
                bell = i
        else:
            chunk.export("chunk{0}.mp3".format(i), format="mp3")
            # convert mp3 file to wav                                                       
            sound = AudioSegment.from_mp3("chunk{0}.mp3".format(i))
            sound.export("transcript.wav", format="wav")

            
            # transcribe audio file                                                         
            AUDIO_FILE = "transcript.wav"


            if i > bell:
                output_chunks += chunk
                if (i - bell) % 3 != 1:
                    output_chunks += chunk
                    short_silence = AudioSegment.silent(duration=sound.duration_seconds*1000)
                    output_chunks += short_silence
                    if (i - bell) % 3 != 0:
                        r = sr.Recognizer()
                        with sr.AudioFile(AUDIO_FILE) as source:
                            audio = r.record(source)  # read the entire audio file    
                            try:              
                                transcription = r.recognize_google(audio, language="tr-TR")
                            except:
                                transcription = '???'
                            current_transcription_line =  transcription + ' - ' + current_transcription_line + ' - no hint'
                            full_transcription += [current_transcription_line] 
                            current_transcription_line = ''
                else:
                    long_silence = AudioSegment.silent(duration=sound.duration_seconds*2000)
                    output_chunks += long_silence
                    r = sr.Recognizer()
                    with sr.AudioFile(AUDIO_FILE) as source:
                        audio = r.record(source)  # read the entire audio file    
                        try:              
                            transcription = r.recognize_google(audio, language="en-EN")
                        except:
                            transcription = '???'
                        current_transcription_line = transcription

            # if len(output_chunks[-1]) < target_length:
            #     output_chunks[-1] += chunk
            # else:
            #     # if the last output chunk is longer than the target length,
            #     # we can start a new one
            #     output_chunks.append(chunk)



    create_output_file(cwd+"/transcriptions/"+filename+"_transcription", full_transcription)            
    output_chunks.export(cwd+"/mods/"+filename+"_mod.mp3", format="mp3")
    break

# now your have chunks that are bigger than 90 seconds (except, possibly the last one)




# use the audio file as the audio source                                        
