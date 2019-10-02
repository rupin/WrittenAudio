"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import xlrd 

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
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL,
        name= "en-US-Wavenet-D")

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
        filename="Row_"+str(row)+ "_"+str(timeslot)
        convertTTS(sentence,filename)

readXLS('Audio Sequence.xlsx')