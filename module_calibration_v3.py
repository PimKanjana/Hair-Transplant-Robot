import numpy as np
import cv2
import glob
from numpy import *
from scipy.optimize import *
import math

class Calibration():

	def cal_with_chessboard(self):
		# termination criteria
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

		# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
		objp = np.zeros((9*6,3), np.float32)
		objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

		# Arrays to store object points and image points from all the images.
		self.objpoints = [] # 3d point in real world space
		self.imgpoints = [] # 2d points in image plane.

		images = glob.glob('*.png')

		for fname in images:

			img = cv2.imread(fname)
			
			gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

			# Find the chess board corners
			ret, corners = cv2.findChessboardCorners(gray, (9,6),None)

			# If found, add object points, image points (after refining them)
			if ret == True:
				self.objpoints.append(objp)
				
				corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
				self.imgpoints.append(corners2)

				# Draw and display the corners
				cv2.drawChessboardCorners(img, (9,6), corners2,ret)
				
				cv2.imshow('img',img)
				cv2.waitKey(500)

		cv2.destroyAllWindows()

		##calibration
		self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)

		# print("camera matrix: ", self.mtx)
		# print("k1, k2, p1, p2, k3 = ", self.dist)  # dist = distortion coefficients (k1, k2, p1, p2, k3) 

		# Computes useful camera characteristics from the camera matrix
		self.apertureWidth = 4.2
		self.apertureHeight = 2.4	# Sensor Size:	4.2 mm x 2.4 mm (for daA1920-30uc)
		self.fovx, self.fovy, self.focalLength, self.principalPoint, self.aspectRatio = cv2.calibrationMatrixValues(self.mtx, gray.shape[::-1], self.apertureWidth, self.apertureHeight)

		# print ("fovx(degree): ", self.fovx)
		# print ("fovy(degree): ", self.fovy)
		# print ("focal length(mm): ", self.focalLength)
		# print ("principal point(mm): ", self.principalPoint)
		# print ("aspect ratio(fy/fx): ", self.aspectRatio)
		
		return self.mtx, self.dist 

	def reprojection_error(self):
		## Re-projection Error
		tot_error = 0
		for i in range(len(objpoints)):
			imgpoints2, _ = cv2.projectPoints(self.objpoints[i], self.rvecs[i], self.tvecs[i], self.mtx, self.dist)
			error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
			#print(error)
			tot_error += error

		# print("Mean error: ", tot_error/len(objpoints))
		
	def undistortion(self, input_img, camera_matrix, dist_coefficient):
		
		
		h, w = input_img.shape[:2]
		self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefficient,(w,h),1,(w,h))
		# print("New camera matrix: ", self.newcameramtx)
		
		# undistort
		self.dst = cv2.undistort(input_img, camera_matrix, dist_coefficient, None, self.newcameramtx) 
		# cv2.imwrite('calibresult_uncrop.jpg', self.dst)
		# cv2.imshow('calibresult_uncrop.jpg',self.dst)
		# cv2.waitKey(0)
		
		# crop the image
		x,y,w,h = self.roi
		self.dst = self.dst[y:y+h, x:x+w]
		# cv2.imwrite('calibresult.jpg', self.dst)
		# cv2.imshow('calibresult.jpg', self.dst)
		# cv2.waitKey(0)
		# print("dist: ",self.dst)
		
		return self.newcameramtx, self.dst, self.roi

	def realworld_converter(self, newcamera_matrix, dist_coefficient, point_in_px, z_distance):
		
		u = point_in_px[0]
		v = point_in_px[1]
		
		cx = newcamera_matrix[0,2]
		cy = newcamera_matrix[1,2]
		fx = newcamera_matrix[0,0]
		fy = newcamera_matrix[1,1]

		k1 = dist_coefficient[0,0]
		k2 = dist_coefficient[0,1]
		p1 = dist_coefficient[0,2]
		p2 = dist_coefficient[0,3]
		k3 = dist_coefficient[0,4]

		x_2 = (u - cx)/fx
		y_2 = (cy - v)/fy

		def myCal(z):

			x = z[0]
			y = z[1]
			r = z[2]
			
			F = empty((3))
			F[0] = x*(1 + k1*pow(r,2) + k2*pow(r,4) + k3*pow(r,6)) + 2*p1*x*y + p2*(pow(r,2) + 2*pow(x,2)) - x_2
			F[1] = y*(1 + k1*pow(r,2) + k2*pow(r,4) + k3*pow(r,6)) + p1*(pow(r,2)+2*pow(y,2)) + 2*p2*x*y - y_2
			F[2] = pow(x,2) + pow(y,2) - pow(r,2) 
			return F

		zGuess = array([1,1,1])
		z = fsolve(myCal,zGuess)
		#print(z)

		x_prime = z[0]
		y_prime = z[1]

		x_real = x_prime*z_distance
		y_real = y_prime*z_distance

		return x_real, y_real

if __name__ == "__main__":
		
	ca = Calibration()
	
	camera_mtx, dist_coeff = ca.cal_with_chessboard()
	# print(camera_mtx)
	# print()
	# print(type(camera_mtx))
	# print(dist_coeff)
	# print(type(dist_coeff))
	
	# camera_mtx = np.array(([[1.28491691e+03,0,9.54919536e+02],[0,1.28846538e+03,5.38886871e+02],[0,0,1]]))
	# dist_coeff = np.array(([[-3.22749095e-01,1.74512521e-01,-2.02649360e-04,3.84570766e-05,-6.93426512e-02]]))
	print(camera_mtx)
	print()
	print(dist_coeff)
	input_img = cv2.imread('test_90mm.jpg')
	print("input: ",input_img)
	newcamera_mtx, undistort_img, roi = ca.undistortion(input_img, camera_mtx, dist_coeff)
	# print("undist: ",undistort_img)
	
	u1 = 192
	v1 = 149
	point_px1 = (([u1,v1]))
	
	u2 = 192
	v2 = 108
	point_px2 = (([u2,v2]))

	z_cm = 8.5
	x_cm1, y_cm1 = ca.realworld_converter(newcamera_mtx, dist_coeff, point_px1, z_cm)
	x_cm2, y_cm2 = ca.realworld_converter(newcamera_mtx, dist_coeff, point_px2, z_cm)
	print(x_cm1, y_cm1)
	print(x_cm2, y_cm2)

	displacement = math.sqrt(pow(x_cm1-x_cm2, 2) + pow(y_cm1-y_cm2, 2))
	print(displacement)
