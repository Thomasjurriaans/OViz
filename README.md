# OViz
This program can be used to visualise any train journeys made in the Netherlands with an OV-Chipkaart.

This gif plays slower than the actual video created, [click here](https://giant.gfycat.com/DentalPiercingGrub.webm) for a more accurate representation.

![gif](http://i.imgur.com/pPbUofZ.gif)


## Requirements
1. FFmpeg with x264 support [(Windows)](https://www.wikihow.com/Install-FFmpeg-on-Windows)
2. Two NS API keys, available for free [here](https://apiportal.ns.nl). You need a key for the "getSpoorkaart" API and one for "getTrips".
3. The Python Libraries in ```requirements.txt```, use Python 3.7.5 if you can. You can install the libraries by running ```pip install -r requirements.txt```, or having your IDE install them for you (PyCharm does this). 

## Usage
1. Clone this repository.
2. Download your OV-Chipkaart history from https://www.ov-chipkaart.nl. Use the "Create expenses overview" / "Maak declaratieoverzicht" function in the history section. Unfortunately you can only download 1 month at a time. Make sure to check all entries in the overview, and download as '.csv'. Put these .csv's in ```/data/travelhistory/raw/```. The order of the filenames is used to order the visualization.
3. Enter your API keys in ```APIconfig.py```
4. Run ```Python OViz.py``` (This can take a couple of minutes)
5. Find your .mp4 video in ```/output/```
6. Please credit by linking this repo :)


This is my first hobby project in Python. I tried to make the code as clear as possible and add comments where necessary, hopefully this makes the code easier to understand. Feedback or questions are always welcome!

Inspired by: https://github.com/guushoekman/train-journeys
