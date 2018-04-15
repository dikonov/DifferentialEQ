# DifferentialEQ

Create nicely averaged EQ curves to match equalization between different audio sources.

# Installation
- Install Python 3.6
- Open the command line (with admin rights). Type `pip install numpy pyqt5 matplotlib pysoundfile`
- Click the `Clone or Download` button at the right, then `Download ZIP`. Unzip to a folder of your choice.

![Imgur](https://i.imgur.com/Wei3V43.png)

# How to Use
- Shift+Rightclick in the folder with the scripts and run the windows power shell / command line. Type `python difeq.py` and enter.
- "+" Add a new differential EQ (opens file dialogs to select source and reference file)
- "-" Delete the selected EQ from the list.
- "=" Export the current average EQ to an XML file for use in Audacity.
- The numbers fade out the EQ curve over the given frequencies to avoid boosting the noise floor.
- Select which channels you want to compare for stereo files.
