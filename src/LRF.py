#!/usr/bin/env python

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

imgDimensions = (640, 480)
imgFrame = None
firstFrame = None
secondFrame = None
thirdFrame = None
forthFrame = None

camera = picam.PiCamera()
camera.resolution = imgDimensions 
camera.framerate = 40
camera.led = False
camera.iso = 30
camera.exposure_mode = 'snow'
rawCapture = PiRGBArray(camera, size=imgDimensions)

syscfg = {'D': 24, 'f': -3.6, 'k': 0.0014} # all in mm

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
	global imgFrame

	pygame.init()
	infoObj = pygame.display.Info ()
	imgFrame = (infoObj.current_w / 2, infoObj.current_h / 2)
	pygame.mouse.set_visible (False)
	screen = pygame.display.set_mode ((infoObj.current_w, infoObj.current_h), 0, 32)
	# Using default system font so that set it None
	myfont = pygame.font.SysFont (None, 30)
	firstFrame = (0,0)
	secondFrame = (infoObj.current_w / 2, 0)
	thirdFrame = (0,infoObj.current_h / 2)
	forthFrame = (infoObj.current_w / 2, infoObj.current_h / 2)

def stickImg (img, update = False, screen_frame = 0):
	if img is not None:
		pygameSurface = pygame.surfarray.make_surface (img.swapaxes(0,1))
		scaledSurface = pygame.transform.scale(pygameSurface, imgFrame) 
		if screen_frame == 0:
			screen.blit (scaledSurface, firstFrame)
		if screen_frame == 1:
			screen.blit (scaledSurface, secondFrame)
		if screen_frame == 2:
			screen.blit (scaledSurface, thirdFrame)
		if screen_frame == 3:
			screen.blit (scaledSurface, forthFrame)
	if update:
		pygame.display.update()

def stickSpot (spot, update = False):
	sx = imgFrame[0] / float(imgDimensions[0])
	sy = imgFrame[1] / float(imgDimensions[1])
	scaled_spot = (int(spot[0] *sx), int(spot[1]*sy))
	pygame.draw.line (screen, (255,0,0), (scaled_spot[0], scaled_spot[1]-5), (scaled_spot[0], scaled_spot[1]+5), 2)
	pygame.draw.line (screen, (255,0,0), (scaled_spot[0]-5, scaled_spot[1]), (scaled_spot[0]+5, scaled_spot[1]), 2)
	#textSurface = myfont.render ('X' + str(spot[0]) + ' Y' + str(spot[1]), True, (255,255,255))
	#screen.blit (textSurface, tuple(map(sum,zip(forthFrame, (30,40)))))
	if update:
		pygame.display.update()

def stickDistance (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(forthFrame,(30,70)))))
	if update:
		pygame.display.update()

def stickFPS (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(forthFrame,(30,10)))))
	if update:
		pygame.display.update()

def cleanScreen ():
	screen.fill ((0,0,0))

def detectSpot (img):
	lab_img = cv2.cvtColor (img, cv2.COLOR_BGR2LAB)
	lw_range = np.array([240, 0,  0], dtype =np.uint8)
	up_range = np.array([255, 255, 255], dtype =np.uint8)
	mask = cv2.inRange (lab_img, lw_range, up_range)
	
	return mask

def getSpot (mask):
	spots = np.where (np.logical_and.reduce ((mask[0] == 255, mask[1] == 255, mask[2] == 255, mask[3] == 255, mask[4] == 255)), 255, 0)
	return spots

def getSpotPos (spots):
	if spots[1].size == 0 or spots[0].size == 0:
		return None
	else:
		tmp = np.where (spots == 255)
		cx = np.sum (tmp[1]) / tmp[1].size 
		cy = np.sum (tmp[0]) / tmp[0].size 
		return (cx, cy)

def __main__ ():
	GPIO.cleanup ()
	GPIO.setmode (GPIO.BOARD)
	laserSETUP ()
	initializePygame ()
	laserOFF ()
	bg_mask = None
	distance_txt = 'INF'
	mask = []
	spots = None
	phase = 0

	for frame in camera.capture_continuous (rawCapture, format ="bgr", use_video_port=True):
		image = np.copy (frame.array) 
		cleanScreen ()

		if phase == 0:
			bg_mask = detectSpot(image)
			laserON ()
			mask = []
			phase = 1
		elif phase == 1:
			mask.append (detectSpot(image) - bg_mask)
			stickImg (mask[-1], screen_frame = 2)
			phase = 2
		elif phase == 2:
			mask.append (detectSpot(image) - bg_mask)
			stickImg (mask[-1], screen_frame = 2)
			phase = 3
		elif phase == 3:
			mask.append (detectSpot(image) - bg_mask)
			stickImg (mask[-1], screen_frame = 2)
			phase = 4
		elif phase == 4:
			mask.append (detectSpot(image) - bg_mask)
			stickImg (mask[-1], screen_frame = 2)
			phase = 5
		else:
			mask.append (detectSpot(image) - bg_mask)
			stickImg (mask[-1], screen_frame = 2)
			laserOFF ()
			phase = 0

			spots = getSpot (mask)
			laserSpot = getSpotPos (spots)
			if laserSpot is not None:
				stickSpot (laserSpot)
				p = laserSpot[0] - imgDimensions[0]/2
				if p != 0:
					distance = syscfg['f'] * (syscfg['D'] / float(syscfg['k']*p))
					distance_txt = str(distance / 10.0)
				else:
					distance_txt = 'INF'

		stickFPS ('FPS ' + str(clock.get_fps()))
		stickImg (spots, screen_frame = 1)
		stickDistance ('Distance: ' + distance_txt + 'cm')
		stickImg (image, update = True)
		
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

		rawCapture.truncate(0)
	
	camera.close()
	pygame.quit ()
	GPIO.cleanup ()

# call main
__main__()
# EOF
