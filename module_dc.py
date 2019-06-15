import serial
import time
import sys

class Dc():
	
	
	def rotate_dc(self, var, ser):
		
		try:
			if(var == '1'):
				ser.write('1'.encode())
				print("clockwise direction")
				
			elif(var == '0'):
				ser.write('0'.encode())
				print("halting")
				
			elif(var == '2'):
				ser.write('2'.encode())
				print("counterclockwise direction")
			else:
				print("Please input only the number '0','1',or '2'")
		
		except KeyboardInterrupt:
			raise
			sys.exit(0)		

if __name__ == "__main__":
	# serial port connection
	ser = serial.Serial('COM16',9600)
	#ser = serial.Serial(port='COM9', baudrate=9600, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
	
	dc = Dc()
	
	while 1:
		var = input()
		dc.rotate_dc(var,ser)
		#print('in loop')
		
	ser.close()
	print ("Done")

			