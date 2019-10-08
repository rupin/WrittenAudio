# WrittenAudio
Written Audio Uses Google Text to Speech engine and a configuration file to create Audio files for videos


usage: createAudio.py [-h] -x X [-r R] [-o O] [-m M] [-v V]

optional arguments:
  -h, --help  show this help message and exit
  
  -x X        The Input .xlsx file
  
  -r R        The Row inside the .xlsx which should be individually processed
  
  -o O        The name of the Output File. Example output.wav
  
  -m M        Combine Audio with Overlay Music File. Example music_pop.wav
  
  -v V        Control the volume of the Music File. Negative values will
              reduce volume, positive values will increase it.

# Before Getting Started
### Install Python

[Install Python](http://www.python.org "Download Python")

### Download Dependencies

Download the code, then run 

<code>pip3 install -r requirements.txt</code>

This command will install all required dependencies for your to run the program.

### Create your .xlsx file
* The Application takes its input from a .xlsx file. 
* The code assumes the first row will be a header with two columns Time and Text
* The first column in this .xlsx file should have the time markers in seconds.
* The second column should have the text that should start at the time marker. 

Look at the included Audio Sequence.xlsx file to understand better.

# How to Use

## Create Individual Audio files from .xlsx file
 
<code>python3 createAudio.py -x 'Audio Sequence.xlsx'</code>

## Create Individual Audio file for a specific row.
After Creating all files, you reviewed them. Edit a specific row
 
<code>python3 createAudio.py -x 'Audio Sequence.xlsx'</code>

## Combine Files with silent periods between Audio
 
<code>python3 createAudio.py -x 'Audio Sequence.xlsx' -o 'output.wav'</code>

Use the Audio Sequence.xlsx file to generate audio files (it skips files which are already generated), and combine those into one single output.wav file. 
