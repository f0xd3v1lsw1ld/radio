import pygame
from pygame.locals import *
import fnmatch
import os
import time
import subprocess
import simpleGui
import logging

# Global stuff -------------------------------------------------------------
screenMode = 0              # Current screen mode; default = viewfinder
shuffelMode = 0             # Current shuffel mode; default = off
playMode = 0                # Current play mode; default = stop
repeatMode = 0              # Current repeat mode; default = off
volume = 95                 # Current volume in percent; default = 95%
volume_step = 5             # step size to change global volume; default = 5
screenModePrior = -1        # Prior screen mode (for detecting changes)
iconPath = 'icon'           # Subdirectory containing UI bitmaps (PNG format)
icons = []                  # This list gets populated at startup
channel_pos = 0             # Current position in playlist, default = 0
running = False             # pygame running identification
textsize = 20               # character size of textbox
channelName = ["Apollo Radio", "MDR Figaro", "MDR Jump"]
channelLink = ["http://apollo-stream.primacom.net:6300",
               "http://c22033-l.i.core.cdn.streamfarm.net/22007mdrfigaro/live/3087mdr_figaro/live_de_128.mp3",
               "http://c22033-l.i.core.cdn.streamfarm.net/22004mdrjump/live/3087mdr_jump/live_de_128.mp3"]

# UI callbacks -------------------------------------------------------------
# These are defined before globals because they're referenced by items in
# the global buttons[] list.


def doneCallback():
    raise SystemExit


def testCallback(n):
    global screenMode
    screenMode += n


