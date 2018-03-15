#!/usr/bin/env python3
import pygame,math

class Board:
	# player ids
	P_NIL = 0 # noone
	P_ONE = 1 # 
	P_TWO = 2
	DIMEN = 8 # 8x8
	class Cell:
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
			if self.owner == Board.P_ONE:
				pygame.draw.circle(screen, [0,0,0], self.midpoint,self.radius,0)
			elif self.owner == Board.P_TWO:
				pygame.draw.circle(screen, [255,255,255], self.midpoint,self.radius,0)


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
				self.grid[x].append(self.Cell((x,y), screen_pos, cell_size, self.P_NIL) )
		center = (self.DIMEN-1)/2
		# set initial pieces
		self.grid[math.floor(center)][math.floor(center+1)].owner = self.P_ONE
		self.grid[math.floor(center+1)][math.floor(center)].owner = self.P_ONE
		# set initial pieces
		self.grid[math.floor(center)][math.floor(center)].owner = self.P_TWO
		self.grid[math.floor(center+1)][math.floor(center+1)].owner = self.P_TWO
		

	def get_intersecting_cell(self, pos):
		for row in self.grid:
			for cell in row:
				if cell.does_intersect(pos):
					return cell
		return None

	def draw(self, screen):
		for row in self.grid:
			for cell in row:
				cell.draw(screen)
		


def main():
	size = [550, 650]
	board = Board((0, size[1]/12), (size[0], size[0]*0.95))
	cur_player = Board.P_ONE
	cur_piece = None 

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
				if cur_piece == None:
					cur_piece = board.get_intersecting_cell(mouse_pos)
					print(cur_piece)
					if cur_piece.owner != cur_player:
						cur_piece = None # cannot pick up empty or other player piece
				else:
					#try to place piece at cell or if clicked again unselect
					other_piece = board.get_intersecting_cell(mouse_pos)
					if other_piece is cur_piece:
						cur_piece = None

		screen.fill([0,0,0])
		board.draw(screen)
		# highlight current piece, and any potential moves
		if cur_piece:
			# highlight the piece
			cur_piece.draw_highlight(screen, True)
		pygame.display.flip()



if __name__ == '__main__':
	main()