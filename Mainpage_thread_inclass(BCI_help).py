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
	
	
	'''
	def OpenSerialPort(self, port=""):
		print ("Open port %s" % port)

		fio2_ser = None

		try:
			fio2_ser = serial.Serial(port,
						baudrate=9600,
						bytesize=serial.EIGHTBITS,
						parity =serial.PARITY_ODD)

		except serial.SerialException as msg:
			print( "Error opening serial port %s" % msg)

		except:
			exctype, errorMsg = sys.exc_info()[:2]
			print ("%s  %s" % (errorMsg, exctype))

		return fio2_ser

	def Camera(self, queue):
		
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
					queue.put(show_im)
					
					
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


	def Robot(self, queue, serialPort, stopped):
		print ("Hair transplant process is starting!")
		serialPort.timeout = 1.0
		while not stopped.is_set(): 
			try:
				robot = ct.Control()
				while True:			
					# distance = queue.get()
					distance = ([2.5413621708824894, 3.496339433599953])
					robot.Motors_Control(serialPort, distance)
					
			except:
				exctype, errorMsg = sys.exc_info()[:2]
				print ("Error reading port - %s" % errorMsg)
				stopped.set()
				break
		# serialPort.close()
		print("...Hair transplant process is finished...")
		
	'''	
	
	# UI section
	def openUI(self,queue):
		
		self.trigger = False
		print("trig1: ", self.trigger)
		
		# call QWidget constructor
		super().__init__()
		self.MainWindow = QtWidgets.QMainWindow()
		self.ui = mp.Ui_MainWindow()
		self.ui.setupUi(self.MainWindow)
		self.MainWindow.show()

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
		
		# sys.exit(app.exec_())
		
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
		
		
		self.trigger = True
		print("trig2: ",self.trigger)
		queue.put(trig)
		'''
		self.robot = ct.Control()
		
		self.serialPort = self.robot.OpenSerialPort('COM15')
		if self.serialPort == None: sys.exit(1)
		
		self.robot.setHome(self.serialPort)
		print("Home la na")
		
		self.queue = multiprocessing.Queue()
		self.stopped = threading.Event()
		# self.p1 = threading.Thread(target=self.Camera, args=(self.queue,))
		self.p2 = threading.Thread(target=self.Robot, args=(self.queue, self.serialPort, self.stopped,))
		# self.p3 = threading.Thread(target=self.viewCam, args=(self.queue,))
		print("thread la jaaa")
		
		# self.p1.start()
		self.p2.start()
		# self.p3.start()
		
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
		
		# Dinamixel setup
		DXL1_ID                      = 1            # Dynamixel ID : 1
		DXL2_ID                      = 2            # Dynamixel ID : 2
		DXL3_ID                      = 3            # Dynamixel ID : 3
		DXL4_ID                      = 4            # Dynamixel ID : 4
		
		dxl.torque_disable(DXL1_ID)
		dxl.torque_disable(DXL2_ID)
		dxl.torque_disable(DXL3_ID)
		dxl.torque_disable(DXL4_ID)
		
		self.dxl.close_port()
			
		'''
		
		# if timer is stopped
		if not self.timer_camera.isActive():
			
			### big window
			
			# create video capture
			self.cap = cv2.VideoCapture(0)				
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,640)  
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)			
			
			
			# start timer
			self.timer_camera.start(20)
						
			'''
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
	
	#app = QtWidgets.QApplication(sys.argv)
		
	# create and show mainWindow
	#Mainpage = Mainpage()
	#Mainpage.openUI()
	#trig = Mainpage.trigger
	
	#sys.exit(app.exec_())
	
	def gui(queue):
		global app, Mainpage
		app = QtWidgets.QApplication(sys.argv)
		
		# create and show mainWindow
		Mainpage = Mainpage()
		Mainpage.openUI(queue)
		trig = Mainpage.trigger
		print("trig3: ",trig)
		
		
		
		sys.exit(app.exec_())
	
	'''
	def OpenSerialPort(port=""):
		print ("Open port %s" % port)

		fio2_ser = None

		try:
			fio2_ser = serial.Serial(port,
						baudrate=9600,
						bytesize=serial.EIGHTBITS,
						parity =serial.PARITY_ODD)

		except serial.SerialException as msg:
			print( "Error opening serial port %s" % msg)

		except:
			exctype, errorMsg = sys.exc_info()[:2]
			print ("%s  %s" % (errorMsg, exctype))

		return fio2_ser
	'''
	
	def Camera(queue):
		
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


	def Robot(queue, serialPort, stopped):
		print ("Hair transplant process is starting!")
		serialPort.timeout = 1.0
		while not stopped.is_set(): 
			try:
				robot = ct.Control()
				while True:			
					distance = queue.get()
					# distance = ([2.5413621708824894, 3.496339433599953])
					robot.Motors_Control(serialPort, distance)

			except:
				exctype, errorMsg = sys.exc_info()[:2]
				print ("Error reading port - %s" % errorMsg)
				stopped.set()
				break
		# serialPort.close()
		print("...Hair transplant process is finished...")
		
	
	
	robot = ct.Control()
	
	serialPort = robot.OpenSerialPort('COM15')
	if serialPort == None: sys.exit(1)
	
	robot.setHome(serialPort)
	
	queue = multiprocessing.Queue()
	stopped = threading.Event()
	p1 = threading.Thread(target=gui, args=(queue, ))
	p2 = threading.Thread(target=Camera, args=(queue,))
	p3 = threading.Thread(target=Robot, args=(queue, serialPort, stopped,))
	
	p1.start()
	print('initialize p1')
	p1.join()
	# p2.start()
	# p3.start()
	
	while True:
		trig = queue.get()
		#trig = Mainpage.trigger
		print("trig4: ",trig)
		if not trig == None:
			
			if trig == True:
				print("trig5: ", trig)
		
				p2.start()
				p3.start()
				break
		
		else:
			print("No trig signal")
			
	
	
	print("Let's start")
	
	while not stopped.is_set():
		try:
			time.sleep(0.1) # 0.1 second

		except KeyboardInterrupt: #Capture Ctrl-C
			print ("Captured Ctrl-C")			
			stopped.set()
			print ("Stopped is set")
	
	serialPort.close()
	print ("Done")
	#sys.exit(0)
		
	print("The robot will stop holding its current position with in 5 seconds!")
	print("Please catch and set the robot in proper position!")
	
	time.sleep(5) 
	
	
	dxl = dm.Dinamixel()
	'''
	# Dinamixel setup
	DXL1_ID                      = 1            # Dynamixel ID : 1
	DXL2_ID                      = 2            # Dynamixel ID : 2
	DXL3_ID                      = 3            # Dynamixel ID : 3
	DXL4_ID                      = 4            # Dynamixel ID : 4
	
	dxl.torque_disable(DXL1_ID)
	dxl.torque_disable(DXL2_ID)
	dxl.torque_disable(DXL3_ID)
	dxl.torque_disable(DXL4_ID)
	'''
	
	dxl.close_port()
	
	
	'''
	def gui(queue):
		global app, Mainpage
		app = QtWidgets.QApplication(sys.argv)
		
		# create and show mainWindow
		Mainpage = Mainpage()
		Mainpage.openUI()
		sys.exit(app.exec_())
	
	def dxl_motor (queue):
	
		DXL2_ID  = 2     
		dxl = dm.Dinamixel()
		dxl.torque_enable(DXL2_ID)
		dxl2_goal_pwm = int(300)
		dxl.write_goal_pwm(DXL2_ID, dxl2_goal_pwm)
		
		
		while 1:
			dxl2_goal_position = 600
			
			dxl.write_goal_position(DXL2_ID, dxl2_goal_position)
			while 1:
				# Read present position
				dxl2_present_position = dxl.read_present_position(DXL2_ID)
				# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL3_ID, dxl3_init_position, dxl3_present_position))
				if dxl2_goal_position - 20 < dxl2_present_position < dxl2_goal_position+ 20:
					break
					
			dxl2_goal_position = 3000
			dxl.write_goal_position(DXL2_ID, dxl2_goal_position)
			while 1:
				# Read present position
				dxl2_present_position = dxl.read_present_position(DXL2_ID)
				# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL3_ID, dxl3_init_position, dxl3_present_position))
				if dxl2_goal_position - 20 < dxl2_present_position < dxl2_goal_position+ 20:
					break
		
	queue = multiprocessing.Queue()
	stopped = threading.Event()
	p1_ = threading.Thread(target=gui, args=(queue,))
	p2_ = threading.Thread(target=dxl_motor, args=(queue, ))

	p1_.start()
	p2_.start()	
	
	while not stopped.is_set():
		try:
			time.sleep(0.1) # 0.1 second

		except KeyboardInterrupt: #Capture Ctrl-C
			print ("Captured Ctrl-C")			
			stopped.set()
			print ("Stopped is set")
	
	dxl = dm.Dinamixel()
	
	dxl.close_port()
	
	'''
	
	