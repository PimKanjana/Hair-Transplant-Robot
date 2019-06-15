import module_inverse_kinematic as ik
import module_dxl as dm
import module_dc as dc

import time
import serial
import sys
import warnings
warnings.filterwarnings('ignore', 'The iteration is not making good progress')

class Control():

	def OpenSerialPort(self, port=""):
		print ("Open port %s" % port)

		self.fio2_ser = None

		try:
			self.fio2_ser = serial.Serial(port,
						baudrate=9600,
						bytesize=serial.EIGHTBITS,
						parity =serial.PARITY_ODD)

		except serial.SerialException as msg:
			print( "Error opening serial port %s" % msg)

		except:
			exctype, errorMsg = sys.exc_info()[:2]
			print ("%s  %s" % (errorMsg, exctype))

		return self.fio2_ser

	def setHome(self, serialPort):
		print ("Hair transplant process is starting!")
		serialPort.timeout = 1.0

		# Dinamixel setup
		self.DXL1_ID                      = 1            # Dynamixel ID : 1
		self.DXL2_ID                      = 2            # Dynamixel ID : 2
		self.DXL3_ID                      = 3            # Dynamixel ID : 3
		self.DXL4_ID                      = 4            # Dynamixel ID : 4
		
		self.dxl1_init_position = 2775   # initialize goal position
		self.dxl2_init_position = -400   # center = 2900
		self.dxl3_init_position = 1400
		self.dxl4_init_position = 3500
		
		self.dxl1_init_pwm = 300
		self.dxl2_init_pwm = 400
		self.dxl3_init_pwm = 885
		self.dxl4_init_pwm = 885

		self.dxl = dm.Dinamixel()
		self.dxl.torque_enable(self.DXL1_ID)
		self.dxl.torque_enable(self.DXL2_ID)
		self.dxl.torque_enable(self.DXL3_ID)
		self.dxl.torque_enable(self.DXL4_ID)

		self.dxl.write_goal_pwm(self.DXL1_ID, self.dxl1_init_pwm)
		self.dxl.write_goal_pwm(self.DXL2_ID, self.dxl2_init_pwm)
		self.dxl.write_goal_pwm(self.DXL3_ID, self.dxl3_init_pwm)
		self.dxl.write_goal_pwm(self.DXL4_ID, self.dxl4_init_pwm)
		
		self.dxl.write_goal_position(self.DXL1_ID, self.dxl1_init_position)
		self.dxl.write_goal_position(self.DXL2_ID, self.dxl2_init_position)
		self.dxl.write_goal_position(self.DXL3_ID, self.dxl3_init_position)
		self.dxl.write_goal_position(self.DXL4_ID, self.dxl4_init_position)


	def Motors_Control(self, serialPort, distance):
		
		# DC setup
		self.d = dc.Dc()
		
		# Dinamixel setup
		
		self.dxl = dm.Dinamixel()
		
		self.DXL1_ID                      = 1            # Dynamixel ID : 1
		self.DXL2_ID                      = 2            # Dynamixel ID : 2
		self.DXL3_ID                      = 3            # Dynamixel ID : 3
		self.DXL4_ID                      = 4            # Dynamixel ID : 4
		
		self.dxl1_init_position = 2775   # initialize goal position
		self.dxl2_init_position = -400   # center = 2900
		self.dxl3_init_position = 1400
		self.dxl4_init_position = 3500
		
		# Getting info for inverse kinematic 
		real_distance = distance
		width = real_distance[0]
		height = real_distance[1]
		print('w,h: ',width, height)
		
		# IK
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
		trans_needle = 2849  # trans_needle = 52*distance_mm
		trans_stick = 2000
		dxl2_center_position = 2900   # = 70*81
		
		# Goal Position for Harvest
		dxl1_goal_position_h = int(self.dxl1_init_position + pos_x)
		# dxl1_goal_position_h = int(pos_x)
		dxl2_goal_position_h = int(self.dxl2_init_position + pos_y)
		# dxl2_goal_position_h = int(pos_y)
		dxl3_goal_position_h = int(trans_needle)
	
		# Goal Position for Implant
		#dxl1_goal_position_i = int(self.dxl1_init_position + pos_x)
		dxl2_goal_position_i = int(dxl2_center_position + (dxl2_center_position - dxl2_goal_position_h))
		dxl3_goal_position_i = int(trans_needle)
		dxl4_goal_position_i = int(trans_stick)
		
		
		# Harvest Phase
		## set needle position
		self.dxl.write_goal_position(self.DXL1_ID, dxl1_goal_position_h)	
		self.dxl.write_goal_position(self.DXL2_ID, dxl2_goal_position_h)
		
		while 1:
			# Read present position
			dxl1_present_position = self.dxl.read_present_position(self.DXL1_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL1_ID, dxl1_goal_position_h, dxl1_present_position))
			dxl2_present_position = self.dxl.read_present_position(self.DXL2_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL2_ID, dxl2_goal_position_h, dxl2_present_position))
			if (dxl1_goal_position_h - 20 < dxl1_present_position < dxl1_goal_position_h + 20) and (dxl2_goal_position_h - 20 < dxl2_present_position < dxl2_goal_position_h + 20):
				break
									
		## rotate needle: CW
		direction_var = str(1)
		self.d.rotate_dc(direction_var, serialPort)
		
		## inject needle 
		self.dxl.write_goal_position(self.DXL3_ID, dxl3_goal_position_h)
		
		while 1:
			# Read present position
			dxl3_present_position = self.dxl.read_present_position(self.DXL3_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL3_ID, dxl3_goal_position_h, dxl3_present_position))
			if dxl3_goal_position_h - 20 < dxl3_present_position < dxl3_goal_position_h + 20:
				break
		
		## stop rotating needle 
		direction_var = str(0)
		self.d.rotate_dc(direction_var, serialPort)
		
		# input('Ready? (y/n): ')
		
		## rotate needle: CCW
		direction_var = str(2)
		self.d.rotate_dc(direction_var, serialPort)
		
		## pull needle back
		self.dxl.write_goal_position(self.DXL3_ID, self.dxl3_init_position)			
		
		while 1:
			# Read present position
			dxl3_present_position = self.dxl.read_present_position(self.DXL3_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL3_ID, dxl3_init_position, dxl3_present_position))
			if self.dxl3_init_position - 20 < dxl3_present_position < self.dxl3_init_position + 20:
				break
		
		## stop rotating needle 
		direction_var = str(0)
		self.d.rotate_dc(direction_var, serialPort)
		
		
		# Implant Phase			
		## move needle to another side
		self.dxl.write_goal_position(self.DXL2_ID, dxl2_goal_position_i)
		while 1:
			# Read present position
			dxl2_present_position = self.dxl.read_present_position(self.DXL2_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL2_ID, dxl2_goal_position_i, dxl2_present_position))
			if dxl2_goal_position_i - 20 < dxl2_present_position < dxl2_goal_position_i + 20:
				break
		
		
		## inject needle 
		self.dxl.write_goal_position(self.DXL3_ID, dxl3_goal_position_i)
		
		while 1:
			# Read present position
			dxl3_present_position = self.dxl.read_present_position(self.DXL3_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL3_ID, dxl3_goal_position_i, dxl3_present_position))
			if dxl3_goal_position_i - 20 < dxl3_present_position < dxl3_goal_position_i + 20:
				break		
		
		## inject stick
		self.dxl.write_goal_position(self.DXL4_ID, dxl4_goal_position_i)
		
		while 1:
			# Read present position
			dxl4_present_position = self.dxl.read_present_position(self.DXL4_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL4_ID, dxl4_goal_position_i, dxl4_present_position))
			if dxl4_goal_position_i - 20 < dxl4_present_position < dxl4_goal_position_i + 20:
				break
						
		## pull needle back
		self.dxl.write_goal_position(self.DXL3_ID, self.dxl3_init_position)
		
		## pull stick back
		self.dxl.write_goal_position(self.DXL4_ID, self.dxl4_init_position)
		
		while 1:
			# Read present position
			dxl3_present_position = self.dxl.read_present_position(self.DXL3_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL3_ID, dxl3_init_position, dxl3_present_position))
			dxl4_present_position = self.dxl.read_present_position(self.DXL4_ID)
			# print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL4_ID, dxl4_init_position, dxl4_present_position))
			if (self.dxl3_init_position - 20 < dxl3_present_position < self.dxl3_init_position + 20) and (self.dxl4_init_position - 20 < dxl4_present_position < self.dxl4_init_position + 20):
				break
		
		
		
		## set needle position for next transplant
		self.dxl.write_goal_position(self.DXL1_ID, dxl1_goal_position_h)
		dxl1_present_position = self.dxl.read_present_position(self.DXL1_ID)
		# print("dxl1 goal position: ",dxl1_goal_position_h)
		# print("dxl1 present position: ",dxl1_present_position)
		self.dxl.write_goal_position(self.DXL2_ID, dxl2_goal_position_h)
		dxl2_present_position = self.dxl.read_present_position(self.DXL2_ID)
		# print("dxl2 goal position: ",dxl2_goal_position_h)
		# print("dxl2 present position: ",dxl2_present_position)
		
		# input('Ready? (y/n): ')

		

if(__name__=='__main__'):
	
	ct = Control()
	
	serialPort = ct.OpenSerialPort('COM15')
	if serialPort == None: sys.exit(1)
	
	ct.setHome(serialPort)
	
	# distance = ([x_distance, y_distance])
	distance = ([1, 1])
	
	ct.Motors_Control(serialPort, distance)
	
		

	