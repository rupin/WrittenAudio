"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import xlrd 
from pydub import AudioSegment

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
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        effects_profile_id=["large-home-entertainment-class-device"],)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open(filename, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file: '+filename)

#convertTTS("Welcome to this tutorial video which teaches you how to design a PCB using Easy E D A.", 'brownfox.mp3')

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
    #sheet.cell_value(0, 0) 
    rowcount=sheet.nrows
    for row in range (1, rowcount):
        timeslot=sheet.cell_value(row, 0)  
        sentence=sheet.cell_value(row, 1)
        filename="Row_"+str(row)+ "_"+str(timeslot)+".mp3"
        convertTTS(sentence,filename)

readXLS('Audio Sequence.xlsx')