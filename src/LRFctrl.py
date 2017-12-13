import picamera as picam
from PIL import Image
from picamera.array import PiRGBArray
import time
import pygame
from pygame.locals import *
import numpy as np
import os
import RPi.GPIO as GPIO
import cv2

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

laserPin = 7

def laserSETUP ():
	GPIO.setup   (laserPin, GPIO.OUT)

def laserON ():
	GPIO.output (laserPin, GPIO.HIGH)

def laserOFF ():
	GPIO.output  (laserPin, GPIO.LOW)

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
	thirdFrame = (0,infoObj.current_h / 2)
	forthFrame = (infoObj.current_w / 2, infoObj.current_h / 2)

def stickImg (img, update = False):
	pygameSurface = pygame.surfarray.make_surface (img.swapaxes(0,1))
	screen.blit (pygameSurface, firstFrame)
	if update:
		pygame.display.update()

def stickFPS (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(secondFrame,(30,10)))))
	if update:
		pygame.display.update()

def stickLsr (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(secondFrame,(30,100)))))
	if update:
		pygame.display.update()

def cleanScreen ():
	screen.fill ((0,0,0))

def detectSpot (img):
	hsv_img = cv2.cvtColor (img, cv2.COLOR_BGR2HSV)

def __main__ ():
	GPIO.cleanup ()
	GPIO.setmode (GPIO.BOARD)
	laserSETUP ()
	initializePygame ()
	laserOFF ()
	laser_on = False

	for frame in camera.capture_continuous (rawCapture, format ="bgr", use_video_port=True):
		image = np.copy (frame.array) 
		cleanScreen ()
		stickImg (image)
		stickFPS ('FPS ' + str(clock.get_fps()))
		if laser_on:
			stickLsr ('Laser ON', update = True)
		else:
			stickLsr ('Laser OFF', update = True)
		
		clock.tick ()
		for event in pygame.event.get ():
			if event.type == QUIT:
				pygame.quit ()
				GPIO.cleanup ()
				sys.exit ()
			if event.type == KEYDOWN and event.key == K_q:
				pygame.quit ()
				GPIO.cleanup ()
				return
			if event.type == KEYDOWN and event.key == K_l:
				laserON ()	
				laser_on = True
			if event.type == KEYDOWN and event.key == K_d:
				laserOFF ()	
				laser_on = False
		rawCapture.truncate(0)
	
	camera.close()
	pygame.quit ()
	GPIO.cleanup ()

# call main
__main__()
# EOF