def playCallback():
    global screenMode, playMode
    if playMode is 0:
        logging.debug("play")
        buttons[screenMode][2].setBg('pause')
        buttons[screenMode][2].draw(screen)
        pygame.display.update()
        playMode = 1
        logging.debug("bevor")
        try:
            subprocess.check_output("mpc play", shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            logging.error("mpc play "+str(e))
            pass
        logging.debug('after')
        display_channel()
        pygame.time.set_timer(USEREVENT + 1, 1000)
    elif playMode is 1:
        logging.debug("stop")
        buttons[screenMode][2].setBg('play')
        buttons[screenMode][2].draw(screen)
        pygame.display.update()
        playMode = 0
        try:
            subprocess.check_output("mpc stop", shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            logging.error("mpc stop "+str(e))
            pass
        pygame.time.set_timer(USEREVENT + 1, 0)
    else:
        playMode = 0
        pygame.time.set_timer(USEREVENT + 1, 0)
        return


def shuffelCallback():
    global screenMode, shuffelMode
    if shuffelMode is 0:
        logging.debug("shuffel_on")
        buttons[screenMode][0].setBg('shuffel_on')
        buttons[screenMode][0].draw(screen)
        pygame.display.update()
        shuffelMode = 1
    elif shuffelMode is 1:
        logging.debug("shuffel_off")
        buttons[screenMode][0].setBg('shuffel_off')
        buttons[screenMode][0].draw(screen)
        pygame.display.update()
        shuffelMode = 0
    else:
        shuffelMode = 0
        return


def repeatCallback():
    global screenMode, repeatMode
    if repeatMode is 0:  # repeat off -> repeat 0ne
        logging.debug("repeat one")
        buttons[screenMode][4].setBg('repeat_1')
        buttons[screenMode][4].draw(screen)
        pygame.display.update()
        repeatMode = 1
    elif repeatMode is 1:  # repeat one -> repeat all
        logging.debug("repeat all")
        buttons[screenMode][4].setBg('repeat_all')
        buttons[screenMode][4].draw(screen)
        pygame.display.update()
        repeatMode = 2
    elif repeatMode is 2:  # repeat all -> repeat off
        logging.debug("repeat off")
        buttons[screenMode][4].setBg('repeat_off')
        buttons[screenMode][4].draw(screen)
        pygame.display.update()
        repeatMode = 0
    else:
        logging.error("wrong repeat Mode")
        repeatMode = 0
        return


def nextCallback():
    logging.debug("next")
    if channel_pos < len(channelName):
        buttons[screenMode][3].setBg('next_press')
        buttons[screenMode][3].draw(screen)
        pygame.display.update()
        time.sleep(0.15)
        buttons[screenMode][3].setBg('next')
        buttons[screenMode][3].draw(screen)
        pygame.display.update()
        try:
            subprocess.check_output("mpc next", shell=True, stderr=subprocess.STDOUT)
            display_playlist()
        except Exception as e:
            logging.error("mpc next "+str(e))
            pass
        display_channel()
    else:
        logging.debug("last channel in list")


def prevCallback():
    logging.debug("prev")
    if channel_pos > 1:
        buttons[screenMode][1].setBg('prev_press')
        buttons[screenMode][1].draw(screen)
        pygame.display.update()
        time.sleep(0.15)
        buttons[screenMode][1].setBg('prev')
        buttons[screenMode][1].draw(screen)
        pygame.display.update()
        try:
            subprocess.check_output("mpc prev", shell=True, stderr=subprocess.STDOUT)
            display_playlist()
        except Exception:
            logging.error("mpc prev")
            pass
        display_channel()
    else:
        logging.debug("first channel in list")


def stopCallback():
    global screenMode
    screenMode = 0


def repeat1Callback():
    global screenMode
    screenMode = 2


def repeatAllCallback():
    global screenMode
    screenMode = 3


def repeatOffCallback():
    global screenMode
    screenMode = 1


def exitCallback():
    global running
    logging.debug("exit")
    buttons[screenMode][5].setBg('exit_press')
    buttons[screenMode][5].draw(screen)
    pygame.display.update()
    time.sleep(0.15)
    buttons[screenMode][5].setBg('exit')
    buttons[screenMode][5].draw(screen)
    pygame.display.update()
    running = False
    pygame.event.post(pygame.event.Event(pygame.QUIT))


def volUpCallback():
    global volume, volume_step
    logging.debug("volume up")
    buttons[screenMode][4].setBg('vol_up_press')
    buttons[screenMode][4].draw(screen)
    pygame.display.update()
    time.sleep(0.15)
    buttons[screenMode][4].setBg('vol_up')
    buttons[screenMode][4].draw(screen)
    pygame.display.update()
    try:
        if volume <= (100 - volume_step):
            volume = volume + volume_step
        logging.debug("set volume to " + str(volume))
        out = "mpc volume " + str(volume)
        subprocess.check_output(out, shell=True, stderr=subprocess.STDOUT)
        display_volume()
    except Exception:
        logging.error("mpc volume up")
        pass
    display_volume()


def volDownCallback():
    global volume, volume_step
    logging.debug("volume down")
    buttons[screenMode][0].setBg('vol_down_press')
    buttons[screenMode][0].draw(screen)
    pygame.display.update()
    time.sleep(0.15)
    buttons[screenMode][0].setBg('vol_down')
    buttons[screenMode][0].draw(screen)
    pygame.display.update()
    try:
        if volume >= (0 + volume_step):
            volume = volume - volume_step
        logging.debug("set volume to " + str(volume))
        out = "mpc volume " + str(volume)
        subprocess.check_output(out, shell=True, stderr=subprocess.STDOUT)
        display_volume()
    except Exception:
        logging.error("mpc volume down")
        pass
    display_volume()

# Create the playlist with configurable internet radio channels


def create_playlist():
    logging.debug("create playlist")
    try:
        subprocess.check_output("mpc clear", shell=True, stderr=subprocess.STDOUT)
    except Exception:
        pass

    for channel in channelLink:
        try:
            subprocess.check_output("mpc add " + channel, shell=True, stderr=subprocess.STDOUT)
            logging.debug("add channel: " + channel)
        except Exception:
            logging.error("mpc add " + channel)
            pass


def display_channel():
    global channel_pos
   # channel = ""
    logging.debug("display channel")
    try:
        channel = subprocess.check_output("mpc status | grep playing", shell=True, stderr=subprocess.STDOUT)
        logging.debug(channel)
        channel = channel[channel.find("#") + 1:channel.find("/")]
        channel_pos = int(channel)
        channel = channelName[int(channel) - 1]
        logging.debug(channel)
        textboxes[0][0].draw(channel, textsize, 64, 64)
    except Exception as e:
        logging.error("mpc status "+str(e))
        textboxes[0][0].draw("display channel", textsize, 64, 64)
        pass
    display_volume()
    display_playlist()
    display_playtime()


def display_volume():
    global volume
    logging.debug("display volume")
    # strvolume =""
    try:
        strvolume = subprocess.check_output("mpc status | grep volume", shell=True, stderr=subprocess.STDOUT)
        strvolume = strvolume[7:strvolume.find("%") + 1]
        textboxes[0][2].draw(strvolume, textsize, 64, 104)
        logging.debug(strvolume)
        volume = int(strvolume[:-1])
    except Exception as e:
        logging.error("mpc status "+str(e))
        textboxes[0][2].draw("display volume", textsize, 64, 104)
        pass

# Retrieve playlist position and size from mpc and display


def display_playlist():
    logging.debug("display playlist")
    try:
        playlist = subprocess.check_output("mpc status | grep playing", shell=True, stderr=subprocess.STDOUT)
        playlist = playlist[playlist.find("#") + 1:playlist.find("/") + 2]
        textboxes[0][1].draw(playlist, textsize, 64, 84)
    except Exception as e:
        logging.error("mpc status "+str(e))
        textboxes[0][1].draw("display playlist", textsize, 64, 84)
        pass


def display_playtime():
    global playMode
    if playMode == 1:
        #logging.info("display playtime: "+str(pygame.time.get_ticks()))
        # playtime = ""
        try:
            playtime = subprocess.check_output("mpc status | grep playing", shell=True, stderr=subprocess.STDOUT)
            playtime = playtime[playtime.find("/") + 2:]
            playtime = playtime[playtime.find(" "):playtime.find("/")]
            textboxes[0][3].draw(playtime, textsize, 64, 124)
        except Exception as e:
            logging.error("mpc status " + str(e))
            textboxes[0][3].draw("display playtime", textsize, 64, 124)
            pass

# buttons[] is a list of lists; each top-level list element corresponds
# to one screen mode (e.g. viewfinder, image playback, storage settings),
# and each element within those lists corresponds to one UI button.
# There's a little bit of repetition (e.g. prev/next buttons are
# declared for each settings screen, rather than a single reusable
# set); trying to reuse those few elements just made for an ugly
# tangle of code elsewhere.

buttons = [
    # Screen mode 0 is app start or stop mode
    [
        simpleGui.Button((0, 183, 64, 58), bg='vol_down', cb=volDownCallback),
        simpleGui.Button((64, 183, 64, 64), bg='prev', cb=prevCallback),
        simpleGui.Button((128, 183, 64, 57), bg='play', cb=playCallback),
        simpleGui.Button((192, 183, 64, 64), bg='next', cb=nextCallback),
        simpleGui.Button((256, 183, 64, 58), bg='vol_up', cb=volUpCallback),
        simpleGui.Button((0, 0, 32, 32), bg='exit', cb=exitCallback)
    ]
]
textboxes = [
    [
        simpleGui.Textbox(200, 20, (192, 192, 192)),
        simpleGui.Textbox(200, 20, (192, 192, 192)),
        simpleGui.Textbox(200, 20, (192, 192, 192)),
        simpleGui.Textbox(200, 20, (192, 192, 192)),
    ]
]

# Initialization -----------------------------------------------------------

# Init framebuffer/touchscreen environment variables

#os.putenv('SDL_VIDEODRIVER', 'fbcon')
#os.putenv('SDL_FBDEV'      , '/dev/fb1')
#os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
#os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# Init pygame and screen
pygame.init()
pygame.mouse.set_visible(True)
#screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((320, 240))
# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((192, 192, 192))
screen.blit(background, (0, 0))
pygame.display.flip()
pygame.display.update()

# Load all icons at startup.
for file in os.listdir(iconPath):
    if fnmatch.fnmatch(file, '*.png'):
        icons.append(simpleGui.Icon(iconPath, file.split('.')[0]))

# Assign Icons to Buttons, now that they're loaded
for s in buttons:        # For each screenful of buttons...
    for b in s:            # For each button on screen...
        b.setIconList(icons)
        for i in icons:      # For each icon...
            if b.bg == i.name:  # Compare names; match?
                b.iconBg = i     # Assign Icon to Button
                b.bg = None  # Name no longer used; allow garbage collection
            if b.fg == i.name:
                b.iconFg = i
                b.fg = None


# Main loop ----------------------------------------------------------------
running = True
create_playlist()

while running:
    run = True
    # Process touchscreen input
    while run:
        for event in pygame.event.get():
            if event.type is MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for b in buttons[screenMode]:
                    if b.selected(pos):
                        break
            if event.type == USEREVENT + 1:
                display_playtime()
            if event.type == pygame.QUIT:
                running = False
                run = False
        # If in viewfinder or settings modes, stop processing touchscreen
        # and refresh the display to show the live preview.  In other modes
        # (image playback, etc.), stop and refresh the screen only when
        # screenMode changes.
        if screenMode >= 3 or screenMode != screenModePrior:
            break

    # Overlay buttons on display and update
    for i, b in enumerate(buttons[screenMode]):
        b.draw(screen)
    pygame.display.update()
    screenModePrior = screenMode

pygame.quit()
