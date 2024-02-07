[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/9FxAlQXs)
# TITLE

| Author        |     Frederic Frenkel          |
| ------------- | ------------- |
| Matrikelnummer|   5120736            |


## Subsection
Needed downloads:  
python3 -m pip install -U matplotlib  
sudo apt-get install python3-tk  
sudo apt-get install python3-pillow  
sudo apt-get install python3-pil.imagetk  
Applying all of these lets the script run on the TACAS23 image.  
It may happen that the program gives you the error "_tkinter.TclError: couldn't connect to display "whatever"  
You can fix this by using this in the terminal:  
export DISPLAY=:0  
using the number that responds to the appropriate monitor.  

To start the main program:  
Start Analysis.py in the commandline  
All settings are explained inside the file, but most settings in Analysis.py are overwritten with those from Settings.txt    
Extra recommendations for settings at end of Project PDF.    
Extra information and a few test cases are in CharIO.py, which can also be run.  

What part of the report this recreates:  
There is no subset here, the runtime is low enough to reproduce all results with the given settings.
