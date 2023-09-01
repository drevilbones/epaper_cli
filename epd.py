# import required python libraries
import os
from os.path import exists
import logging
import sys
import textwrap
import argparse
 
# get display from Waveshare library
import epd4in2 

# get functions from Pillow
from PIL import Image, ImageDraw, ImageFont
 
font_dir = '/usr/share/fonts/'

try:
    # parse CLI arguments
    parser = argparse.ArgumentParser(description='Display data on Waveshare epaper screen.')
    parser.add_argument("file", help="name of the file to display")
    parser.add_argument("--font", help="font face to use for text, defaults to Terminess",
        default='Terminus/TerminessNerdFont-Regular.ttf')
    parser.add_argument("--size", help="size of the font, defaults to 16",
        default=16, type=int)
    parser.add_argument("--verbose", action='store_true')
    
    if not len(sys.argv) > 1:
        parser.print_usage()
        exit()
    args = parser.parse_args()

    if not exists(args.file):
        print("file not found: " + args.file)
        exit()
    
    logger = logging.getLogger('epd')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # initialize display
    logger.debug('init display')
    epd_disp = epd4in2.EPD()
    epd_disp.init()
    epd_disp.Clear()
       
    #define fonts
    logger.debug('loading font ' + args.font + " at size " + str(args.size)) 
    font = ImageFont.truetype(font_dir + args.font, int(args.size))
    
    # #TODO test if font is monospace with font.metrics("fixed")
    
    # define and draw background
    logger.debug('setting up image')
    image = Image.new(mode='1', size=(epd_disp.width,epd_disp.height),color=255)
    logger.debug('calling draw')
    draw = ImageDraw.Draw(image)

    # position and draw text
    logger.debug('drawing text')
    rows = epd_disp.height // args.size
    charlen = font.getlength("X") # find pixel width of a single char (only works with mono font)
    cols = epd_disp.width // charlen
    logger.debug("rows: " + str(rows) + ", columns: " + str(cols))
    wrapper = textwrap.TextWrapper()
    wrapper.width = cols
    wrapper.max_lines = rows
    file = open(args.file)
    text = file.read()
    file.close()
    wrapped_text = wrapper.wrap(text)
    
    for linenum in range(0, rows):
        draw.text((0, linenum * args.size), font=font, text=wrapped_text[linenum])
    
    #logger.debug('loading graphic')
    #beholder = Image.open('beholder.jpg')
    
    # paste image onto background image
    #logger.debug('pasting image onto bg')
    #image.paste(beholder, (80, 35))
    
    # write buffer contents to display
    logger.debug('write buffer')
    epd_disp.display(epd_disp.getbuffer(image))

    # go to sleep
    logger.debug('display going to sleep')
    epd_disp.sleep()

except Exception as e:
    logger.exception(e)
