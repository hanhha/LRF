#!/usr/bin/env python

import picamera as picam
from PIL import Image
from picamera.array import PiRGBArray
import numpy as np
import os
import RPi.GPIO as GPIO
import cv2

import curses

os.environ['SDL_VIDEODRIVER'] = 'fbcon'

imgDimensions = (800, 600)

camera = picam.PiCamera()
camera.resolution = imgDimensions 
camera.framerate = 40
camera.led = False
camera.iso = 30
camera.exposure_mode = 'snow'
rawCapture = PiRGBArray(camera, size=imgDimensions)

linear_params = {'A': 1, 'B': 0}

laserPin = 7

def laserSETUP ():
	GPIO.setup   (laserPin, GPIO.OUT)

def laserON ():
	GPIO.output (laserPin, GPIO.HIGH)

def laserOFF ():
	GPIO.output  (laserPin, GPIO.LOW)

def detectSpot (img):
	lab_img = cv2.cvtColor (img, cv2.COLOR_BGR2LAB)
	lw_range = np.array([240, 0,  0], dtype =np.uint8)
	up_range = np.array([255, 255, 255], dtype =np.uint8)
	mask = cv2.inRange (lab_img, lw_range, up_range)
	
	return mask

def getSpot (mask):
	spots = np.where (np.logical_and.reduce ((mask[0] == 255, mask[1] == 255)), 255, 0)
	return spots

def getSpotPos (spots):
	if spots[1].size == 0 or spots[0].size == 0:
		return None
	else:
		tmp = np.where (spots == 255)
		if tmp[1].size == 0 or tmp[0].size == 0:
			return None
		else:
			cx = np.sum (tmp[1]) / tmp[1].size 
			cy = np.sum (tmp[0]) / tmp[0].size 
			return (cx, cy)

def __main__ (stdscr):
	curses.init_pair (1, curses.COLOR_CYAN, curses.COLOR_BLACK)
	rate = 1
	stdscr.nodelay(1)

	GPIO.cleanup ()
	GPIO.setmode (GPIO.BOARD)
	laserSETUP   ()
	laserOFF     ()
	bg_mask      = None
	distance_txt = 'INF'
	mask         = []
	spots        = None
	laserSpot    = None
	phase        = 0

	for frame in camera.capture_continuous (rawCapture, format ="bgr", use_video_port=True):
		image = np.copy (frame.array) 

		if phase == 0:
			bg_mask = detectSpot(image)
			laserON ()
			mask = []
			phase = 1
		elif phase == 1:
			mask.append (detectSpot(image) - bg_mask)
			phase = 2
		elif phase == 2:
			mask.append (detectSpot(image) - bg_mask)
			phase = 3
		else:
			laserOFF ()
			phase = 0

			spots = getSpot (mask)
			laserSpot = getSpotPos (spots)
			if laserSpot is not None:
				p = laserSpot[0] - imgDimensions[0]/2
				if p != 0:
					distance = linear_params['A'] * float(p) + linear_params['B']
					distance_txt = str(distance) 
				else:
					distance_txt = 'INF'

		stdscr.move (1,1)
		stdscr.clrtoeol ()
		stdscr.addstr (1, 1, 'Distance: ' + distance_txt + 'cm', curses.color_pair(1))
		stdscr.refresh ()
		if stdscr.getch () == ord('q'):
			break
		
		rawCapture.truncate(0)
	
	camera.close()
	GPIO.cleanup ()

if __name__ == '__main__':
	curses.wrapper(__main__)
# EOF
