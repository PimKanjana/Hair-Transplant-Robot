import math 

class InverseKinematic():
	def __init__(self, width, height):
		# input parameter
		# self.q = float(input('Enter camera distance(q): '))
		# self.r = float(input('Enter phantom radius(r): '))
		# self.theta = float(input('Enter angle between camera and needle(degree): '))
		self.q = float(85)
		self.r = float(70)
		self.theta = float(60)
		# self.h = float(input('Enter y-output from camera(h): '))
		# self.w = float(input('Enter x-output from camera(w): '))
		self.h = float(height)
		self.w = float(width)
		self.theta_rad = math.radians(self.theta)

	## finding angle for motor1 (Phi)
	def finding_Phi(self):
		# finding point A(y,z) and B(y,z)
		Ay = -self.q*math.sin(self.theta_rad)
		Az = self.r + self.q*math.cos(self.theta_rad)
		l = math.sqrt(math.pow(self.q,2) + math.pow(self.h,2))
		alpha_rad = math.atan2(self.h,self.q)
		alpha = math.degrees(alpha_rad)
		By = Ay + l*math.sin(alpha_rad + self.theta_rad)
		Bz = Az - l*math.cos(alpha_rad + self.theta_rad)

		# finding point C(y,z)
		m1 = (Az-Bz)/(Ay-By)
		a1 = m1                   # linear equation: z = a1*y + b1
		b1 = Az - m1*Ay     
		p1 = 1 + math.pow(a1,2)             # quadratic equation: p1*y^2 + n1*y + k1 = 0
		n1 = 2*a1*b1
		k1 = math.pow(b1,2) - math.pow(self.r,2)  

		Cy = (-n1 - math.sqrt(math.pow(n1,2) - 4*p1*k1))/(2*p1)    # choose Cy-maximum value
		Cz = a1*Cy + b1

		# point D(y,z)
		Dy = 0
		Dz = self.r
		DC = math.sqrt(math.pow(Dy-Cy,2) + math.pow(Dz-Cz,2))

		# finding angle for motor1 (phi)
		self.Phi = 2*math.degrees(math.asin((DC/2)/self.r))
		return self.Phi

	## finding angle for motor2 (Psi)
	def finding_Psi(self):
		# finding point E(x,z) and F(x,z)
		Ex = 0
		Ez = self.r + self.q*math.cos(self.theta_rad)
		#Ez = self.r + self.q
		Fx = self.w
		Fz = self.r

		# finding point G(x,z)
		m2 = (Ez-Fz)/(Ex-Fx)
		a2 = m2               # linear equation: z = a2*x + b2 
		b2 = Ez - m2*Ex   
		p2 = 1 + math.pow(a2,2)
		n2 = 2*a2*b2  
		k2 = math.pow(b2,2) - math.pow(self.r,2)       # quadratic equation: p1*x^2 + n1*x + k1 = 0

		Gx = (-n2 - math.sqrt(math.pow(n2,2) - 4*p2*k2))/(2*p2) # choose Gx-maximum value
		Gz = a2*Gx + b2

		# point H(x,z)
		Hx = 0
		Hz = self.r
		HG = math.sqrt(math.pow(Hx-Gx,2) + math.pow(Hz-Gz,2))

		# finding angle for motor2 (Psi)
		self.Psi = 2*math.degrees(math.asin((HG/2)/self.r))
		return self.Psi
	
if __name__ == "__main__":
	width = -6.597445536627514 - (-6.622074754228398)
	height = 3.5021442989545313 - 3.1442081356150466
	invki = InverseKinematic(width, height)
	angle_1 = invki.finding_Phi()
	angle_2 = invki.finding_Psi()
	print("Phi: ",angle_1)
	print("Psi: ",angle_2)
	
	