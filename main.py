
from processors.createAudio import CreateAudio
import argparse
from pathlib import Path
import os
def createFolder(xlsfilename):
        xls_file_name=Path(xlsfilename).resolve().stem
        if not os.path.exists(xls_file_name):
            os.mkdir(xls_file_name)
        return xls_file_name

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
        
        
        folder_name=createFolder(inputfile)
        processor=CreateAudio(folder_name)

        if(operationType=="GENERATE_AUDIO"):
            processor.generateAudio(inputfile)
        elif(operationType=="COMBINE_AUDIO_WITH_OVERLAY"):
            combined_audio_operations=processor.combineFiles(inputfile,outputfile)
            processor.overlayMusic(outputfile, overlayfile, combined_audio_operations,musicscaling)
        elif(operationType=="GENERATE_AND_COMBINE_AUDIO"):
            processor.combineFiles(inputfile,outputfile)
        elif(operationType=='GENERATE_AUDIO_FOR_ROW'):
            processor.generateAudio(inputfile,rownum)

if __name__ == "__main__":
   main()