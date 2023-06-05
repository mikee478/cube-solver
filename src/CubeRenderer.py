from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import OpenGL.GL as gl
import math
from time import time

class CubeRenderer(QOpenGLWidget):

	# Move constants
	U = 0
	R = 1
	F = 2
	D = 3
	L = 4
	B = 5
	Ui = 6
	Ri = 7
	Fi = 8
	Di = 9
	Li = 10
	Bi = 11

	def __init__(self, stickers):
		super(CubeRenderer, self).__init__(parent=None)

		self.first = 0

		self.moveQueue = []
		self.stickers = stickers

		# Looks better when look from an angle
		self.xRot = 550
		self.yRot = 675
		self.zRot = 0

		self.firstPassMove = True
		self.orgTheta = []

		self.currentMove = -1 # Not executing a move
		self.thetaTotal = 0
		self.moveSpeed = 4

		self.cubeRot = []
		self.cubePos = []
		self.cubes = []
		for x in range(3):
			self.cubes.append([])
			self.cubePos.append([])
			self.cubeRot.append([])
			for y in range(3):
				self.cubes[x].append([0]*3)
				self.cubePos[x].append([0]*3)
				self.cubeRot[x].append([0]*3)

		self.cubeColors = self.initCubeColors(stickers)

		self.waitSecs = 1.0
		self.startTime = time()

		timer = QTimer(self) # set up a timer
		timer.timeout.connect(self.updatePosition) # timer callback function
		timer.start(1) # 1 ms cyclic timer

	# Parses stickers passed in from UI to set up the cube colors
	def initCubeColors(self, stickers):
		colors = []
		for x in range(3):
			colors.append([])
			for y in range(3):
				colors[x].append([])
				for z in range(3):
					colors[x][y].append([])
					for _ in range(6):
						colors[x][y][z].append((0,0,0)) # black, default color

		colors[0][2][0][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][0][0]);
		colors[1][2][0][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][0][1]);
		colors[2][2][0][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][0][2]);

		colors[0][2][1][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][1][0]);
		colors[1][2][1][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][1][1]);
		colors[2][2][1][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][1][2]);

		colors[0][2][2][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][2][0]);
		colors[1][2][2][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][2][1]);
		colors[2][2][2][CubeRenderer.U] = self.getColorTuple(stickers[CubeRenderer.U][2][2]);

		for y in range(2, -1, -1):
			for z in range(3):
				colors[2][y][z][CubeRenderer.R] = self.getColorTuple(stickers[CubeRenderer.R][z][2-y]);

		for y in range(2, -1, -1):
			for x in range(3):
				colors[x][2-y][2][CubeRenderer.F] = self.getColorTuple(stickers[CubeRenderer.F][y][x]);

		colors[2][0][0][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][0][0]);
		colors[1][0][0][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][0][1]);
		colors[0][0][0][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][0][2]);
		colors[2][0][1][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][1][0]);
		colors[1][0][1][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][1][1]);
		colors[0][0][1][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][1][2]);
		colors[2][0][2][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][2][0]);
		colors[1][0][2][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][2][1]);
		colors[0][0][2][CubeRenderer.D] = self.getColorTuple(stickers[CubeRenderer.D][2][2]);

		colors[0][0][0][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][0][0]);
		colors[0][1][0][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][0][1]);
		colors[0][2][0][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][0][2]);
		colors[0][0][1][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][1][0]);
		colors[0][1][1][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][1][1]);
		colors[0][2][1][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][1][2]);
		colors[0][0][2][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][2][0]);
		colors[0][1][2][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][2][1]);
		colors[0][2][2][CubeRenderer.L] = self.getColorTuple(stickers[CubeRenderer.L][2][2]);

		colors[0][0][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][0][0]);
		colors[1][0][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][0][1]);
		colors[2][0][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][0][2]);
		colors[0][1][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][1][0]);
		colors[1][1][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][1][1]);
		colors[2][1][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][1][2]);
		colors[0][2][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][2][0]);
		colors[1][2][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][2][1]);
		colors[2][2][0][CubeRenderer.B] = self.getColorTuple(stickers[CubeRenderer.B][2][2]);

		return colors

	# Gets the solved color of a face
	def getColorTuple(self, face):
		if(face == CubeRenderer.U):
			return (1.0, 1.0, 1.0) # white
		elif(face == CubeRenderer.R):
			return (0.698, 0.133, 0.133) # red
		elif(face == CubeRenderer.F):
			return (0, 1.0, 0) # green
		elif(face == CubeRenderer.D):
			return (1.0, 1.0, 0) # yellow
		elif(face == CubeRenderer.L):
			return (1.0, 0.404, 0) # orange
		elif(face == CubeRenderer.B):
			return (0, 0, 1.0) # blue
		else:
			return (0,0,0)

	# Set the rotation in the X axis
	def setXRotation(self, angle):
		if angle != self.xRot:
			self.xRot = angle
	
	# Set the rotation in the Y axis
	def setYRotation(self, angle):
		if angle != self.yRot:
			self.yRot = angle

	# Set the rotation in the Z axis
	def setZRotation(self, angle):
		if angle != self.zRot:
			self.zRot = angle

	# This function is called once before the first call to paintGL() or resizeGL(), 
	# and then once whenever the widget has been assigned a new QGLContext 
	def initializeGL(self):
		for x in range(-1, 2):
			for y in range(-1, 2):
				for z in range(-1, 2):
					self.cubePos[x+1][y+1][z+1] = (x*1.1, y*1.1, z*1.1)
					self.cubeRot[x+1][y+1][z+1] = (0.0, 0,0, 0,0, 0.0, 1.0, 0.0)
					self.cubes[x+1][y+1][z+1] = self.makeCube(x*1.1, y*1.1, z*1.1, 0.5, self.cubeColors[x+1][y+1][z+1])
		gl.glEnable(gl.GL_NORMALIZE)
		gl.glEnable(gl.GL_DEPTH_TEST);
		gl.glClearColor(190/255,220/255,245/255, 1.0)

	# This function is called whenever the widget needs to be painted.
	def paintGL(self):
		gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
		gl.glPushMatrix()
		gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
		gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
		gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
		for x in range(3):
			for y in range(3):
				for z in range(3):
					pos = self.cubePos[x][y][z]
					rot = self.cubeRot[x][y][z]
					self.drawCube(self.cubes[x][y][z], pos[0], pos[1], pos[2], rot[0], rot[1], rot[2])
					self.cubeRot[x][y][z] = (0, 0, 0, 0, 0, 0)
		gl.glPopMatrix()

	# This function is called whenever the widget has been resized.
	def resizeGL(self, width, height):
		side = min(width, height)
		if side >= 0:
			gl.glViewport((width - side) // 2, (height - side) // 2, side, side)
			gl.glMatrixMode(gl.GL_PROJECTION)
			gl.glLoadIdentity()
			gl.glFrustum(-1.0, +1.0, -1.0, 1.0, 5.0, 60.0)
			gl.glMatrixMode(gl.GL_MODELVIEW)
			gl.glLoadIdentity()
			gl.glTranslated(0.0, 0.0, -40.0)

	# Callback function for mouse pressed
	def mousePressEvent(self, event):
		self.lastPos = event.pos()

	# Callback function for mouse moved
	def mouseMoveEvent(self, event):
		dx = event.pos().x() - self.lastPos.x()
		dy = event.pos().y() - self.lastPos.y()
		self.lastPos = event.pos()
		if event.buttons() == Qt.MouseButton.LeftButton:
			self.setXRotation(self.xRot + 8 * dy)
			self.setYRotation(self.yRot + 8 * dx)

	# Get the rotation in the X axis
	def xRotation(self):
		return self.xRot

	# Get the rotation in the Y axis
	def yRotation(self):
		return self.yRot

	# Get the rotation in the Z axis
	def zRotation(self):
		return self.zRot
	
	# Creates a cube with given parameters
	def makeCube(self, x, y, z, size, colors):
		list = gl.glGenLists(1)
		gl.glNewList(list, gl.GL_COMPILE)

		# up face
		tup = colors[0];
		gl.glColor3f(tup[0], tup[1], tup[2])
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex3d(x+size, y+size, z-size)
		gl.glVertex3d(x+size, y+size, z+size)
		gl.glVertex3d(x-size, y+size, z-size)
		gl.glVertex3d(x-size, y+size, z+size)
		gl.glEnd()

		# right face
		tup = colors[1];
		gl.glColor3f(tup[0], tup[1], tup[2])
		gl.glBegin(gl.GL_QUADS)
		gl.glVertex3d(x+size, y-size, z-size)
		gl.glVertex3d(x+size, y-size, z+size)
		gl.glVertex3d(x+size, y+size, z+size)
		gl.glVertex3d(x+size, y+size, z-size)
		gl.glEnd()

		# front face
		tup = colors[2];
		gl.glColor3f(tup[0], tup[1], tup[2])		
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex3d(x-size, y-size, z+size)
		gl.glVertex3d(x-size, y+size, z+size)
		gl.glVertex3d(x+size, y-size, z+size)
		gl.glVertex3d(x+size, y+size, z+size)
		gl.glEnd()

		# down face
		tup = colors[3];
		gl.glColor3f(tup[0], tup[1], tup[2])
		gl.glBegin(gl.GL_QUADS)		
		gl.glVertex3d(x-size, y-size, z-size)
		gl.glVertex3d(x+size, y-size, z-size)
		gl.glVertex3d(x+size, y-size, z+size)
		gl.glVertex3d(x-size, y-size, z+size)
		gl.glEnd()

		# left face
		tup = colors[4];
		gl.glColor3f(tup[0], tup[1], tup[2])
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex3d(x-size, y+size, z-size)
		gl.glVertex3d(x-size, y+size, z+size)
		gl.glVertex3d(x-size, y-size, z-size)
		gl.glVertex3d(x-size, y-size, z+size)
		gl.glEnd()

		# back face
		gl.glColor3f(0.0,1.0,1.0)
		tup = colors[5];
		gl.glColor3f(tup[0], tup[1], tup[2])
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex3d(x-size, y-size, z-size)
		gl.glVertex3d(x-size, y+size, z-size)
		gl.glVertex3d(x+size, y-size, z-size)
		gl.glVertex3d(x+size, y+size, z-size)
		gl.glEnd()

		gl.glEndList()
		return list

	# Draws a cube
	def drawCube(self, cube, dx, dy, dz, angleX, angleY, angleZ):
		gl.glPushMatrix()
		gl.glRotated(angleX, 1, 0, 0)
		gl.glRotated(angleY, 0, 1, 0)
		gl.glRotated(angleZ, 0, 0, 1)
		
		if self.first < 3*3*3:
			self.first += 1
			gl.glTranslated(dx, dy, dz)

		gl.glCallList(cube)
		gl.glPopMatrix()

	# Forces an angle in the range [0,360)
	def normalizeAngle(self, angle):
		while (angle < 0):
			angle += 360
		while (angle > 360):
			angle -= 360
		return angle

	# Rotates a 2d point around another 2d by a given angle
	def rotate_point(self, cx, cy, angle, px, py):
		s = math.sin(angle);
		c = math.cos(angle);
		# translate point back to origin:
		px -= cx;
		py -= cy;
		# rotate point
		xnew = px * c - py * s;
		ynew = px * s + py * c;
		# translate point back:
		px = xnew + cx;
		py = ynew + cy;
		return (px, py);

	# Pops a move from the queue and start execution or continues execution of the current move
	def updatePosition(self):
		# currentMove = -2 : Making the new cube after the swaps
		# currentMove = -1 : Queueing up next move 
		# currentMove >= 0 : Executing a move

		# delay before starting solve
		if time() - self.startTime < self.waitSecs:
			self.update()
			return

		if self.currentMove == -2:
			self.cubeColors = self.initCubeColors(self.stickers)
			for x in range(-1, 2):
				for y in range(-1, 2):
					for z in range(-1, 2):
						self.cubePos[x+1][y+1][z+1] = (x*1.1, y*1.1, z*1.1)
						self.cubeRot[x+1][y+1][z+1] = (0.0, 0,0, 0,0, 0.0, 1.0, 0.0)
						self.cubes[x+1][y+1][z+1] = self.makeCube(x*1.1, y*1.1, z*1.1, 0.5, self.cubeColors[x+1][y+1][z+1])
			self.currentMove = -1
			self.thetaTotal = 0
			return

		# Not executing a move and there's more to process
		if self.currentMove == -1 and self.moveQueue != []:
			self.currentMove = self.moveQueue.pop(0)
			return

		# Continue executing
		if self.currentMove == CubeRenderer.U:
			self.moveU()
		elif self.currentMove == CubeRenderer.R:
			self.moveR()
		elif self.currentMove == CubeRenderer.F:
			self.moveF()
		elif self.currentMove == CubeRenderer.D:
			self.moveD()
		elif self.currentMove == CubeRenderer.L:
			self.moveL()
		elif self.currentMove == CubeRenderer.B:
			self.moveB()
		elif self.currentMove == CubeRenderer.Ui:
			self.moveUi()
		elif self.currentMove == CubeRenderer.Ri:
			self.moveRi()
		elif self.currentMove == CubeRenderer.Fi:
			self.moveFi()
		elif self.currentMove == CubeRenderer.Di:
			self.moveDi()
		elif self.currentMove == CubeRenderer.Li:
			self.moveLi()
		elif self.currentMove == CubeRenderer.Bi:
			self.moveBi()
		
		#Update the UI
		self.update()

	# Cycles the colors of 4 stickers
	def cycleStickers(self, ind1, ind2, ind3, ind4):
		temp = self.stickers[ind1[0]][ind1[1]][ind1[2]]
		self.stickers[ind1[0]][ind1[1]][ind1[2]] = self.stickers[ind2[0]][ind2[1]][ind2[2]]
		self.stickers[ind2[0]][ind2[1]][ind2[2]] = self.stickers[ind3[0]][ind3[1]][ind3[2]]
		self.stickers[ind3[0]][ind3[1]][ind3[2]] = self.stickers[ind4[0]][ind4[1]][ind4[2]]
		self.stickers[ind4[0]][ind4[1]][ind4[2]] = temp

	# Execute clockwise rotation of the up face
	def moveU(self):
		self.thetaTotal += self.moveSpeed

		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[x][2][z][0], self.cubeRot[x][2][z][1], self.cubeRot[x][2][z][2]))

		for x in range(3):
			for z in range(3):
				self.cubeRot[x][2][z] = (self.orgTheta[z+3*x][0], self.orgTheta[z+3*x][1] - self.thetaTotal, self.orgTheta[z+3*x][2], 0, -1.0, 0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			self.cycleStickers((CubeRenderer.U, 0, 0),(CubeRenderer.U, 2, 0),(CubeRenderer.U, 2, 2),(CubeRenderer.U, 0, 2)) #U corners
			self.cycleStickers((CubeRenderer.U, 1, 0),(CubeRenderer.U, 2, 1),(CubeRenderer.U, 1, 2),(CubeRenderer.U, 0, 1)) #U edges
			self.cycleStickers((CubeRenderer.F, 0, 1),(CubeRenderer.R, 1, 0),(CubeRenderer.B, 2, 1),(CubeRenderer.L, 1, 2)) #U Side Edges
			self.cycleStickers((CubeRenderer.F, 0, 0),(CubeRenderer.R, 2, 0),(CubeRenderer.B, 2, 2),(CubeRenderer.L, 0, 2)) #U Side Lcorners
			self.cycleStickers((CubeRenderer.F, 0, 2),(CubeRenderer.R, 0, 0),(CubeRenderer.B, 2, 0),(CubeRenderer.L, 2, 2)) #U Side Rcorners

	# Execute clockwise rotation of the right face
	def moveR(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for y in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[2][y][z][0], self.cubeRot[2][y][z][1], self.cubeRot[2][y][z][2]))

		for y in range(3):
			for z in range(3):
				self.cubeRot[2][y][z] = (self.orgTheta[z+3*y][0] - self.thetaTotal, self.orgTheta[z+3*y][1], self.orgTheta[z+3*y][2], -1.0, 0.0, 0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			self.cycleStickers((CubeRenderer.R, 0, 0),(CubeRenderer.R, 2, 0),(CubeRenderer.R, 2, 2),(CubeRenderer.R, 0, 2)) #R corners
			self.cycleStickers((CubeRenderer.R, 1, 0),(CubeRenderer.R, 2, 1),(CubeRenderer.R, 1, 2),(CubeRenderer.R, 0, 1)) #R edges
			self.cycleStickers((CubeRenderer.U, 1, 2),(CubeRenderer.F, 1, 2),(CubeRenderer.D, 1, 0),(CubeRenderer.B, 1, 2)) #R Side Edges
			self.cycleStickers((CubeRenderer.U, 0, 2),(CubeRenderer.F, 0, 2),(CubeRenderer.D, 2, 0),(CubeRenderer.B, 0, 2)) #R Side left corner
			self.cycleStickers((CubeRenderer.U, 2, 2),(CubeRenderer.F, 2, 2),(CubeRenderer.D, 0, 0),(CubeRenderer.B, 2, 2)) #R Side right corners

	#E xecute clockwise rotation of the front face
	def moveF(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for y in range(3):
					self.orgTheta.append((self.cubeRot[x][y][2][0], self.cubeRot[x][y][2][1], self.cubeRot[x][y][2][2]))

		for x in range(3):
			for y in range(3):
				self.cubeRot[x][y][2] = (self.orgTheta[y+3*x][0], self.orgTheta[y+3*x][1], self.orgTheta[y+3*x][2]-self.thetaTotal, 0.0, 0.0, 1.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			self.cycleStickers((CubeRenderer.F, 0, 0),(CubeRenderer.F, 2, 0),(CubeRenderer.F, 2, 2),(CubeRenderer.F, 0, 2)) #F corners
			self.cycleStickers((CubeRenderer.F, 1, 0),(CubeRenderer.F, 2, 1),(CubeRenderer.F, 1, 2),(CubeRenderer.F, 0, 1)) #F edges
			self.cycleStickers((CubeRenderer.U, 2, 1),(CubeRenderer.L, 2, 1),(CubeRenderer.D, 2, 1),(CubeRenderer.R, 2, 1)) #F Side Edges
			self.cycleStickers((CubeRenderer.U, 2, 0),(CubeRenderer.L, 2, 0),(CubeRenderer.D, 2, 0),(CubeRenderer.R, 2, 0)) #F Side CL
			self.cycleStickers((CubeRenderer.U, 2, 2),(CubeRenderer.L, 2, 2),(CubeRenderer.D, 2, 2),(CubeRenderer.R, 2, 2)) #F Side CR

	# Execute clockwise rotation of the down face
	def moveD(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[x][0][z][0], self.cubeRot[x][0][z][1], self.cubeRot[x][0][z][2]))

		for x in range(3):
			for z in range(3):
				self.cubeRot[x][0][z] = (self.orgTheta[z+3*x][0], self.orgTheta[z+3*x][1]+self.thetaTotal, self.orgTheta[z+3*x][2], 0.0, -1.0, 0.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			self.cycleStickers((CubeRenderer.D, 0, 0),(CubeRenderer.D, 2, 0),(CubeRenderer.D, 2, 2),(CubeRenderer.D, 0, 2)) #D corners
			self.cycleStickers((CubeRenderer.D, 1, 0),(CubeRenderer.D, 2, 1),(CubeRenderer.D, 1, 2),(CubeRenderer.D, 0, 1)) #D edges
			self.cycleStickers((CubeRenderer.R, 1, 2),(CubeRenderer.F, 2, 1),(CubeRenderer.L, 1, 0),(CubeRenderer.B, 0, 1)) #D Side Edges
			self.cycleStickers((CubeRenderer.R, 2, 2),(CubeRenderer.F, 2, 0),(CubeRenderer.L, 0, 0),(CubeRenderer.B, 0, 2)) #D Side Edges
			self.cycleStickers((CubeRenderer.R, 0, 2),(CubeRenderer.F, 2, 2),(CubeRenderer.L, 2, 0),(CubeRenderer.B, 0, 0)) #D Side CR

	# Execute clockwise rotation of the left face
	def moveL(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for y in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[0][y][z][0], self.cubeRot[0][y][z][1], self.cubeRot[0][y][z][2]))

		for y in range(3):
			for z in range(3):
				self.cubeRot[0][y][z] = (self.orgTheta[z+3*y][0]+self.thetaTotal, self.orgTheta[z+3*y][1], self.orgTheta[z+3*y][2], -1.0, 0.0, 0.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			self.cycleStickers((CubeRenderer.L, 0, 0),(CubeRenderer.L, 2, 0),(CubeRenderer.L, 2, 2),(CubeRenderer.L, 0, 2)) #L corners
			self.cycleStickers((CubeRenderer.L, 1, 0),(CubeRenderer.L, 2, 1),(CubeRenderer.L, 1, 2),(CubeRenderer.L, 0, 1)) #L edges
			for i in range(3): #quick fix
				self.cycleStickers((CubeRenderer.U, 1, 0),(CubeRenderer.F, 1, 0),(CubeRenderer.D, 1, 2),(CubeRenderer.B, 1, 0)) #L Side Edges
				self.cycleStickers((CubeRenderer.U, 0, 0),(CubeRenderer.F, 0, 0),(CubeRenderer.D, 2, 2),(CubeRenderer.B, 0, 0)) #L Side Edges
				self.cycleStickers((CubeRenderer.U, 2, 0),(CubeRenderer.F, 2, 0),(CubeRenderer.D, 0, 2),(CubeRenderer.B, 2, 0)) #L Side CR

	# Execute clockwise rotation of the back face
	def moveB(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False

			for x in range(3):
				for y in range(3):
					self.orgTheta.append((self.cubeRot[x][y][0][0], self.cubeRot[x][y][0][1], self.cubeRot[x][y][0][2]))

		for x in range(3):
			for y in range(3):
				self.cubeRot[x][y][0] = (self.orgTheta[y+3*x][0], self.orgTheta[y+3*x][1], self.orgTheta[y+3*x][2]+self.thetaTotal, 0.0, 0.0, -1.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			# #goes opposite of direction
			self.cycleStickers((CubeRenderer.B, 0, 0),(CubeRenderer.B, 2, 0),(CubeRenderer.B, 2, 2),(CubeRenderer.B, 0, 2)) #B corners
			self.cycleStickers((CubeRenderer.B, 1, 0),(CubeRenderer.B, 2, 1),(CubeRenderer.B, 1, 2),(CubeRenderer.B, 0, 1)) #B edges
			self.cycleStickers((CubeRenderer.L, 0, 1),(CubeRenderer.U, 0, 1),(CubeRenderer.R, 0, 1),(CubeRenderer.D, 0, 1)) #B Side Edges
			self.cycleStickers((CubeRenderer.L, 0, 0),(CubeRenderer.U, 0, 0),(CubeRenderer.R, 0, 0),(CubeRenderer.D, 0, 0)) #B Side Edges
			self.cycleStickers((CubeRenderer.L, 0, 2),(CubeRenderer.U, 0, 2),(CubeRenderer.R, 0, 2),(CubeRenderer.D, 0, 2)) #B Side Edges

	# Execute counter-clockwise rotation of the up face
	def moveUi(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[x][2][z][0], self.cubeRot[x][2][z][1], self.cubeRot[x][2][z][2]))

		for x in range(3):
			for z in range(3):
				self.cubeRot[x][2][z] = (self.orgTheta[z+3*x][0], self.orgTheta[z+3*x][1] + self.thetaTotal, self.orgTheta[z+3*x][2], 0, 1.0, 0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			for i in range(3):
				self.cycleStickers((CubeRenderer.U, 0, 0),(CubeRenderer.U, 2, 0),(CubeRenderer.U, 2, 2),(CubeRenderer.U, 0, 2)) #U corners
				self.cycleStickers((CubeRenderer.U, 1, 0),(CubeRenderer.U, 2, 1),(CubeRenderer.U, 1, 2),(CubeRenderer.U, 0, 1)) #U edges
				self.cycleStickers((CubeRenderer.F, 0, 1),(CubeRenderer.R, 1, 0),(CubeRenderer.B, 2, 1),(CubeRenderer.L, 1, 2)) #U Side Edges
				self.cycleStickers((CubeRenderer.F, 0, 0),(CubeRenderer.R, 2, 0),(CubeRenderer.B, 2, 2),(CubeRenderer.L, 0, 2)) #U Side Lcorners
				self.cycleStickers((CubeRenderer.F, 0, 2),(CubeRenderer.R, 0, 0),(CubeRenderer.B, 2, 0),(CubeRenderer.L, 2, 2)) #U Side Rcorners

	# Execute counter-clockwise rotation of the right face
	def moveRi(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for y in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[2][y][z][0], self.cubeRot[2][y][z][1], self.cubeRot[2][y][z][2]))

		for y in range(3):
			for z in range(3):
				self.cubeRot[2][y][z] = (self.orgTheta[z+3*y][0] + self.thetaTotal, self.orgTheta[z+3*y][1], self.orgTheta[z+3*y][2], 1.0, 0.0, 0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []
			
			#goes opposite of direction
			for i in range(3):
				self.cycleStickers((CubeRenderer.R, 0, 0),(CubeRenderer.R, 2, 0),(CubeRenderer.R, 2, 2),(CubeRenderer.R, 0, 2)) #R corners
				self.cycleStickers((CubeRenderer.R, 1, 0),(CubeRenderer.R, 2, 1),(CubeRenderer.R, 1, 2),(CubeRenderer.R, 0, 1)) #R edges
				self.cycleStickers((CubeRenderer.U, 1, 2),(CubeRenderer.F, 1, 2),(CubeRenderer.D, 1, 0),(CubeRenderer.B, 1, 2)) #R Side Edges
				self.cycleStickers((CubeRenderer.U, 0, 2),(CubeRenderer.F, 0, 2),(CubeRenderer.D, 2, 0),(CubeRenderer.B, 0, 2)) #R Side left corner
				self.cycleStickers((CubeRenderer.U, 2, 2),(CubeRenderer.F, 2, 2),(CubeRenderer.D, 0, 0),(CubeRenderer.B, 2, 2)) #R Side right corners

	# Execute counter-clockwise rotation of the front face
	def moveFi(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for y in range(3):
					self.orgTheta.append((self.cubeRot[x][y][2][0], self.cubeRot[x][y][2][1], self.cubeRot[x][y][2][2]))

		for x in range(3):
			for y in range(3):
				self.cubeRot[x][y][2] = (self.orgTheta[y+3*x][0], self.orgTheta[y+3*x][1], self.orgTheta[y+3*x][2]+self.thetaTotal, 0.0, 0.0, -1.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			for i in range(3):
				self.cycleStickers((CubeRenderer.F, 0, 0),(CubeRenderer.F, 2, 0),(CubeRenderer.F, 2, 2),(CubeRenderer.F, 0, 2)) #F corners
				self.cycleStickers((CubeRenderer.F, 1, 0),(CubeRenderer.F, 2, 1),(CubeRenderer.F, 1, 2),(CubeRenderer.F, 0, 1)) #F edges
				self.cycleStickers((CubeRenderer.U, 2, 1),(CubeRenderer.L, 2, 1),(CubeRenderer.D, 2, 1),(CubeRenderer.R, 2, 1)) #F Side Edges
				self.cycleStickers((CubeRenderer.U, 2, 0),(CubeRenderer.L, 2, 0),(CubeRenderer.D, 2, 0),(CubeRenderer.R, 2, 0)) #F Side CL
				self.cycleStickers((CubeRenderer.U, 2, 2),(CubeRenderer.L, 2, 2),(CubeRenderer.D, 2, 2),(CubeRenderer.R, 2, 2)) #F Side CR

	# Execute counter-clockwise rotation of the down face
	def moveDi(self):
		self.thetaTotal += self.moveSpeed

		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[x][0][z][0], self.cubeRot[x][0][z][1], self.cubeRot[x][0][z][2]))

		for x in range(3):
			for z in range(3):
				self.cubeRot[x][0][z] = (self.orgTheta[z+3*x][0], self.orgTheta[z+3*x][1]-self.thetaTotal, self.orgTheta[z+3*x][2], 0.0, 1.0, 0.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			for i in range(3):
				self.cycleStickers((CubeRenderer.D, 0, 0),(CubeRenderer.D, 2, 0),(CubeRenderer.D, 2, 2),(CubeRenderer.D, 0, 2)) #D corners
				self.cycleStickers((CubeRenderer.D, 1, 0),(CubeRenderer.D, 2, 1),(CubeRenderer.D, 1, 2),(CubeRenderer.D, 0, 1)) #D edges
				self.cycleStickers((CubeRenderer.R, 1, 2),(CubeRenderer.F, 2, 1),(CubeRenderer.L, 1, 0),(CubeRenderer.B, 0, 1)) #D Side Edges
				self.cycleStickers((CubeRenderer.R, 2, 2),(CubeRenderer.F, 2, 0),(CubeRenderer.L, 0, 0),(CubeRenderer.B, 0, 2)) #D Side Edges
				self.cycleStickers((CubeRenderer.R, 0, 2),(CubeRenderer.F, 2, 2),(CubeRenderer.L, 2, 0),(CubeRenderer.B, 0, 0)) #D Side CR

	# Execute counter-clockwise rotation of the left face
	def moveLi(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for y in range(3):
				for z in range(3):
					self.orgTheta.append((self.cubeRot[0][y][z][0], self.cubeRot[0][y][z][1], self.cubeRot[0][y][z][2]))

		for y in range(3):
			for z in range(3):
				self.cubeRot[0][y][z] = (self.orgTheta[z+3*y][0]-self.thetaTotal, self.orgTheta[z+3*y][1], self.orgTheta[z+3*y][2], 1.0, 0.0, 0.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			for m in range(3):
				self.cycleStickers((CubeRenderer.L, 0, 0),(CubeRenderer.L, 2, 0),(CubeRenderer.L, 2, 2),(CubeRenderer.L, 0, 2)) #L corners
				self.cycleStickers((CubeRenderer.L, 1, 0),(CubeRenderer.L, 2, 1),(CubeRenderer.L, 1, 2),(CubeRenderer.L, 0, 1)) #L edges
				for i in range(3): #quick fix
					self.cycleStickers((CubeRenderer.U, 1, 0),(CubeRenderer.F, 1, 0),(CubeRenderer.D, 1, 2),(CubeRenderer.B, 1, 0)) #L Side Edges
					self.cycleStickers((CubeRenderer.U, 0, 0),(CubeRenderer.F, 0, 0),(CubeRenderer.D, 2, 2),(CubeRenderer.B, 0, 0)) #L Side Edges
					self.cycleStickers((CubeRenderer.U, 2, 0),(CubeRenderer.F, 2, 0),(CubeRenderer.D, 0, 2),(CubeRenderer.B, 2, 0)) #L Side CR

	# Execute counter-clockwise rotation of the back face
	def moveBi(self):
		self.thetaTotal += self.moveSpeed
		
		if(self.firstPassMove):
			self.firstPassMove = False
			for x in range(3):
				for y in range(3):
					self.orgTheta.append((self.cubeRot[x][y][0][0], self.cubeRot[x][y][0][1], self.cubeRot[x][y][0][2]))

		for x in range(3):
			for y in range(3):
				self.cubeRot[x][y][0] = (self.orgTheta[y+3*x][0], self.orgTheta[y+3*x][1], self.orgTheta[y+3*x][2]-self.thetaTotal, 0.0, 0.0, 1.0)

		if(self.thetaTotal >= 90):
			self.currentMove = -2
			self.firstPassMove = True
			self.orgTheta = []

			#goes opposite of direction
			for i in range(3):
				self.cycleStickers((CubeRenderer.B, 0, 0),(CubeRenderer.B, 2, 0),(CubeRenderer.B, 2, 2),(CubeRenderer.B, 0, 2)) #B corners
				self.cycleStickers((CubeRenderer.B, 1, 0),(CubeRenderer.B, 2, 1),(CubeRenderer.B, 1, 2),(CubeRenderer.B, 0, 1)) #B edges
				self.cycleStickers((CubeRenderer.L, 0, 1),(CubeRenderer.U, 0, 1),(CubeRenderer.R, 0, 1),(CubeRenderer.D, 0, 1)) #B Side Edges
				self.cycleStickers((CubeRenderer.L, 0, 0),(CubeRenderer.U, 0, 0),(CubeRenderer.R, 0, 0),(CubeRenderer.D, 0, 0)) #B Side Edges
				self.cycleStickers((CubeRenderer.L, 0, 2),(CubeRenderer.U, 0, 2),(CubeRenderer.R, 0, 2),(CubeRenderer.D, 0, 2)) #B Side Edges