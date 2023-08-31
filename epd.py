# import required python libraries
import os
import logging
import sys
import textwrap
 
# get display from Waveshare library
import epd4in2 

# get functions from Pillow
from PIL import Image, ImageDraw, ImageFont
 
font_dir = '/usr/share/fonts/'

# parse cli argumets
#for arg in sys.argv
 
try:
    logger = logging.getLogger('epd')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    # initialize display
    logger.debug('init display')
    epd_disp = epd4in2.EPD()
    epd_disp.init()
    epd_disp.Clear()
       
    #define fonts
    logger.debug('loading font')
    font_size = 24
    font = ImageFont.truetype(font_dir + 'Terminus/TerminessNerdFont-Regular.ttf', font_size)
    
    #TODO test if font is monospace with font.metrics("fixed")
    
    # define and draw background
    logger.debug('setting up image')
    image = Image.new(mode='1', size=(epd_disp.width,epd_disp.height),color=255)
    logger.debug('calling draw')
    draw = ImageDraw.Draw(image)
    
    # position and draw text
    text = "Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal. Now we are engaged in a great civil war, testing whether that nation, or any nation so conceived and so dedicated, can long endure. We are met on a great battle-field of that war. We have come to dedicate a portion of that field, as a final resting place for those who here gave their lives that that nation might live. It is altogether fitting and proper that we should do this. But, in a larger sense, we can not dedicate—we can not consecrate—we can not hallow—this ground. The brave men, living and dead, who struggled here, have consecrated it, far above our poor power to add or detract. The world will little note, nor long remember what we say here, but it can never forget what they did here. It is for us the living, rather, to be dedicated here to the unfinished work which they who fought here have thus far so nobly advanced. It is rather for us to be here dedicated to the great task remaining before us—that from these honored dead we take increased devotion to that cause for which they gave the last full measure of devotion—that we here highly resolve that these dead shall not have died in vain—that this nation, under God, shall have a new birth of freedom—and that government of the people, by the people, for the people, shall not perish from the earth."

    logger.debug('drawing text')
    rows = epd_disp.height // font_size
    charlen = font.getlength("X") # find pixel width of a single char (only works with mono font)
    cols = epd_disp.width // charlen
    logger.debug("rows: " + str(rows) + ", columns: " + str(cols))
    wrapper = textwrap.TextWrapper()
    wrapper.width = cols
    wrapper.max_lines = rows
    wrapped_text = wrapper.wrap(text)
    
    for linenum in range(0, rows):
        draw.text((0, linenum * font_size), font=font, text=wrapped_text[linenum])
    
    #logger.debug('loading graphic')
    #beholder = Image.open('beholder.jpg')
    
    # paste image onto background image
    #logger.debug('pasting image onto bg')
    #image.paste(beholder, (80, 35))
    
    # write buffer contents to display
    logger.debug('write buffer')
    epd_disp.display(epd_disp.getbuffer(image))

    # go to sleep
    logger.debug('me go ni-ni')
    epd_disp.sleep()

except Exception as e:
    logger.exception(e)
