# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

last_position = (0, 0, 0)
vs = VideoStream(src=1).start()
time.sleep(2.0)

def process_coordinates(x, y, radius):
	print('processing coordinates')
	last_position = (x, y, radius)

	if abs(last_position[0] - x) > 100 or abs(last_position[1] - y) > 100:
		# error case
		return b'5'
	else:
		# center is at x = 300
		# radius of 30 is the stopping point
		if x < 200:
			# turn right
			return b'3'
		elif x > 400:
			# turn left
			return b'4'
		else:
			if(radius < 30):
				# forwards
				return b'1'
			else:
				# stationary
				return b'0'

def process_frame():
	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space, then initialize the
	# list of tracked points
	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)
	pts = deque(maxlen=64)

	print('processing')
	# grab the current frame
	frame = vs.read()
	print('got frame')		 

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		print("Frame is none")
		return "ERROR"
		 
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
		 
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
			
	print('frame math complete')
		 
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		
		command = process_coordinates(x, y, radius)		
		print('coordinates processed')	
	
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		
		 
	return command

