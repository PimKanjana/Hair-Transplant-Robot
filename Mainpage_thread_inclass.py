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
import module_dxl as dm
import sys
import cv2
from pypylon import pylon

import threading, multiprocessing
import time
import serial
import sys
import warnings
warnings.filterwarnings('ignore', 'The iteration is not making good progress')


class Mainpage(QWidget):

	def Camera(self, queue, queue2):
		
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
				
				# Find distance between target and needle position
				try:
					fdist = fd.FindingDistance(img)
					distance = fdist.real_distance
					
					# send out distance values to control thread
					queue.put(distance)
					
					show_im = fdist.ip_Orb.reimg
					queue2.put(show_im)
					
					
				except:
					print("No distance")
					# pass
				
				
				k = cv2.waitKey(1)
				if k == 27:
					break
				
			grabResult.Release()

		# Releasing the resource    
		camera.StopGrabbing()

		cv2.destroyAllWindows()


	def RobotTask(self, queue, serialPort, stopped, queue2):
		print ("Hair transplant process is starting!")
		serialPort.timeout = 1.0
		while not stopped.is_set(): 
			try:
				robot = ct.Control()
				while True:			
					while not queue.empty():
						distance = queue.get()
						print("distance: ", distance)
				
						# distance = ([2.5413621708824894, 3.496339433599953])
						robot.Motors_Control(serialPort, distance)
						
						picture = queue2.get()
						print("picture: ", picture)
			except:
				exctype, errorMsg = sys.exc_info()[:2]
				print ("Error reading port stopped.set()
				break
		# serialPort.close()
		print("...Hair transplant process is finished...")
		
	
	
	# UI section
	def openUI(self):
		
				
		# call QWidget constructor
		super().__init__()
		self.MainWindow = QtWidgets.QMainWindow()
		self.ui = mp.Ui_MainWindow()
		self.ui.setupUi(self.MainWindow)
		self.MainWindow.show()
		
		self.robot = ct.Control()
		
		self.serialPort = self.robot.OpenSerialPort('COM15')
		if self.serialPort == None: sys.exit(1)
		
		self.robot.setHome(self.serialPort)
		# print("Home la na")
		
		self.queue = multiprocessing.Queue()
		self.queue2 = multiprocessing.Queue()
		self.stopped = threading.Event()
		self.p1 = threading.Thread(target=self.Camera, args=(self.queue, self.queue2))
		self.p2 = threading.Thread(target=self.RobotTask, args=(self.queue, self.serialPort, self.stopped,self.queue2,))
		
		# print("thread la jaaa")
		
		self.p1.start()
		self.p2.start()
	
		
		print("Let's start")
		
		while not self.stopped.is_set():
			try:
				time.sleep(0.1) # 0.1 second

			except KeyboardInterrupt: #Capture Ctrl-C
				print ("Captured Ctrl-C")			
				self.stopped.set()
				print ("Stopped is set")
		
		self.serialPort.close()
		print ("Done")
		#sys.exit(0)
			
		print("The robot will stop holding its current position with in 5 seconds!")
		print("Please catch and set the robot in proper position!")
		
		time.sleep(5) 
		
		
		self.dxl = dm.Dinamixel()	
		self.dxl.close_port()

		
		# set timer for digital clock
		self.timer_datetime = QTimer()
		self.timer_datetime.timeout.connect(self.update_datetime)   #update digital clock using update_datetime function
		self.timer_datetime.start(100)
		
		# set timer for camera
		self.timer_camera = QTimer()
		self.timer_camera.timeout.connect(self.viewCam)
		
		self.ui.playButton.clicked.connect(self.play_button_clicked)
		
		self.ui.pauseButton.clicked.connect(self.pause_button_clicked)
		self.ui.stopButton.clicked.connect(self.stop_button_clicked)
		
		sys.exit(app.exec_())
		
	# update digital clock 
	def update_datetime(self):
		date_ = QDate.currentDate()
		time_ = QTime.currentTime()
		self.ui.label_date.setText("<font color='#f8edd4'>" + date_.toString(Qt.ISODate) + "</font>")
		self.ui.label_time.setText("<font color='#f8edd4'>" + time_.toString() + "</font>")

		
	# view camera
	def viewCam(self):
		
		### big window
		
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
		self.ui.label_camera.setPixmap(QPixmap.fromImage(qImg))
		self.ui.label_camera.setScaledContents(True)
		
		
		'''
		### small window
		self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
	
		if self.grabResult.GrabSucceeded():
			# Access the image data
			image2 = self.converter.Convert(self.grabResult)
			img2 = image2.GetArray()
		
		# show_im = queue.get()			
		# get image infos
		height2, width2, channel2 = img2.shape
		step2 = channel2 * width2
		# create QImage from image
		qImg2 = QImage(img2.data, width2, height2, step2, QImage.Format_RGB888)
		# show image in img_label
		self.ui.label_camera2.setPixmap(QPixmap.fromImage(qImg2))
		self.ui.label_camera2.setScaledContents(True)
		'''
		
	def play_button_clicked(self):
						
		
		# if timer is stopped
		# if not self.timer_camera.isActive():
		
		
		
		'''
		### big window
		
		# create video capture
		self.cap = cv2.VideoCapture(0)				
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,640)  
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)			
		
		
		# start timer
		self.timer_camera.start(20)
					
		
		### small window
		
		# conecting to the first available camera
		self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
	
		# Grabing Continusely (video) with minimal delay
		self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
		self.converter = pylon.ImageFormatConverter()

		# converting to opencv bgr format
		self.converter.OutputPixelFormat = pylon.PixelType_RGB8packed
		self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
		'''
		
	def pause_button_clicked(self):
		
			
		# stop timer
		self.timer_camera.stop()
		
		### big window
		
		
		# release video capture
		self.cap.release()
		
		'''
		### small window
		# Releasing grab result
		self.grabResult.Release()
		# Releasing the resource    
		self.camera.StopGrabbing()
		'''
		
	def stop_button_clicked(self):
		
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
				
				# if rsp5 == QtWidgets.QDialog.Accepted:
					
		else:
			pass
		

if __name__ == "__main__":
	
	
	app = QtWidgets.QApplication(sys.argv)
		
	# create and show mainWindow
	Mainpage = Mainpage()
	Mainpage.openUI()
	
	sys.exit(app.exec_())
	
	
