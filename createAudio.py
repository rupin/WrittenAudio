"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import xlrd 
from pydub import AudioSegment
import io
from pydub.playback import play

# sound1 = AudioSegment.from_wav("/path/to/file1.wav")
# sound2 = AudioSegment.from_wav("/path/to/file2.wav")

# combined_sounds = sound1 + sound2
# combined_sounds.export("/output/path.wav", format="wav")

# audio_in_file = "in_sine.wav"
# audio_out_file = "out_sine.wav"

# # create 1 sec of silence audio segment
# one_sec_segment = AudioSegment.silent(duration=1000)  #duration in milliseconds

# #read wav file to an audio segment
# song = AudioSegment.from_wav(audio_in_file)

# #Add above two audio segments    
# final_song = one_sec_segment + song

# #Either save modified audio
# final_song.export(audio_out_file, format="wav")

# #Or Play modified audio
# play(final_song)

# # Advanced usage, if you have raw audio data:
# sound = AudioSegment(
#     # raw audio data (bytes)
#     data=b'…',

#     # 2 byte (16 bit) samples
#     sample_width=2,

#     # 44.1 kHz frame rate
#     frame_rate=44100,

#     # stereo
#     channels=2
# )

def convertTTS(engtext, filename):
    print(engtext)

    #return

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=engtext)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
        name= "en-US-Wavenet-A")

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16, # this gets a WAV file
        effects_profile_id=["large-home-entertainment-class-device"],)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    # with open(filename, 'wb') as out:
    #     # Write the response to the output file.
    #     out.write(response.audio_content)
    #     print('Audio content written to file: '+filename)
    return response.audio_content


def readFile(myFile):
    f = open(myFile, "r")
    p=0

    for x in f:
        filenameToSave=str(p)+".mp3"
        convertTTS(x,filenameToSave)
        p=p+1 


#readFile('textsentences.txt')

def readXLS(myfile):      
    wb = xlrd.open_workbook(myfile) 
    sheet = wb.sheet_by_index(0)
    lastTiming=0
    lastDuration=0 
    #sheet.cell_value(0, 0)
    combined_sounds = AudioSegment.silent(duration=1)
    rowcount=sheet.nrows
    for row in range (1, 3):
        timeslot=sheet.cell_value(row, 0)  
        sentence=sheet.cell_value(row, 1)
        
        #blankWAV=AudioSegment.silent(duration=emptyduration*1000)
        filename="Row_"+str(row)+ "_"+str(timeslot)+".wav"
        audioStream=convertTTS(sentence,filename)

       # audiobinaryIO=io.BytesIO(audioStream)

        # Advanced usage, if you have raw audio data:
        current_audio = AudioSegment(data=audioStream,
                            sample_width=2,
                            frame_rate=24000,
                            channels=1)
        #play(sound)
        currentDuration=current_audio.duration_seconds
        
        #The duration of the empty slot is equal to time difference between
        #the current start time, and the time the audio the sentence took.

        emptyduration=timeslot-(lastTiming+lastDuration)
        blankWAV=AudioSegment.silent(duration=emptyduration*1000,
                                    frame_rate=24000,
                                    )
        combined_sounds=combined_sounds+blankWAV+current_audio
        lastTiming=timeslot
        lastDuration=currentDuration # dummy, but this has to be initialised by the duration of the current stream
    combined_sounds.export("combined audio.wav", format="wav")
readXLS('Audio Sequence.xlsx')