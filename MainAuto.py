from pypylon import pylon
import cv2
import module_control as ct
import module_findDistance as fd
import module_dxl as dm
import threading, multiprocessing
import time
import serial
import sys
import warnings
warnings.filterwarnings('ignore', 'The iteration is not making good progress')

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
	

if(__name__=='__main__'):
	
	robot = ct.Control()
	
	serialPort = robot.OpenSerialPort('COM15')
	if serialPort == None: sys.exit(1)
	
	robot.setHome(serialPort)
	
	queue = multiprocessing.Queue()
	stopped = threading.Event()
	p1 = threading.Thread(target=Camera, args=(queue,))
	p2 = threading.Thread(target=Robot, args=(queue, serialPort,stopped,))

	p1.start()
	p2.start()
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
	
	