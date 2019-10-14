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


#print()

class CreateAudio():

    

    def __init__(self, folder_name):
        self.foldername=folder_name


    


    def createFileName(self,row, timeslot):
        filename="Row_"+str(row)+ "_"+str(timeslot)+".wav"
        #print(self.foldername)
        filePath=os.path.join(self.foldername, filename)
        #print(filePath)
        return filePath

    def appendFolderName(self,filename):

        return os.path.join(self.foldername, filename)

    
    def createAudioFile(self,row, timeslot, sentence):
        filename=self.createFileName(row, timeslot)
        newTTSObject=TTS(TTS.SERVICE_PROVIDER_GOOGLE)
        audioStream=newTTSObject.convertTTSGoogle(sentence)
        #The response's audio_content is binary.
        with open(filename, 'wb') as out:
            # Write the response to the output file.
            out.write(audioStream)
            print('Audio content written to file: '+filename)


    def generateAudio(self, myfile,pending_row=-1):      
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
                self.createAudioFile(pending_row,timeslot, sentence)
            else:
                print("Row number "+str(pending_row)+" does not exist in the input file")
                sys.exit(2)  
        else:

            for row in range (1, rowcount):
                timeslot=sheet.cell_value(row, 0)  
                sentence=sheet.cell_value(row, 1) 
                self.createAudioFile(row,timeslot, sentence)      
                #audioStream=TTS.convertTTSGoogle(sentence)

           

            
       

    def combineFiles(self,inputxlsfilename, outputFileName):

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
                filename=self.createFileName(row, timeslot)
                fileExists=os.path.exists(filename)
                if(not fileExists):
                    self.createAudioFile(row,timeslot, sentence)
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
            export_file_name=self.appendFolderName(outputFileName)
            combined_sounds.export(export_file_name, format="wav")
            print(export_file_name+' Saved')
            #print(operations)
            return operations



    #readXLS('Audio Sequence.xlsx')
    def overlayMusic(self,audioFile, musicFile, audioMarks, musicscaling=-10):
        #print(audiofile)
        #print(musicFile)
        #print(audiomarks)
        transition=1000
        baseAudioFilePath=self.appendFolderName(audioFile)
        audioFileRef=AudioSegment.from_wav(baseAudioFilePath)
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
        export_file_name=self.appendFolderName(outputFileName)
        newcombinedMusic.export(export_file_name, format="wav")
        print(export_file_name+' Saved')
        #play(newcombinedMusic)

