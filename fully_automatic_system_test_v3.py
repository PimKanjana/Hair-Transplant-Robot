from pypylon import pylon
import cv2
import numpy as np
import module_image as im
import math
import module_calibration_v3 as ca
import module_inverse_kinematic as ik
import module_dxl as dm
import module_dc as dc
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

def camera(queue):
	
	global ip_Blob, ip_Orb

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
			#print(img)
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
			
						
			ip_Blob = im.ImageProcessing(undistort_img, 'BLOB')
			
			ip_Orb = im.ImageProcessing(undistort_img, 'ORB')
			
			cv2.namedWindow('BLOB keypoints', cv2.WINDOW_NORMAL)
			cv2.imshow('BLOB keypoints', ip_Blob.reimg)
			cv2.imwrite('BLOB_result_1.jpg', ip_Blob.reimg)
			# shape_Blob = ip_Blob.point2f.shape 
			try:
				shape_Blob = ip_Blob.point2f.shape 
			except:
				print("Hello_blob")
									
			cv2.namedWindow('ORB keypoints', cv2.WINDOW_NORMAL)
			cv2.imshow('ORB keypoints', ip_Orb.reimg)
			cv2.imwrite('ORB_result_1.jpg', ip_Orb.reimg)
			# shape_Orb = ip_Orb.point2f.shape
			try:
				shape_Orb = ip_Orb.point2f.shape
			except:
				print("Hello_orb")
			cv2.namedWindow('Gray Image', cv2.WINDOW_NORMAL)
			cv2.imshow('Gray Image', ip_Blob.gray_roi)
			cv2.imwrite('Gray Image_1.jpg', ip_Blob.gray_roi)
			
			
			s = (shape_Orb[0], 2)
			diff = np.zeros(s)
			
			
			if (range(shape_Blob[0])) or (range(shape_Orb[0])):
				try:
					distance_min = 10000
					for i in range(shape_Blob[0]):
						distance = math.sqrt(math.pow(ip_Blob.needle_pose[0,0] - ip_Blob.point2f[i,0], 2) + math.pow(ip_Blob.needle_pose[0,1] - ip_Blob.point2f[i,1] ,2))
						if distance < distance_min:
							distance_min = distance
							selected_point = np.array([[ip_Blob.point2f[i,0], ip_Blob.point2f[i,1]]])
								
					k = 0
					hair_group = np.zeros((1,2))
					other = np.zeros((1,2))
					for j in range(shape_Orb[0]):
						diff[k,0] = abs(ip_Orb.point2f[j,0] - selected_point[0,0])
						diff[k,1] = abs(ip_Orb.point2f[j,1] - selected_point[0,1])
						if diff[k,0] < 40 and diff[k,1] < 40:
						# if diff[k,0] < 15 and diff[k,1] < 20:
							hair_group = np.append(hair_group, [[ip_Orb.point2f[j,0], ip_Orb.point2f[j,1]]], axis=0)	
						else:
							other = np.append(other, [[ip_Orb.point2f[j,0], ip_Orb.point2f[j,1]]], axis=0)	
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
					real_distance = ([x_distance, y_distance])
					
				except:
					print("No point")
			
			queue.put(real_distance)
			# queue.put(target_point_px)
			
			k = cv2.waitKey(1)
			if k == 27:
				break
			
		grabResult.Release()

	# Releasing the resource    
	camera.StopGrabbing()

	cv2.destroyAllWindows()


