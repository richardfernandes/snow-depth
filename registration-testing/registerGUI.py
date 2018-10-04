# import necessary packages
import cv2
import numpy as np
import Tkinter as tk
import tkFileDialog
from matplotlib import pyplot as plt

# global variables
MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15

# GUI class
class GUI:
	def __init__(self):
		# open window
		self.root = tk.Tk()
		self.root.configure(background='#ffffff')
		self.root.title("Select Images")

		# variables
		self.templateDir = ""
		self.inputDir = ""

		# label
		self.label = tk.Label(
			self.root,
			text = "Register Image to Template",
			background = '#ffffff',
			foreground = '#000000',
			font = ("Calibri Light", 18))

		# buttons
		self.image1Button = tk.Button(
			self.root,
			text = "Select Template",
			background = '#ffffff',
			foreground = '#000000',
			command = lambda: self.selectFile("1"),
			width = 17,
			font = ("Calibri Light", 14))

		self.image2Button = tk.Button(
			self.root,
			text = "Select Image",
			background = '#ffffff',
			foreground = '#000000',
			command = lambda: self.selectFile("2"),
			width = 17,
			font = ("Calibri Light", 14))

		self.execute = tk.Button(
			self.root,
			text = "Register",
			background = '#ffffff',
			foreground = '#000000',
			command = lambda: self.root.destroy(),
			width = 17,
			font = ("Calibri Light", 14))

		# packing
		self.label.pack(pady = 20, padx = 50)
		self.image1Button.pack(pady = (20,5), padx = 50)
		self.image2Button.pack(pady = (5,20), padx = 50)
		self.execute.pack(pady = (5,20), padx = 50)

		self.root.mainloop()

	def selectFile(self, method):
		# open file selector
		if(method == "1"):
			self.templateDir = tkFileDialog.askopenfilename(initialdir = "/",title = "Select image",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
		elif(method == "2"):
			self.inputDir = tkFileDialog.askopenfilename(initialdir = "/",title = "Select image",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))

	def getDirs(self):
		return self.templateDir, self.inputDir

# function to align image to template
def alignImages(img1_, img2_):

	# apply median blur to highlight foreground features
	img1 = cv2.medianBlur(img1_, 5)
	img2 = cv2.medianBlur(img2_, 5)

	# convert images to grayscale
	img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
	img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

	# detect ORB features and compute descriptors
	orb = cv2.ORB_create(2500)
	kp1, desc1 = orb.detectAndCompute(img1, None)
	kp2, desc2 = orb.detectAndCompute(img2, None)

	# create brute-force matcher object
	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

	# match the descriptors
	matches = bf.match(desc1, desc2)

	# sort matches by score
	matches = sorted(matches, key = lambda x: x.distance)

	# remove poor matches
	matches = matches[:int(len(matches)*GOOD_MATCH_PERCENT)]

	# draw top matches
	imgMatches = cv2.drawMatches(img1, kp1, img2, kp2, matches, None)
	cv2.imwrite("./matches.jpg", imgMatches)

	# extract location of good matches
	points1 = np.zeros((len(matches), 2), dtype = np.float32)
	points2 = np.zeros((len(matches), 2), dtype = np.float32)

	for i, match in enumerate(matches):
		points1[i, :] = kp1[match.queryIdx].pt
		points2[i, :] = kp2[match.trainIdx].pt

	# convert numpy arrays to list
	points1 = points1.tolist()
	points2 = points2.tolist()

	# filter points to exclude poor point matching
	# points which differ by more than 150 pixels in x or y domains
	# are removed from the point lists
	for i, point in enumerate(points1):
		if(abs(point[1] - points2[i][1]) != 0 and abs(point[0] - points2[i][0]) > 100 and \
		(abs(point[0] - points2[i][0]) / abs(point[1] - points2[i][1])) < 25):
			points1.pop(i)
			points2.pop(i)

	# convert lists to numpy arrays
	points1 = np.asarray(points1)
	points2 = np.asarray(points2)

	# find homography
	h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

	# use homography
	height, width, channels = img2_.shape
	img1Reg = cv2.warpPerspective(img1_, h, (width, height))

	# return registered images and homography
	return img1Reg, h

# open GUI
gui = GUI()

template, image = gui.getDirs()

# read reference image
print("Reading reference image :", template)
imReference = cv2.imread(template)

# read image to be aligned
print("Reading image to be aligned :", image)
img = cv2.imread(image)

print("Aligning images ...")
# Registered image stored in imReg
# Estimated homography stored in h
imReg, h = alignImages(img, imReference)

# write aligned image to disk
outputFile = "aligned.jpg"
print("Saving aligned image :", outputFile)
cv2.imwrite(outputFile, imReg)

# print estimated homography
print "Estimated homography: \n", h
