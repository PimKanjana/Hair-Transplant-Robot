import os
import time

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library

class Dinamixel():

	# Control table address is different in Dynamixel model
	ADDR_X_TORQUE_ENABLE      = 64               
	ADDR_X_GOAL_POSITION      = 116
	ADDR_X_PRESENT_POSITION   = 132
	ADDR_X_GOAL_PWM           = 100   # value 0-885
	ADDR_X_PRESENT_PWM        = 124
	
	# Protocol version
	PROTOCOL_VERSION          = 2.0

	# Default setting
	BAUDRATE                    = 57600         # Dynamixel default baudrate : 57600
	DEVICENAME                  = 'COM8'        # Check which port is being used on your controller ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

	TORQUE_ENABLE               = 1                 # Value for enabling the torque
	TORQUE_DISABLE              = 0                 # Value for disabling the torque
	#DXL_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
	#DXL_MAXIMUM_POSITION_VALUE  = 4000            # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
	DXL_MOVING_STATUS_THRESHOLD = 5                # Dynamixel moving status threshold
	
	# Initialize PortHandler instance
	# Set the port path
	# Get methods and members of PortHandlerLinux or PortHandlerWindows
	portHandler = PortHandler(DEVICENAME)

	# Initialize PacketHandler instance
	# Set the protocol version
	# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
	packetHandler = PacketHandler(PROTOCOL_VERSION)
	
	def __init__(self):
	
		# Open port
		if self.portHandler.openPort():
			print("Succeeded to open the port")
		else:
			print("Failed to open the port")
			print("Press any key to terminate...")
			getch()
			quit()
	
		# Set Port Baudrate
		if self.portHandler.setBaudRate(self.BAUDRATE):
			print("Succeeded to change the baudrate")
		else:
			print("Failed to change the baudrate")
			print("Press any key to terminate...")
			getch()
			quit()
	def twos_complement(self, input_value, num_bits):
		'''Calculates a two's complement integer from the given input value's bits'''
		if input_value > 2147483647:
			input_value = input_value-4294967295
		#self.mask = 2**(num_bits - 1)
		#self.mask = 2**32
		#value = -(input_value & self.mask) + (input_value & ~self.mask)
		#value = (input_value & ~self.mask)
		#print("value: ",(input_value))
		return input_value
		
	def torque_enable(self, dxl_id):   # Enable Dynamixel Torque
		self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_X_TORQUE_ENABLE, self.TORQUE_ENABLE)
		if self.dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
		elif self.dxl_error != 0:
			print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
		else:
			print("Dynamixel ID1 has been successfully connected")
	
	def torque_disable(self, dxl_id):    # Disable Dynamixel Torque
		self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_X_TORQUE_ENABLE, self.TORQUE_DISABLE)
		if self.dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
		elif self.dxl_error != 0:
			print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

	def close_port(self):  # Close port
		self.portHandler.closePort()
	
	def write_goal_position(self, dxl_id, dxl_goal_position):  # Write goal position
		self.dxl_comm_result, self.dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, self.ADDR_X_GOAL_POSITION, dxl_goal_position)
		if self.dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
		elif self.dxl_error != 0:
			print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
	
	def write_goal_pwm(self, dxl_id, dxl_goal_pwm):  # Write goal pwm
		self.dxl_comm_result, self.dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, dxl_id, self.ADDR_X_GOAL_PWM, dxl_goal_pwm)
		if self.dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
		elif self.dxl_error != 0:
			print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
	
	def read_present_position(self, dxl_id): 	# Read present position
		self.dxl_present_position,self.dxl_comm_result, self.dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id, self.ADDR_X_PRESENT_POSITION)
		self.dxl_present_position = self.twos_complement(self.dxl_present_position,4)
		#print("%d" %int.from_bytes(self.dxl_present_position, byteorder='big', signed=True))
		
		# print("%d" %self.dxl_present_position)
		if self.dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
		elif self.dxl_error != 0:
			print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

		return self.dxl_present_position
	
	def read_present_pwm(self, dxl_id): 	# Read present pwm
		self.dxl_present_pwm, self.dxl_comm_result, self.dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, dxl_id, self.ADDR_X_PRESENT_PWM)
		if self.dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
		elif self.dxl_error != 0:
			print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

		return self.dxl_present_pwm
		
if __name__ == "__main__":
	# Default setting
	#DXL1_ID                      = 1            # Dynamixel ID : 1
	DXL2_ID                      = 2            # Dynamixel ID : 2
	#DXL3_ID                      = 3            # Dynamixel ID : 3
	#DXL4_ID                      = 4           # Dynamixel ID : 4
	
	dxl = Dinamixel()
	#dxl.torque_enable(DXL1_ID)
	dxl.torque_enable(DXL2_ID)
	#dxl.torque_enable(DXL3_ID)
	
	dxl2_goal_pwm = int(300)
	dxl.write_goal_pwm(DXL2_ID, dxl2_goal_pwm)
	
	while 1:
		print("Press any key to continue! (or press ESC to quit!)")
		if getch() == chr(0x1b):
			break
		
		#Input Goal position
		# pos_x = input("Enter x coordinate: ")
		# pos_y = input("Enter y coordinate: ")
		# trans_needle = input("Enter Needle Moving Distance: ") 
		
		#dxl1_goal_position = int(pos_x)
		dxl2_goal_position = -300
		#dxl3_goal_position = int(trans_needle)

		#dxl.write_goal_position(DXL1_ID, dxl1_goal_position)
		dxl.write_goal_position(DXL2_ID, dxl2_goal_position)
		#dxl.write_goal_position(DXL3_ID, dxl3_goal_position)
	
		while 1:
			# Read present position
			dxl_present_position = dxl.read_present_position(DXL2_ID)			
			# x = (dxl_present_position).to_bytes(4, byteorder='big', signed=True)
			# print("byte val: ", x)
			print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL2_ID, dxl2_goal_position, dxl_present_position))
			#print(int.from_bytes(b'x', byteorder='big', signed=True))
			if not abs(dxl2_goal_position - dxl_present_position) > 20:
				break
	
	#dxl.torque_disable(DXL1_ID)
	dxl.torque_disable(DXL2_ID)
	#dxl.torque_disable(DXL3_ID)
	
	dxl.close_port()
	
	#int.from_bytes(b'\xfc\x00', byteorder='big', signed=True)
	
	
		