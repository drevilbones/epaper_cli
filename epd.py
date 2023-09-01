# import required python libraries
import os
from os.path import exists
import logging
import sys
import textwrap
import argparse
import fileinput
 
# get display from Waveshare library
import epd4in2 

# get functions from Pillow
from PIL import Image, ImageDraw, ImageFont
 
font_dir = '/usr/share/fonts/'

try:
    # parse CLI arguments
    parser = argparse.ArgumentParser(description='Display data on Waveshare epaper screen.')
    parser.add_argument("--file", "-f", help="name of the file to display", metavar='filename')
    parser.add_argument("--font", help="font face to use for text, defaults to Terminess",
        default='Terminus/TerminessNerdFont-Regular.ttf', metavar='font_filename')
    parser.add_argument("--size", help="size of the font, defaults to 12",
        default=12, type=int, metavar='font_size')
    parser.add_argument("--pipe", "-p", help="read from pipe", action='store_true')
    parser.add_argument("--verbose", "-v", action='store_true')
    parser.add_argument("--nowrap", "-nw", action='store_true', help="don't wrap output (may exceed display)")
    
    args = parser.parse_args()
    
    logger = logging.getLogger('epd')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    if args.verbose:
        logger.setLevel(logging.DEBUG)    

    if args.file is not None and not exists(args.file):
        print("file not found: " + args.file)
        exit()
        
    # open and store file contents (or read from stdin)
    text = ""
    if args.file is not None:
        logger.debug('opening file: ' + args.file)    
        file = open(args.file)
        text = file.read()
        file.close()
    elif args.pipe:
        for line in sys.stdin:
            text += line
    else:
        parser.print_usage()
        exit()
    logger.debug(text)

    # initialize display
    logger.debug('init display')
    epd_disp = epd4in2.EPD()
    epd_disp.init()
    epd_disp.Clear()
       
    #define fonts
    logger.debug('loading font ' + args.font + " at size " + str(args.size)) 
    font = ImageFont.truetype(font_dir + args.font, int(args.size))
    
    # define and draw background
    logger.debug('setting up image')
    image = Image.new(mode='1', size=(epd_disp.width,epd_disp.height),color=255)
    logger.debug('calling draw')
    draw = ImageDraw.Draw(image)

    # position and draw text
    logger.debug('drawing text')
    
    if args.nowrap:
        draw.text((0,0), font=font, text=text)
    else: # wrap the text
        # calc area for text
        rows = epd_disp.height // args.size
        #TODO test if font is monospace
        #TODO figure out why this mangles piped-in text
        charlen = font.getlength("X") # find pixel width of a single char (only works with mono font)
        cols = epd_disp.width // charlen
        logger.debug("rows: " + str(rows) + ", columns: " + str(cols))
        wrapper = textwrap.TextWrapper(replace_whitespace=False, drop_whitespace=False)
        wrapper.width = cols
        wrapper.max_lines = rows
        wrapped_text = wrapper.wrap(text)
        stopnum = rows
        if len(wrapped_text) < rows:
            stopnum = len(wrapped_text)
        for linenum in range(0, stopnum):
            draw.text((0, linenum * args.size), font=font, text=wrapped_text[linenum])
    
    # write buffer contents to display
    logger.debug('write buffer')
    epd_disp.display(epd_disp.getbuffer(image))

    # go to sleep
    logger.debug('display going to sleep')
    epd_disp.sleep()

except Exception as e:
    logger.exception(e)

    logger.debug('display going to sleep')
    epd_disp.sleep()
