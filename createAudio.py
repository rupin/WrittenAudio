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
from math import ceil
from pathlib import Path
from onlineservices.TTS import TTS
import argparse

#print()



def createFileName(row, timeslot):
    return "Row_"+str(row)+ "_"+str(timeslot)+".wav"

def createAudioFile(row, timeslot, sentence):
    filename=createFileName(row, timeslot)
    newTTSObject=TTS(TTS.SERVICE_PROVIDER_GOOGLE)
    audioStream=newTTSObject.convertTTSGoogle(sentence)
    #The response's audio_content is binary.
    with open(filename, 'wb') as out:
        # Write the response to the output file.
        out.write(audioStream)
        print('Audio content written to file: '+filename)


 




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
            #audioStream=TTS.convertTTSGoogle(sentence)

       

        
    #combined_sounds.export("combined audio.wav", format="wav")


def combineFiles(inputxlsfilename, outputFileName):

        wb = xlrd.open_workbook(inputxlsfilename) 
        sheet = wb.sheet_by_index(0)
        lastTiming=0
        lastDuration=0 
        operations=[]
        #sheet.cell_value(0, 0)
        combined_sounds = None
        rowcount=sheet.nrows
        silentDurationStarttime=0
        

        for row in range (1, rowcount):
            timeslot=sheet.cell_value(row, 0)  
            sentence=sheet.cell_value(row, 1) 
            filename=createFileName(row, timeslot)
            fileExists=os.path.exists(filename)
            if(not fileExists):
                createAudioFile(row,timeslot, sentence)
            #print(filename) 
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
            #print(currentDuration)
            emptyduration=timeslot-(lastTiming+lastDuration)
            #print(timeslot)
            emptyduration=round(emptyduration,3) * 1000
            if(emptyduration<0):
                print('Audio in row '+str(row-1)+' exceeds time beyond the start time of row '+str(row))
                
                userChoice=input('Press C/c to continue, X/x to stop processing: ')
                if(userChoice.lower()=='c'):
                    pass
                else: 
                    print('Processing Halted')   
                    sys.exit(2)
            blankWAV=AudioSegment.silent(duration=emptyduration,frame_rate=24000)
            silentDurationEndTime=silentDurationStarttime+emptyduration

            if(emptyduration>3000):
                silentduration={}
                silentduration['type']='S'
                silentduration['start']=silentDurationStarttime               
                silentduration['end']=silentDurationEndTime
                operations.append(silentduration)

            audioduration={}
            audioduration['type']='A'
            audioduration['start']=silentDurationEndTime
            audioduration['end']=silentDurationStarttime=round(silentDurationEndTime+(currentDuration*1000),3)
            operations.append(audioduration)

            
           
            if(combined_sounds is None):

                combined_sounds=blankWAV+current_audio
            else:
                combined_sounds=combined_sounds+blankWAV+current_audio
            lastTiming=timeslot
            lastDuration=currentDuration # dummy, but this has to be initialised by the duration of the current stream
            #silenDurationStarttime=audioduration['end']

        combined_sounds.export(outputFileName, format="wav")
        print(outputFileName+' Saved')
        #print(operations)
        return operations



#readXLS('Audio Sequence.xlsx')
def overlayMusic(audioFile, musicFile, audioMarks, musicscaling=-10):
    #print(audiofile)
    #print(musicFile)
    #print(audiomarks)
    transition=1000
    audioFileRef=AudioSegment.from_wav(audioFile)
    musicFileRef=AudioSegment.from_wav(musicFile)
    audioFileDuration=audioFileRef.duration_seconds
    musicfileDuration=musicFileRef.duration_seconds
    #print(musicfileDuration)
    #print(audioFileDuration)
    if(audioFileDuration>musicfileDuration):
        factor=ciel(audioFileDuration/musicfileDuration)
        musicFileRef=musicFileRef*factor #duplicate the music file
    musicFileRef=(musicFileRef[0:audioFileDuration*1000])+musicscaling # trim any excess
    musicfileDuration=musicFileRef.duration_seconds
    #print(musicfileDuration)
    modifiedMusicRef=None
    for audioMark in audioMarks:
        marktype=audioMark['type']
        markStart=audioMark['start']
        markEnd=audioMark['end']
       # initialSegment=musicFileRef[markStart:markStart+transition]
       # middleSegment=musicFileRef[markStart+transition:markEnd-transition]
       # finalSegment=musicFileRef[markEnd-transition:markEnd]
        segment=musicFileRef[markStart:markEnd]
        if(marktype=='S'):#needs the total duration greater than 2000
            #initialSegment=initialSegment*
            #pass
            segment=segment.fade_in(1000).fade_out(1000)
            
        elif(marktype=='A'):
            segment=segment-20
             
        if(modifiedMusicRef is None):
            modifiedMusicRef=segment
        else:
            modifiedMusicRef=modifiedMusicRef+segment

        
    silent_file_name=Path(audioFile).resolve().stem
    outputFileName=silent_file_name+"_"+musicFile    
    newcombinedMusic=audioFileRef.overlay(modifiedMusicRef) 
    newcombinedMusic.export(outputFileName, format="wav")
    print(outputFileName+' Saved')
    #play(newcombinedMusic)



def main():
    inputfile = ''
    outputfile = ''
    overlayfile=''
    musicscaling=-10
    rownum=0
    operationType='GENERATE_AUDIO'

    parser = argparse.ArgumentParser()
    parser.add_argument("-x", help="The Input .xlsx file", required=True)
    parser.add_argument("-r",type=int, help="The Row inside the .xlsx which should be individually processed")
    parser.add_argument("-o", help="The name of the Output File. Example output.wav")
    parser.add_argument("-m", help="Combine Audio with Overlay Music File. Example music_pop.wav")
    parser.add_argument("-v",type=int, help="Control the volume of the Music File. Negative values will reduce volume, positive values will increase it.")
    #parser.add_argument("-f",type=int, help="Optional, Fade duration in milliseconds")
    
    args = parser.parse_args()

    if(args.x):
        inputfile = args.x
        operationType='GENERATE_AUDIO'
    if(args.r):
        rownum = args.r
        operationType='GENERATE_AUDIO_FOR_ROW'
    if(args.o):
        outputfile = args.o
        operationType='GENERATE_AND_COMBINE_AUDIO'
    if(args.m):
        overlayfile = args.m
        operationType='COMBINE_AUDIO_WITH_OVERLAY'
    if(args.v):
        musicscaling=args.v
    
    

    if(operationType=="GENERATE_AUDIO"):
        generateAudio(inputfile)
    elif(operationType=="COMBINE_AUDIO_WITH_OVERLAY"):
        combined_audio_operations=combineFiles(inputfile,outputfile)
        overlayMusic(outputfile, overlayfile, combined_audio_operations,musicscaling)
    elif(operationType=="GENERATE_AND_COMBINE_AUDIO"):
        combineFiles(inputfile,outputfile)
    elif(operationType=='GENERATE_AUDIO_FOR_ROW'):
        generateAudio(inputfile,rownum)

if __name__ == "__main__":
   main()