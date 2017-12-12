import picamera as picam
from PIL import Image
from picamera.array import PiRGBArray
import time
import cv2
import pygame

imgDimensions = (320, 240) 

camera = picam.PiCamera()
camera.resolution = imgDimensions 
camera.framerate  = 32
#camera.iso        = 200
rawCapture = PiRGBArray(camera, size=imgDimensions)

def shot ():
	camera.capture (rawCapture, format="bgr")
	image = rawCapture.array
	rawCapture.truncate (0)
	return image

def __main__ ():
	pygame.init()
	image_color = shot()
	screen = pygame.display.set_mode (imgDimensions, 0, 32)
	pygameSurface = pygame.surfarray.make_surface (image_color.swapaxes(0,1))
	screen.blit (pygameSurface, (0,0))
	pygame.display.update()
	
	
	time.sleep(2)
	pygame.quit ()
	camera.close ()
	print ("end")	

# call main
__main__()
# EOF
