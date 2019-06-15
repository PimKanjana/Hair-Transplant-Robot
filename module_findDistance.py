from pypylon import pylon
import cv2
import numpy as np
import module_image as im
import math
import module_calibration_v3 as ca

class FindingDistance():
	
	def __init__(self, img):
		
		# global shape_Blob, shape_Orb 
		
		calib = ca.Calibration()

		'''
		camera_mtx, dist_coeff = calib.cal_with_chessboard()
		# Note: you can use the module_calibration.py to get the camera_mtx and dist_coeff before run this script and ignore the above line
		'''
		# camera_mtx = np.array([[1.29318816e+03, 0.00000000e+00, 9.87300897e+02],[0.00000000e+00, 1.29381128e+03, 5.42173382e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
		# dist_coeff = np.array([[-0.30326631,0.11434278,-0.00238106,0.00098426, 0.00104268]])

		# camera_mtx = np.array([[1.29982528e+03, 0.00000000e+00, 9.79805260e+02],[0.00000000e+00, 1.30015101e+03, 5.30700673e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
		# dist_coeff = np.array([[-3.18230575e-01, 1.62160810e-01, -5.38303677e-04, -1.33312489e-05, -6.13006122e-02]])

		camera_mtx = np.array([[1.29760392e+03, 0.00000000e+00, 9.86416590e+02],[0.00000000e+00, 1.29751992e+03, 5.25766518e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
		dist_coeff = np.array([[-0.29074228, -0.01329975, -0.00066982, 0.0004208, 0.24864]])
				
		newcamera_mtx, undistort_img, roi = calib.undistortion(img, camera_mtx, dist_coeff)

		cx = newcamera_mtx[0,2]
		cy = newcamera_mtx[1,2]
		fx = newcamera_mtx[0,0]
		fy = newcamera_mtx[1,1]

		x = roi[0]
		y = roi[1]
		w = roi[2]
		h = roi[3]			

				
		self.ip_Blob = im.ImageProcessing(undistort_img, 'BLOB')

		self.ip_Orb = im.ImageProcessing(undistort_img, 'ORB')

		# cv2.namedWindow('BLOB keypoints', cv2.WINDOW_NORMAL)
		# cv2.imshow('BLOB keypoints', self.ip_Blob.reimg)
		# cv2.imwrite('BLOB_result_1.jpg', self.ip_Blob.reimg)
		# shape_Blob = ip_Blob.point2f.shape 
		try:
			shape_Blob = self.ip_Blob.point2f.shape 
		except:
			print("Hello_blob")
								
		# cv2.namedWindow('ORB keypoints', cv2.WINDOW_NORMAL)
		# cv2.imshow('ORB keypoints', self.ip_Orb.reimg)
		# cv2.imwrite('ORB_result_1.jpg', self.ip_Orb.reimg)
		# shape_Orb = ip_Orb.point2f.shape
		try:
			shape_Orb = self.ip_Orb.point2f.shape
		except:
			print("Hello_orb")
			
		# cv2.namedWindow('Gray Image', cv2.WINDOW_NORMAL)
		# cv2.imshow('Gray Image', self.ip_Blob.gray_roi)
		# cv2.imwrite('Gray Image_1.jpg', self.ip_Blob.gray_roi)

		s = (shape_Orb[0], 2)
		diff = np.zeros(s)

		if (range(shape_Blob[0])) or (range(shape_Orb[0])):
			try:
				distance_min = 10000
				for i in range(shape_Blob[0]):
					distance = math.sqrt(math.pow(self.ip_Blob.needle_pose[0,0] - self.ip_Blob.point2f[i,0], 2) + math.pow(self.ip_Blob.needle_pose[0,1] - self.ip_Blob.point2f[i,1] ,2))
					if distance < distance_min:
						distance_min = distance
						selected_point = np.array([[self.ip_Blob.point2f[i,0], self.ip_Blob.point2f[i,1]]])
							
				k = 0
				hair_group = np.zeros((1,2))
				other = np.zeros((1,2))
				for j in range(shape_Orb[0]):
					diff[k,0] = abs(self.ip_Orb.point2f[j,0] - selected_point[0,0])
					diff[k,1] = abs(self.ip_Orb.point2f[j,1] - selected_point[0,1])
					if diff[k,0] < 40 and diff[k,1] < 40:
					# if diff[k,0] < 15 and diff[k,1] < 20:
						hair_group = np.append(hair_group, [[self.ip_Orb.point2f[j,0], self.ip_Orb.point2f[j,1]]], axis=0)	
					else:
						other = np.append(other, [[self.ip_Orb.point2f[j,0], self.ip_Orb.point2f[j,1]]], axis=0)	
					k = k+1
				hair_group = np.delete(hair_group,0,0)
				other = np.delete(other,0,0)
				
				
				# x_min = 10000
				# for i in range(hair_group.shape[0]):
					# x_ = hair_group[i,0]
					# if x_ < x_min:
						# x_min = x_
						# target_point_px_imageframeRef = hair_group[i]
				
				
				y_max = 0
				for i in range(hair_group.shape[0]):
					y_ = hair_group[i,1]
					if y_ > y_max:
						y_max = y_
						target_point_px_imageframeRef = hair_group[i]
				#print("TP_Iref: ",target_point_px_imageframeRef )
				target_point_px_calframeRef = ([target_point_px_imageframeRef[0]+746, target_point_px_imageframeRef[1]+399])
				#print("TP_Cref: ",target_point_px_calframeRef)
				
				z_mm = 80 
				x_mm, y_mm = calib.realworld_converter(newcamera_mtx, dist_coeff, target_point_px_calframeRef, z_mm)
				target_point_mm = ([x_mm, y_mm])
				
				#center_point_px_calframeRef = ([w/2, h/2])
				center_point_px_calframeRef = ([cx-x, cy-y])
				cx_mm, cy_mm = calib.realworld_converter(newcamera_mtx, dist_coeff, center_point_px_calframeRef, z_mm)
				x_distance = abs(x_mm-cx_mm) 
				y_distance = abs(y_mm-cy_mm)
				self.real_distance = ([x_distance, y_distance])
				
			except:
				print("No point")
			
		# return self.real_distance
		
if(__name__=='__main__'):

	# img = cv2.imread("calibresult.jpg")
	
	# conecting to the first available camera
	camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

	# Grabing Continusely (video) with minimal delay
	camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
	##camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
	##camera.StartGrabbing(pylon.GrabStrategy_LatestImages)
	converter = pylon.ImageFormatConverter()

	# converting to opencv bgr format
	converter.OutputPixelFormat = pylon.PixelType_BGR8packed
	converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

	while camera.IsGrabbing():
		grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

		if grabResult.GrabSucceeded():
			# Access the image data
			image = converter.Convert(grabResult)
			img = image.GetArray()
	
			fd = FindingDistance(img)
			print(fd.real_distance)
			k = cv2.waitKey(1)
			if k == 27:
				break
			
		grabResult.Release()

	# Releasing the resource    
	camera.StopGrabbing()

	cv2.destroyAllWindows()
	
	
	

	
	
	
	
	