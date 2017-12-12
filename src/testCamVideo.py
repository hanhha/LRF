import picamera as picam
from PIL import Image
from picamera.array import PiRGBArray
import time
import pygame
from pygame.locals import *
import numpy as np
import os

os.environ['SDL_VIDEODRIVER'] = 'fbcon'

imgDimensions = (320, 240)

firstFrame = None
secondFrame = None
thirdFrame = None
forthFrame = None

camera = picam.PiCamera()
camera.resolution = imgDimensions 
camera.framerate = 30
camera.led = False
rawCapture = PiRGBArray(camera, size=imgDimensions)

screen = None

clock = pygame.time.Clock ()

def initializePygame ():
	global screen, myfont
	global firstFrame, secondFrame, thirdFrame, forthFrame

	pygame.init()
	infoObj = pygame.display.Info ()
	pygame.mouse.set_visible (False)
	screen = pygame.display.set_mode ((infoObj.current_w, infoObj.current_h), 0, 32)
	# Using default system font so that set it None
	myfont = pygame.font.SysFont (None, 30)
	firstFrame = (0,0)
	secondFrame = (infoObj.current_w / 2, 0)
	thirdFrame = (0,infoObj.current_h)
	forthFrame = (infoObj.current_w, infoObj.current_h)

def stickImg (img, update = False):
	pygameSurface = pygame.surfarray.make_surface (img.swapaxes(0,1))
	screen.blit (pygameSurface, firstFrame)
	if update:
		pygame.display.update()

def stickText (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, secondFrame + (10,10))
	if update:
		pygame.display.update()

def cleanScreen ():
	screen.fill ((0,0,0))

def __main__ ():
	initializePygame ()
	for frame in camera.capture_continuous (rawCapture, format ="bgr", use_video_port=True):
		image = np.copy (frame.array) 
		cleanScreen ()
		stickImg (image)
		stickText ('FPS ' + str(clock.get_fps()), update = True)
		
		clock.tick ()
		for event in pygame.event.get ():
			if event.type == QUIT:
				pygame.quit ()
				sys.exit ()
			if event.type == KEYDOWN and event.key == K_q:
				return
				
		rawCapture.truncate(0)
	
	camera.close()

# call main
__main__()
# EOF
