from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Dialog_stop import Ui_Dialog3
from Dialog_after_stop import Ui_Dialog4
from Dialog_after_after_stop import Ui_Dialog5
from Homepage import *
import Mainpage_ui as mp

import module_control as ct
import module_findDistance as fd

import sys
import cv2
from pypylon import pylon
import threading, multiprocessing
import time
import serial
import sys
import warnings
warnings.filterwarnings('ignore', 'The iteration is not making good progress')

		
		
		
# UI section
def openUI():
	
	global ui, timer_camera, date_, time_
	
	# call QWidget constructor
	# super().__init__()
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = mp.Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	

	# set timer for digital clock
	timer_datetime = QTimer()
	print(timer_datetime)
	timer_datetime.timeout.connect(update_datetime)   #update digital clock using update_datetime function
	timer_datetime.start(100)
	
	# set timer for camera
	timer_camera = QTimer()
	timer_camera.timeout.connect(viewCam)
	
	ui.playButton.clicked.connect(play_button_clicked)
	ui.pauseButton.clicked.connect(pause_button_clicked)
	ui.stopButton.clicked.connect(stop_button_clicked)
	
	sys.exit(app.exec_())
# update digital clock 
def update_datetime():
	
	date_ = QDate.currentDate()
	time_ = QTime.currentTime()
	ui.label_date.setText("<font color='#f8edd4'>" + date_.toString(Qt.ISODate) + "</font>")
	ui.label_time.setText("<font color='#f8edd4'>" + time_.toString() + "</font>")

	
# view camera
def viewCam():
	global grabResult 
	
	### big window
	'''
	# read image in BGR format
	ret, image = self.cap.read()
	# convert image to RGB format
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	# get image infos
	height, width, channel = image.shape
	step = channel * width
	# create QImage from image
	qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
	# show image in img_label
	self.label_camera.setPixmap(QPixmap.fromImage(qImg))
	self.label_camera.setScaledContents(True)
	'''
	
	
	### small window
	
	grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
	
	if grabResult.GrabSucceeded():
		# Access the image data
		image2 = converter.Convert(grabResult)
		img2 = image2.GetArray()
					
					
		# distance = ([x_distance, y_distance])
		fdist = fd.FindingDistance()
		distance = fdist.Distance(img2)
		
		robot.DXL_Control(serialPort, distance)
		
		show_im = fdist.ip_Orb.reimg
		
		# get image infos
		height2, width2, channel2 = show_im.shape
		step2 = channel2 * width2
		# create QImage from image
		qImg2 = QImage(show_im.data, width2, height2, step2, QImage.Format_RGB888)
		# show image in img_label
		ui.label_camera2.setPixmap(QPixmap.fromImage(qImg2))
		ui.label_camera2.setScaledContents(True)
	
	
def play_button_clicked():
	
	global camera, converter
	
	# robot = ct.Control()
	
	# serialPort = robot.OpenSerialPort('COM15')
	# if serialPort == None: sys.exit(1)
	
	# robot.setHome(serialPort)
		
	# if timer is stopped
	if not timer_camera.isActive():
		
		### big window
		'''
		# create video capture
		self.cap = cv2.VideoCapture(0)				
		# self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,640)  
		# self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)			
		'''
		
		# start timer
		timer_camera.start(20)
					
		
		### small window
		
		# conecting to the first available camera
		camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
	
		# Grabing Continusely (video) with minimal delay
		camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
		converter = pylon.ImageFormatConverter()

		# converting to opencv bgr format
		converter.OutputPixelFormat = pylon.PixelType_RGB8packed
		converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

	
def pause_button_clicked():
		
	# stop timer
	timer_camera.stop()
	
	### big window
	'''
	# release video capture
	self.cap.release()
	'''
	
	
	
	### small window
	# Releasing grab result
	grabResult.Release()
	# Releasing the resource    
	camera.StopGrabbing()
	
def stop_button_clicked():
	
	Dialog3 = QtWidgets.QDialog()
	ui3 = Ui_Dialog3()
	ui3.setupUi(Dialog3)
	Dialog3.show()
	rsp3 = Dialog3.exec_()
	
	if rsp3 == QtWidgets.QDialog.Accepted:
		Dialog4 = QtWidgets.QDialog()
		ui4 = Ui_Dialog4()
		ui4.setupUi(Dialog4)
		Dialog4.show()
		rsp4 = Dialog4.exec_()
		
		if rsp4 == QtWidgets.QDialog.Accepted:
			Dialog5 = QtWidgets.QDialog()
			ui5 = Ui_Dialog5()
			ui5.setupUi(Dialog5)
			Dialog5.show()
			rsp5 = Dialog5.exec_()
			
			if rsp5 == QtWidgets.QDialog.Accepted:
				# stop timer
				timer_camera.stop()
				
				### big window
				'''
				# release video capture
				self.cap.release()
				'''
				
									
				### small window
				# Releasing grab result
				grabResult.Release()
				# Releasing the resource    
				camera.StopGrabbing()
				
				# app = QtWidgets.QApplication(sys.argv)
				# sys.exit(app.exec_())
				
	else:
		pass
	

if __name__ == "__main__":
	
	
	# app = QtWidgets.QApplication(sys.argv)
	
	# create and show mainWindow
	mainpage = openUI()
	
	# sys.exit(app.exec_())

			
