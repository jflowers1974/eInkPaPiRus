#!/usr/bin/python

# Install the following: (Python 3)
# 1) https://github.com/PiSupply/PaPiRus
# 2) blockchain.info 
# >sudo pip install blockchain
# 3) Blockchain python rpc (optimized for blockchain)
# >sudo pip install python-bitcoinrpc
# 4) Simple JSON
# >sudo pip install simplejson

import os
import sys
import time
import datetime
import RPi.GPIO as GPIO
import urllib2
import json
import simplejson

from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from blockchain import statistics

user = os.getuid()
if user != 0:
    print "Please run script as root"
    sys.exit()

# Command line usage
# papirus-buttons

WHITE = 1
BLACK = 0

SIZE = 22

SW1 = 16
SW2 = 26
SW3 = 20
SW4 = 21

defaultText = "[4] [3] [2] [1] ***************\n[1]: Bitcoin*****\n[2]: Litecoin****\n[4]: Shutdown rPi"

def main():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SW1, GPIO.IN)
    GPIO.setup(SW2, GPIO.IN)
    GPIO.setup(SW3, GPIO.IN)
    GPIO.setup(SW4, GPIO.IN)

    papirus = Papirus()

    write_text(papirus, defaultText, SIZE)

    while True:
        if GPIO.input(SW1) == False:
            stats = statistics.get()
            btcBlockHeight = stats.total_blocks
            # The blockchain api returns bits, need to convert to kB
            btcBlockSizeCleaned = (stats.blocks_size)/125000

            write_text(papirus, "%s --BITCOIN--\nBlockheight:%d \nBlocksize    : %d kB" % (todayCleaned(), btcBlockHeight,btcBlockSizeCleaned), SIZE)

            time.sleep(10)
            write_text(papirus, defaultText, SIZE)
            
        if GPIO.input(SW2) == False:
            responseBlockr = urllib2.urlopen("http://ltc.blockr.io/api/v1/coin/info")
            htmlResponse = simplejson.load(responseBlockr)
            #print(htmlResponse["data"]["last_block"]["nb"])
            ltcBlockHeight = int(htmlResponse["data"]["last_block"]["nb"])

            dayDate = todayCleaned()
            write_text(papirus,"%s --LITECOIN--\nBlockheight:%d" % (todayCleaned(), ltcBlockHeight), SIZE)

            time.sleep(10)
            write_text(papirus, defaultText, SIZE)

        if GPIO.input(SW3) == False:
            write_text(papirus, "Three", SIZE)

            time.sleep(10)
            write_text(papirus, defaultText, SIZE)

            
        if GPIO.input(SW4) == False:
            write_text(papirus, "Shutdown Begun \nCheers!", SIZE)
            shutdown()

            #time.sleep(10)
            #write_text(papirus, defaultText, SIZE)

        time.sleep(0.1)

def todayCleaned():
    today = datetime.datetime.today()
    todayCleaned = time.strftime("%A %I:%M %p")
    return todayCleaned

def shutdown():
    os.system("shutdown -h now")

def write_text(papirus, text, size):

    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', size)

    # Calculate the max number of char to fit on line
    line_size = (papirus.width / (size*0.65))

    current_line = 0
    text_lines = [""]

    # Compute each line
    for word in text.split():
        # If there is space on line add the word to it
        if (len(text_lines[current_line]) + len(word)) < line_size:
            text_lines[current_line] += " " + word
        else:
            # No space left on line so move to next one
            text_lines.append("")
            current_line += 1
            text_lines[current_line] += " " + word

    current_line = 0
    for l in text_lines:
        current_line += 1
        draw.text( (0, ((size*current_line)-size)) , l, font=font, fill=BLACK)

    papirus.display(image)
    papirus.update()

if __name__ == '__main__':
    main()
