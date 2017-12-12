import picamera as picam
from PIL import Image
from picamera.array import PiRGBArray
import time
import pygame
from pygame.locals import *
import numpy as np

imgDimensions = (320, 240)

camera = picam.PiCamera()
camera.resolution = imgDimensions 
camera.framerate = 30
camera.led = False
rawCapture = PiRGBArray(camera, size=imgDimensions)

screen = None

def initializePygame ():
	global screen
	pygame.init()
	infoObj = pygame.display.Info ()
	pygame.mouse.set_visible (False)
	screen = pygame.display.set_mode ((infoObj.current_w, infoObj.current_h), 0, 32)

def stickImg (img, update = False):
	pygameSurface = pygame.surfarray.make_surface (img.swapaxes(0,1))
	screen.blit (pygameSurface, (0,0))
	if update:
		pygame.display.update()

def __main__ ():
	initializePygame ()
	for frame in camera.capture_continuous (rawCapture, format ="bgr", use_video_port=True):
		image = np.copy (frame.array) 
		stickImg (image, update = True)

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
