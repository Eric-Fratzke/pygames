#!/usr/bin/env python3
import pygame,math

class Board:
	'''
	Board - Represents the Othello/Reversi board as a 2D grid of cells.
			Each cell is owned by either player one, two, or neither(nil). 
	'''

	# Statics for the board
	P0 = 0 # niether player
	P1 = 1 # player one
	P2 = 2 # player two
	DIMEN = 8 # dimension of the grid 8x8
	P1_COLOR = [0,0,0]
	P2_COLOR = [255,255,255]
	class Cell:
		'''
		Board - Basic components of the board
				Each cell has an owner that is either one of the players or none. 
				Each cell also contains its indices on the grid [0-DIMEN][0-DIMEN] and its
				position in screen space (x,y).
		'''
		# Statics for the cells
		FRAMES = 5 # number animation frames 
		def __init__(self, grid_pos, screen_pos, size, owner):
			i,j = grid_pos[0],grid_pos[1]
			x,y = screen_pos[0],screen_pos[1]
			
			self.grid_pos = grid_pos # indices on grid
			self.screen_pos = screen_pos # coordinates of rect
			self.size = size  # size of cell
			self.owner = owner # player one, two or nil
			self.midpoint = int((x*2+size[0])/2), int((y*2+size[1])/2) # get middle of rect diagonal
			self.radius = int((size[0]+size[1])/5) # create radius slightly smaller than avg of width and height
			self.rect = [self.screen_pos[0],self.screen_pos[1],self.size[0],self.size[1]]
			self.frame = 0
			if (i%2) == 0 and (j%2) != 0:
					self.cell_color = [25,125,0]
			elif (j%2) == 0 and (i%2) != 0:
					self.cell_color = [25,125,0]
			else:
				self.cell_color = [105,25,0]

		def __repr__(self):
			return "(" + str( self.grid_pos[0]) + ", " + str(self.grid_pos[1]) + ")"

		def draw(self, screen):
			pygame.draw.rect(screen, self.cell_color, self.rect, 0)
			# draw the piece if any
			if self.owner != Board.P0:
				color = None
				if self.frame == 0: # not currently animated
					if self.owner == Board.P1:
						color = Board.P1_COLOR
					elif self.owner == Board.P2:
						color = Board.P2_COLOR
					pygame.draw.circle(screen, color, self.midpoint,self.radius,0)
				else: #animate
					# to simulate the piece being flipped draw an ellipse whose width decrease then increases
					# on the increase change the color to the new owner 
					# flips along
					rot = math.sin(self.frame)
					if rot < 0:
						rot *= -1
						# flip color to current owner
						if self.owner == Board.P1:
							color = Board.P1_COLOR
						elif self.owner == Board.P2:
							color = Board.P2_COLOR
					else:
						# still flipping, draw with previous owner color
						if self.owner == Board.P1:
							color = Board.P2_COLOR
						elif self.owner == Board.P2:
							color = Board.P1_COLOR
					# draw animated rotating disk effect with ellipse
					w,h = self.radius*2/self.frame*rot, self.radius*2
					x,y = self.midpoint[0]-self.radius/self.frame*rot, self.midpoint[1]-self.radius
					pygame.draw.ellipse(screen, color, [x,y,w,h],0)
					self.frame += 1
					self.frame %= self.FRAMES


		def flip(self):
			self.frame = 1
			# flip owner
			if self.owner == Board.P1:
				self.owner = Board.P2
			elif self.owner == Board.P2:
				self.owner = Board.P1

		def draw_highlight(self,screen, piece=False):
			if piece:
				pygame.draw.circle(screen, [155,12,0], self.midpoint,self.radius,3)
			else:
				pygame.draw.rect(screen, [155,12,0], self.rect, 3)


		def does_intersect(self, pos):
			return (pos[0] > self.rect[0] and pos[0] < self.rect[0]+self.rect[2]) \
				and (pos[1] > self.rect[1] and pos[1] < self.rect[1]+self.rect[3])
			

	def __init__(self, offset, size):
		self.offset = offset
		self.size = size 
		cell_size = math.floor(size[0]/self.DIMEN), math.floor(size[1]/self.DIMEN)
		self.grid = []
		self.setup_board(offset, cell_size)
	
	def setup_board(self, offset, cell_size):
		# clear if not empty
		if len(self.grid) > 0:	
			for row in self.grid:
				row[:] = []
			self.grid[:] = []
		# populate elements
		for x in range(0, self.DIMEN):
			self.grid.append([])
			for y in range(0, self.DIMEN):
				screen_pos = (offset[0]+x*cell_size[0], offset[1]+y*cell_size[1])
				self.grid[x].append(self.Cell((x,y), screen_pos, cell_size, self.P0) )
		center = (self.DIMEN-1)/2
		# set initial pieces
		self.grid[math.floor(center)][math.floor(center+1)].owner = self.P1
		self.grid[math.floor(center+1)][math.floor(center)].owner = self.P1
		self.grid[math.floor(center)][math.floor(center)].owner = self.P2
		self.grid[math.floor(center+1)][math.floor(center+1)].owner = self.P2
		

	def get_intersecting_cell(self, pos):
		for row in self.grid:
			for cell in row:
				if cell.does_intersect(pos):
					return cell
		return None

	# def get_moves(self, screen):
	# 	for row in self.grid:
	# 		for cell in row:
	# 			cell.draw(screen)
		
	def draw(self, screen):
		for row in self.grid:
			for cell in row:
				cell.draw(screen)


def main():
	size = [550, 650]
	board = Board((0, size[1]/12), (size[0], size[0]*0.95))
	cur_player = Board.P1
	selected_cell = None 

	pygame.init()
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Quoridor")
	exit = False
	clock = pygame.time.Clock()


	# main while loop
	while not exit:
		clock.tick(10)
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT:
				exit=True 
			elif event.type == pygame.KEYDOWN:
				break
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				#pick up piece an high light moves
				if selected_cell == None:
					cell = board.get_intersecting_cell(mouse_pos)
					# select piece if it is owned by player
					if cell.owner == cur_player:
						selected_cell = cell 
						# test flip animation
						# selected_cell.flip()
						# selected_cell = None #
				else:
					#try to place piece at cell or if clicked again unselect
					cell = board.get_intersecting_cell(mouse_pos)
					if cell is selected_cell:
						selected_cell = None

		screen.fill([0,0,0])
		board.draw(screen)
		# if cell is celected highlight current piece, and any potential moves
		if selected_cell:
			# highlight the piece
			selected_cell.draw_highlight(screen, True)
		pygame.display.flip()



if __name__ == '__main__':
	main()