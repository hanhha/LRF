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
camera.framerate = 30
camera.led = False
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
	textSurface = myfont.render ('X' + str(spot[0]) + ' Y' + str(spot[1]), True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(forthFrame, (30,40)))))
	if update:
		pygame.display.update()

def stickDistance (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(forthFrame,(30,70)))))
	if update:
		pygame.display.update()

def stickFPS (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(thirdFrame,(30,40)))))
	if update:
		pygame.display.update()

def stickLsr (text, update = False):
	textSurface = myfont.render (text, True, (255,255,255))
	screen.blit (textSurface, tuple(map(sum,zip(thirdFrame,(30,70)))))
	if update:
		pygame.display.update()

def stickCUM (color, update = False):
	bgr = [color.b, color.g, color.r]
	hsv = cv2.cvtColor (np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
	lab = cv2.cvtColor (np.uint8([[bgr]]), cv2.COLOR_BGR2LAB)[0][0]
	textRGB = myfont.render ('R' + str(bgr[2]) + ' G' + str(bgr[1]) + ' B' + str(bgr[0]), True, (255,255,255))
	textHSV = myfont.render ('H' + str(hsv[0]) + ' S' + str(hsv[1]) + ' V' + str(hsv[2]), True, (255,255,255))
	textLAB = myfont.render ('L' + str(lab[0]) + ' A' + str(lab[1]) + ' B' + str(lab[2]), True, (255,255,255))
	screen.blit (textRGB, tuple(map(sum,zip(thirdFrame,(30,100)))))
	screen.blit (textHSV, tuple(map(sum,zip(thirdFrame,(30,130)))))
	#screen.blit (textYCB, tuple(map(sum,zip(thirdFrame,(30,160)))))
	screen.blit (textLAB, tuple(map(sum,zip(thirdFrame,(30,160)))))
	if update:
		pygame.display.update()

def cleanScreen ():
	screen.fill ((0,0,0))

def getPixelAtMouse ():
	return screen.get_at (pygame.mouse.get_pos())

def detectSpot (img):
	# invert bgr
	#inv_img = cv2.bitwise_not (img)
	# convert to lab
	#hsv_img = cv2.cvtColor (inv_img, cv2.COLOR_BGR2HSV)
	lab_img = cv2.cvtColor (img, cv2.COLOR_BGR2LAB)
	# look for high lightness
	#lw_range = np.array([90 - 10, 70,  50 ], dtype =np.uint8)
	#up_range = np.array([90 + 10, 255, 255], dtype =np.uint8)
	lw_range = np.array([240, 0,  0], dtype =np.uint8)
	up_range = np.array([255, 255, 255], dtype =np.uint8)
	mask = cv2.inRange (lab_img, lw_range, up_range)
	
	return mask

def getSpot (mask):
	spots = np.where (mask == 255)
	if spots[1].size == 0 or spots[0].size == 0:
		return None
	else:
		cx = np.sum (spots[1]) / spots[1].size 
		cy = np.sum (spots[0]) / spots[0].size 
		return (cx, cy)

def shot ():
	camera.capture (rawCapture, format="bgr")
	image = rawCapture.array
	rawCapture.truncate (0)
	return image

def __main__ ():
	GPIO.cleanup ()
	GPIO.setmode (GPIO.BOARD)
	laserSETUP ()
	initializePygame ()
	laserOFF ()
	laser_on = False

	image0 = shot ()
	bg_msk = detectSpot (image0)
	laserON ()
	laser_on = True
	time.sleep (5)
	image1 = shot ()
	fg_msk = detectSpot (image1) - bg_msk

	stickImg (image0)
	stickImg (image1, screen_frame = 1)
	stickImg (bg_msk, screen_frame = 2)
	stickImg (fg_msk, screen_frame = 3, update = True)
	
	escape = False
	while not escape:
		for event in pygame.event.get ():
			if event.type == QUIT:
				camera.close()
				pygame.quit ()
				GPIO.cleanup ()
				sys.exit ()
			if event.type == KEYDOWN and event.key == K_q:
				escape = True	
	
	camera.close()
	pygame.quit ()
	laserOFF ()
	GPIO.cleanup ()

# call main
__main__()
# EOF