def control(queue, serialPort, stopped):
	print ("Hair transplant process is starting!")
	serialPort.timeout = 1.0
	while not stopped.is_set(): 
		try:
			# Dinamixel setup
			DXL1_ID                      = 1            # Dynamixel ID : 1
			DXL2_ID                      = 2            # Dynamixel ID : 2
			DXL3_ID                      = 3            # Dynamixel ID : 3
			DXL4_ID                      = 4            # Dynamixel ID : 4
			
			dxl1_init_position = 2190   # initialize goal position
			dxl2_init_position = -400   # center = 2900
			dxl3_init_position = 1400
			dxl4_init_position = 3500
			
			dxl1_init_pwm = 300
			dxl2_init_pwm = 400
			dxl3_init_pwm = 885
			dxl4_init_pwm = 885

			dxl = dm.Dinamixel()
			dxl.torque_enable(DXL1_ID)
			dxl.torque_enable(DXL2_ID)
			dxl.torque_enable(DXL3_ID)
			dxl.torque_enable(DXL4_ID)

			dxl.write_goal_pwm(DXL1_ID, dxl1_init_pwm)
			dxl.write_goal_pwm(DXL2_ID, dxl2_init_pwm)
			dxl.write_goal_pwm(DXL3_ID, dxl3_init_pwm)
			dxl.write_goal_pwm(DXL4_ID, dxl4_init_pwm)
			
			dxl.write_goal_position(DXL1_ID, dxl1_init_position)
			dxl.write_goal_position(DXL2_ID, dxl2_init_position)
			dxl.write_goal_position(DXL3_ID, dxl3_init_position)
			dxl.write_goal_position(DXL4_ID, dxl4_init_position)

			# DC setup
			d = dc.Dc()
				
			while 1:	
			
				real_distance = queue.get()
				width = real_distance[0]
				height = real_distance[1]
				print('w,h: ',width, height)
				
									
				invki = ik.InverseKinematic(width, height)
				angle_1 = invki.finding_Phi()
				angle_2 = invki.finding_Psi()
				print('phi, psi: ',angle_1, angle_2)
				
				# angle_1 = input("phi: ")
				# angle_2 =input("phi: ")
				
				
				# Dynamixel Target Goal Position
				pos_x = angle_1 * 57
				#pos_x = 2417
				pos_y = angle_2 * 81
				#pos_y = -70
				trans_needle = 2587  # trans_needle = 52*distance_mm
				trans_stick = 2000
				dxl2_center_position = 2900   # = 70*81
				
				# Goal Position for Harvest
				dxl1_goal_position_h = int(dxl1_init_position + pos_x)
				# dxl1_goal_position_h = int(pos_x)
				dxl2_goal_position_h = int(dxl2_init_position + pos_y)
				# dxl2_goal_position_h = int(pos_y)
				dxl3_goal_position_h = int(trans_needle)
				
				# Goal Position for Implant
				#dxl1_goal_position_i = int(dxl1_init_position + pos_x)
				dxl2_goal_position_i = int(dxl2_center_position + (dxl2_center_position - dxl2_goal_position_h))
				dxl3_goal_position_i = int(trans_needle)
				dxl4_goal_position_i = int(trans_stick)
				
				# Harvest Phase
				## set needle position
				dxl.write_goal_position(DXL1_ID, dxl1_goal_position_h)	
				dxl.write_goal_position(DXL2_ID, dxl2_goal_position_h)
				while 1:
					# Read present position
					dxl1_present_position = dxl.read_present_position(DXL1_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL1_ID, dxl1_goal_position_h, dxl1_present_position))
					dxl2_present_position = dxl.read_present_position(DXL2_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL2_ID, dxl2_goal_position_h, dxl2_present_position))
					if (dxl1_goal_position_h - 20 < dxl1_present_position < dxl1_goal_position_h + 20) and (dxl2_goal_position_h - 20 < dxl2_present_position < dxl2_goal_position_h + 20):
						break
											
				## rotate needle: CW
				direction_var = str(1)
				d.rotate_dc(direction_var, serialPort)
				
				## inject needle 
				dxl.write_goal_position(DXL3_ID, dxl3_goal_position_h)
				
				while 1:
					# Read present position
					dxl3_present_position = dxl.read_present_position(DXL3_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL3_ID, dxl3_goal_position_h, dxl3_present_position))
					if dxl3_goal_position_h - 20 < dxl3_present_position < dxl3_goal_position_h + 20:
						break
				
				## stop rotating needle 
				direction_var = str(0)
				d.rotate_dc(direction_var, serialPort)
				
				# input('Ready? (y/n): ')
				
				## rotate needle: CCW
				direction_var = str(2)
				d.rotate_dc(direction_var, serialPort)
				
				## pull needle back
				dxl.write_goal_position(DXL3_ID, dxl3_init_position)			
				
				while 1:
					# Read present position
					dxl3_present_position = dxl.read_present_position(DXL3_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL3_ID, dxl3_init_position, dxl3_present_position))
					if dxl3_init_position - 20 < dxl3_present_position < dxl3_init_position + 20:
						break
				
				## stop rotating needle 
				direction_var = str(0)
				d.rotate_dc(direction_var, serialPort)
				
				
				# Implant Phase			
				## move needle to another side
				dxl.write_goal_position(DXL2_ID, dxl2_goal_position_i)
				while 1:
					# Read present position
					dxl2_present_position = dxl.read_present_position(DXL2_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL2_ID, dxl2_goal_position_i, dxl2_present_position))
					if dxl2_goal_position_i - 20 < dxl2_present_position < dxl2_goal_position_i + 20:
						break
				
				
				## inject needle 
				dxl.write_goal_position(DXL3_ID, dxl3_goal_position_i)
				
				while 1:
					# Read present position
					dxl3_present_position = dxl.read_present_position(DXL3_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL3_ID, dxl3_goal_position_i, dxl3_present_position))
					if dxl3_goal_position_i - 20 < dxl3_present_position < dxl3_goal_position_i + 20:
						break		
				
				## inject stick
				dxl.write_goal_position(DXL4_ID, dxl4_goal_position_i)
				
				while 1:
					# Read present position
					dxl4_present_position = dxl.read_present_position(DXL4_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL4_ID, dxl4_goal_position_i, dxl4_present_position))
					if dxl4_goal_position_i - 20 < dxl4_present_position < dxl4_goal_position_i + 20:
						break
								
				## pull needle back
				dxl.write_goal_position(DXL3_ID, dxl3_init_position)
				
				## pull stick back
				dxl.write_goal_position(DXL4_ID, dxl4_init_position)
				
				while 1:
					# Read present position
					dxl3_present_position = dxl.read_present_position(DXL3_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL3_ID, dxl3_init_position, dxl3_present_position))
					dxl4_present_position = dxl.read_present_position(DXL4_ID)
					# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL4_ID, dxl4_init_position, dxl4_present_position))
					if (dxl3_init_position - 20 < dxl3_present_position < dxl3_init_position + 20) and (dxl4_init_position - 20 < dxl4_present_position < dxl4_init_position + 20):
						break
				
				
				
				## set needle position for next transplant
				dxl.write_goal_position(DXL1_ID, dxl1_goal_position_h)
				dxl1_present_position = dxl.read_present_position(DXL1_ID)
				# print("dxl1 goal position: ",dxl1_goal_position_h)
				# print("dxl1 present position: ",dxl1_present_position)
				dxl.write_goal_position(DXL2_ID, dxl2_goal_position_h)
				dxl2_present_position = dxl.read_present_position(DXL2_ID)
				# print("dxl2 goal position: ",dxl2_goal_position_h)
				# print("dxl2 present position: ",dxl2_present_position)
				
				# input('Ready? (y/n): ')
				
		except:
			exctype, errorMsg = sys.exc_info()[:2]
			print ("Error reading port - %s" % errorMsg)
			stopped.set()
			break
	# serialPort.close()
	print("...Hair transplant process is finished...")
	

if(__name__=='__main__'):
	
	#serialPort = OpenSerialPort('/dev/ttyUSB0')
	serialPort = OpenSerialPort('COM16')
	if serialPort == None: sys.exit(1)
	
	queue = multiprocessing.Queue()
	stopped = threading.Event()
	p1 = threading.Thread(target=camera, args=(queue,))
	p2 = threading.Thread(target=control, args=(queue, serialPort,stopped,))

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
	
	