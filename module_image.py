import cv2
import numpy as np
import sys

class ImageProcessing():
	
	global reimg, img_with_bounding
	
	def __init__(self, img, feature):
		
		# sharpening
		gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		blurred = cv2.bilateralFilter(gray_image, 9, 75, 75)
		gray_image = cv2.addWeighted(gray_image, 1.5, blurred, -0.5, 0)
		gray_image = cv2.bilateralFilter(gray_image, 9, 75, 75)
	
		# Extract ROI		
		x,y,w,h = cv2.boundingRect(gray_image)   # (x=0,y=0,w=1920,h=1080)
		#print("x,y,w,h: ", x,y,w,h)
		self.roi = img[y+int(h/2.5):y + h-int(h/2.5) , x+int(w/2.5):x + w-int(w/2.5)]
		
		# Draw a bounding of ROI
		self.img_with_bounding = img.copy()
		cv2.rectangle(self.img_with_bounding, (x+int(w/2.5), y+int(h/2.5)), (x + w-int(w/2.5), y + h-int(h/2.5)), (0, 0, 255), 2)
		
		# Find Needle position
		self.gray_roi = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)
		x,y,w,h = cv2.boundingRect(self.gray_roi)
		#print("xr,yr,wr,hr: ", x,y,w,h)
		self.needle_pose = np.array([[w/2, h/2]]) 
		
		# Otsu's thresholding
		ret,self.th = cv2.threshold(self.gray_roi,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		
		# Otsu's thresholding after Gaussian filtering
		self.blur = cv2.GaussianBlur(self.gray_roi,(5,5),0)
		ret2,self.th2 = cv2.threshold(self.blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		
		# Morphological filtering
		kernel = np.ones((2,2),np.uint8)
		self.dilation = cv2.dilate(self.th,kernel,iterations = 1)
		#opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
		
		if feature == 'ORB':
			# Initiate ORB object
			orb = cv2.ORB_create(nfeatures = 5000, scaleFactor = 1.1, nlevels = 10, scoreType = cv2.ORB_FAST_SCORE, patchSize = 100)

			# find the keypoints with ORB
			keypoints = orb.detect(self.gray_roi, None)

			# compute the descriptors with ORB
			keypoints, descriptors = orb.compute(self.gray_roi, keypoints)
			self.point2f = cv2.KeyPoint_convert(keypoints)

			# retval = cv2.ORB.getMaxFeatures(orb)
			# print('retval: ',retval)
			# print('number of Kp: ', len(keypoints))
		elif feature == 'FAST':
			# Initiate FAST object with default values
			fast = cv2.FastFeatureDetector_create(10,True,2)  

			# TYPE_5_8 = 0, TYPE_7_12 = 1, TYPE_9_16 = 2

			# find and draw the keypoints
			keypoints = fast.detect(self.th2, None)
			self.point2f = cv2.KeyPoint_convert(keypoints)
		
		elif feature == 'BLOB':
			# Setup SimpleBlobDetector parameters.
			params = cv2.SimpleBlobDetector_Params()

			# Change thresholds
			params.minThreshold = 10
			params.maxThreshold = 200

			# Filter by Area.
			params.filterByArea = True
			params.minArea = 5

			# Filter by Circularity
			params.filterByCircularity = True
			params.minCircularity = 0.1

			# Filter by Convexity
			params.filterByConvexity = True
			params.minConvexity = 0.5

			# Filter by Inertia
			params.filterByInertia = True
			params.minInertiaRatio = 0.01

			# Create a detector with the parameters
			ver = (cv2.__version__).split('.')
			if int(ver[0]) < 3:
				detector = cv2.SimpleBlobDetector(params)
			else:
				detector = cv2.SimpleBlobDetector_create(params)

			# Detect blobs.
			keypoints = detector.detect(self.gray_roi)
			self.point2f = cv2.KeyPoint_convert(keypoints)
		
		else:
			print('Error in feature type')
			sys.exit(1)
			
		# draw only the location of the keypoints without size or orientation
		self.final_keypoints = cv2.drawKeypoints(self.roi, keypoints, None, color=(0,255,0), flags=0)

		# split channel
		b_channel, g_channel, r_channel = cv2.split(self.final_keypoints)
		alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 50 #creating a dummy alpha channel image.
		img_BGRA = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
		
		# Create new layers
		layer_1 = np.zeros((h, w, 4))
		layer_2 = np.zeros((h, w, 4))
		
		# Draw a blue line with thickness of 1 px on layer_1
		cv2.line(layer_1,(int(w/2)-20,int(h/2)),(int(w/2)+20,int(h/2)),(255,0,0,255),1)
		cv2.line(layer_1,(int(w/2),int(h/2)-20),(int(w/2),int(h/2)+20),(255,0,0,255),1)
		
		# cv2.line(layer_1,(int(w/2)-60,int(h/2)),(int(w/2)-20,int(h/2)),(255,0,0,255),1)
		# cv2.line(layer_1,(int(w/2)-40,int(h/2)-20),(int(w/2)-40,int(h/2)+20),(255,0,0,255),1)
		
		# Draw a red closed circle on layer_2
		cv2.circle(layer_2,(int(w/2),int(h/2)), 10, (0,0,255,255), 1)
		
		# copy the first layer into the resulting image
		self.reimg = img_BGRA[:]  
		
		#overlay each drawing parts
		cnd = layer_1[:, :, 3] > 0
		self.reimg[cnd] = layer_1[cnd]
		cnd = layer_2[:, :, 3] > 0
		self.reimg[cnd] = layer_2[cnd]

if __name__ == "__main__":

	input_image = cv2.imread("calibresult.jpg")
	imp = ImageProcessing(input_image, 'ORB')
	
	cv2.namedWindow('ORB keypoints', cv2.WINDOW_NORMAL)
	cv2.imshow('ORB keypoints', imp.reimg)
	
	# cv2.namedWindow('title', cv2.WINDOW_NORMAL)
	# cv2.imshow('title', imp.dilation)
	
	cv2.namedWindow('title', cv2.WINDOW_NORMAL)
	cv2.imshow('title', imp.img_with_bounding)
	
	cv2.waitKey(0)
	print(imp.point2f)
	print(imp.needle_pose)
	print(type(imp.point2f))
	
	
	
	
	
	
	
	
	