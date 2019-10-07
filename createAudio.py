"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import xlrd 
from pydub import AudioSegment
import io
from pydub.playback import play
import sys, getopt, os


def convertTTS(engtext):
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
    return response.audio_content

def createFileName(row, timeslot):
    return "Row_"+str(row)+ "_"+str(timeslot)+".wav"

def createAudioFile(row, timeslot, sentence):
    filename=createFileName(row, timeslot)
    audioStream=convertTTS(sentence)
    #The response's audio_content is binary.
    with open(filename, 'wb') as out:
        # Write the response to the output file.
        out.write(audioStream)
        print('Audio content written to file: '+filename)


 
def testBlank():
    blankWAV1=AudioSegment.silent(duration=2*1000,
                                    frame_rate=24000,
                                    ) 
    blankWAV2=AudioSegment.silent(duration=2*1000,
                                    frame_rate=24000,
                                    ) 
    play(blankWAV1+blankWAV2)   



def generateAudio(myfile,pending_row=-1):      
    wb = xlrd.open_workbook(myfile) 
    sheet = wb.sheet_by_index(0)
    lastTiming=0
    lastDuration=0 
    #sheet.cell_value(0, 0)
    combined_sounds = AudioSegment.silent(duration=1)
    rowcount=sheet.nrows
    if(pending_row>0):
        if(pending_row<=rowcount):
            timeslot=sheet.cell_value(pending_row, 0)  
            sentence=sheet.cell_value(pending_row, 1) 
            createAudioFile(pending_row,timeslot, sentence)
        else:
            print("Row number "+str(pending_row)+" does not exist in the input file")
            sys.exit(2)  
    else:

        for row in range (1, rowcount):
            timeslot=sheet.cell_value(row, 0)  
            sentence=sheet.cell_value(row, 1) 
            createAudioFile(row,timeslot, sentence)      
            #audioStream=convertTTS(sentence)

       

        
    #combined_sounds.export("combined audio.wav", format="wav")


def combineFiles(inputxlsfilename, outputFileName):

        wb = xlrd.open_workbook(inputxlsfilename) 
        sheet = wb.sheet_by_index(0)
        lastTiming=0
        lastDuration=0 
        #sheet.cell_value(0, 0)
        combined_sounds = AudioSegment.silent(duration=1)
        rowcount=sheet.nrows          

        for row in range (1, rowcount):
            timeslot=sheet.cell_value(row, 0)  
            sentence=sheet.cell_value(row, 1) 
            filename=createFileName(row, timeslot)
            fileExists=os.path.exists(filename)
            if(not fileExists):
                createAudioFile(row,timeslot, sentence)
              
            current_audio=AudioSegment.from_wav(filename)   

            # # Advanced usage, if you have raw audio data:
            # current_audio = AudioSegment(data=audioStream,
            #         sample_width=2,
            #         frame_rate=24000,
            #         channels=1)
            #play(sound)
            currentDuration=current_audio.duration_seconds

            #The duration of the empty slot is equal to time difference between
            #the current start time, and the time the audio the sentence took.

            emptyduration=timeslot-(lastTiming+lastDuration)
            emptyduration=round(emptyduration,3)
            if(emptyduration<0):
                print('Audio in row '+str(row-1)+' exceeds time beyond the start time of row '+str(row))
                
                userChoice=input('Press C/c to continue, X/x to stop processing: ')
                if(userChoice.lower()=='c'):
                    pass
                else: 
                    print('Processing Halted')   
                    sys.exit(2)
            blankWAV=AudioSegment.silent(duration=emptyduration*1000,frame_rate=24000)
            
            combined_sounds=combined_sounds+blankWAV+current_audio
            lastTiming=timeslot
            lastDuration=currentDuration # dummy, but this has to be initialised by the duration of the current stream
        

        combined_sounds.export(outputFileName, format="wav")
        print(outputFileName+' Saved')


#readXLS('Audio Sequence.xlsx')


def printHelpMessage():
    print('Help Information and Parameters')
    print(" 1: Create Individual Audio files from a .xls source")
    print(' createAudio.py -x <input xls files>')
    print(" Example: createAudio.py -x 'abc.xls'")
    print()
    print(" 2: Regenerate audio for a specific row")
    print(' createAudio.py -x <input xls files> -r <row number>')
    print(" Example: createAudio.py -x 'abc.xls' -r 3")
    print()
    print(" 3: Combine Audio from existing audio files")
    print(' createAudio.py -x <input xls file> -c -o <outputfile>')
    print(" Example: createAudio.py -x 'abc.xls' -c -o 'myaudiofile.wav'")


def main(argv):
    inputfile = ''
    outputfile = ''
    
    rownum=0
    operationType='GENERATE_AUDIO'
    try:
        opts, args = getopt.getopt(argv,"hx:r:o:c")
    except getopt.GetoptError:
        printHelpMessage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printHelpMessage()
            sys.exit()      
        if opt=="-x":
            inputfile = arg
        elif opt=="-o":
            outputfile = arg
        elif opt =='-r':
            
            operationType='GENERATE_AUDIO_FOR_ROW'
            rownum=int(arg)
        elif opt=='-c':
            operationType='COMBINE_AUDIO'




    #print ('Input file is "', inputfile)
    #print ('Output file is "', outputfile)
    if(operationType=="GENERATE_AUDIO"):
        generateAudio(inputfile)
    elif(operationType=="COMBINE_AUDIO"):
        combineFiles(inputfile,outputfile)
    elif(operationType=='GENERATE_AUDIO_FOR_ROW'):
        generateAudio(inputfile,rownum)
        #pass

if __name__ == "__main__":
   main(sys.argv[1:])