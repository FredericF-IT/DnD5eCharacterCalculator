# DnD 5e Character Calculator
## Setup
Requires Python 3.  
Was written with Python v3.9.4 64-bit.  
The following packages may already be installed. Only try installing them if you get an import error.
### Needed Python modules (Linux)
python3 -m pip install -U matplotlib  
sudo apt-get install python3-tk  
sudo apt-get install python3-pillow  
sudo apt-get install python3-pil.imagetk  
### Needed Python modules (Windows)
python -m pip install -U matplotlib  
python -m pip install -U tk  
python -m pip install -U pillow
## Usage
Start main.py in the commandline.  
### 1. Analysis
This generates ALL possible (good*) Characters.  
All settings for Analysis have a default value and are explained inside the Analysis.py file, but the actually used settings are inside Settings.txt.    
Extra recommendations for settings at end of the project PDF (also explains criteria for good*).    
This only accounts for DpR.

It is recommended to download the PDF, as the git viewer doesen't show/activate hyperreferences and can be hard to read. 
### 2. Creation
Build a specific Character, the DpR is calculted live.  
Not done yet.  
May add DpSR (Damage per short rest) and DpLR (Damage per long rest) to account for resources like spellslots, action surges etc.
## Content
There are only limited options available as of writing, I am uncertain of what sourcebooks will be added at all.  
This will not include any dice-rolling mechanics, as this should not be used as a usable character sheet.  
This constraint exists so that WotC do not sue me, as this free programm would compete with DnD Beyond.  
It is only supposed to let you find a character you want to play.  
This is why I would advise against forking this project with the goal of adding such a feature.
