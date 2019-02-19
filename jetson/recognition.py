# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

last_position = (0, 0, 0)

class Recognition:
	def __init__(self):
		self.last_position = (0, 0, 0)
	
	def process_coordinates(self, x, y, radius):
		if abs(self.last_position[0] - x) > 100 or abs(self.last_position[1] - y) > 100:
			print('error case')
		else:
			# center is at x = 300
			# radius of 30 is the stopping point
			if x < 250:
				print('turn left')
			elif x > 350:
				print('turn right')
			else:
				if(radius < 30):
					print('move forwards')
				else:
					print('stationary')
		self.last_position = (x, y, radius)

	def begin(self):
		# define the lower and upper boundaries of the "green"
		# ball in the HSV color space, then initialize the
		# list of tracked points
		greenLower = (29, 86, 6)
		greenUpper = (64, 255, 255)
		pts = deque(maxlen=64)
		 
		# if a video path was not supplied, grab the reference
		# to the webcam
		
		vs = VideoStream(src=1).start()
		 
		# allow the camera or video file to warm up
		time.sleep(2.0)

		# keep looping
		while True:
			# grab the current frame
			frame = vs.read()
		 
			# if we are viewing a video and we did not grab a frame,
			# then we have reached the end of the video
			if frame is None:
				print("Frame is none")
				break
		 
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
		 
			# only proceed if at least one contour was found
			if len(cnts) > 0:
				# find the largest contour in the mask, then use
				# it to compute the minimum enclosing circle and
				# centroid
				c = max(cnts, key=cv2.contourArea)
				((x, y), radius) = cv2.minEnclosingCircle(c)
		
				self.process_coordinates(x, y, radius)		
	
				M = cv2.moments(c)
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		 
				# only proceed if the radius meets a minimum size
				if radius > 10:
					# draw the circle and centroid on the frame,
					# then update the list of tracked points
					cv2.circle(frame, (int(x), int(y)), int(radius),
						(0, 255, 255), 2)
					cv2.circle(frame, center, 5, (0, 0, 255), -1)
		 
			# update the points queue
			pts.appendleft(center)

			# loop over the set of tracked points
			for i in range(1, len(pts)):
				# if either of the tracked points are None, ignore
				# them
				if pts[i - 1] is None or pts[i] is None:
					continue
		 
				# otherwise, compute the thickness of the line and
				# draw the connecting lines
				thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
				cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
		 
			# show the frame to our screen
			cv2.imshow("Frame", frame)
			key = cv2.waitKey(1) & 0xFF
		 
			# if the 'q' key is pressed, stop the loop
			if key == ord("q"):
				break
		 
		# if we are not using a video file, stop the camera video stream
		if not args.get("video", False):
			vs.stop()
		 
		# otherwise, release the camera
		else:
			vs.release()
		 
		# close all windows
		cv2.destroyAllWindows()

