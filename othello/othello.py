#!/usr/bin/env python3
import datetime
import pygame,math,random


class Board:
	'''
	Board - Represents the Othello/Reversi board as a 2D grid of cells.
			Each cell is owned by either player one, two, or neither(nil). 
	'''
	# Statics for the board
	P0 = -1 # niether player
	P1 = 0 # player one
	P2 = 1 # player two
	DIMEN = 8 # dimension of the grid 8x8
	P1_COLOR = [0,0,0]
	P2_COLOR = [255,255,255]

	ORANGE_COLOR = [105,25,0]
	GREEN_COLOR = [25,125,0]
	
	# Move and states
	TIE = 2 		# TIE
	NO_MOVES = 3	
	GAME_OVER = 4
	WAIT_TIME = 5 # 5 seconds

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
					self.cell_color = Board.ORANGE_COLOR
			elif (j%2) == 0 and (i%2) != 0:
					self.cell_color = Board.ORANGE_COLOR
			else:
				self.cell_color = Board.GREEN_COLOR

		def __repr__(self):
			return "(" + str( self.grid_pos[0]) + ", " + str(self.grid_pos[1]) + ")"

		def __eq__(self, other):
			if other:
				return self.grid_pos == other.grid_pos		
			return False

		def __hash__(self):
			return hash(self.grid_pos )

		def copy(self):
			'''
				return deepcopy of cell
			'''
			return Board.Cell(self.grid_pos, self.screen_pos, self.size, self.owner)

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
			self.owner = Board.toggle_player(self.owner)


		def draw_highlight(self,screen, piece=False):
			if piece:
				pygame.draw.circle(screen, [255,12,0], self.midpoint,self.radius+2,3)
			else:
				pygame.draw.rect(screen, [250,250,0], self.rect, 3)


		def does_intersect(self, pos):
			return (pos[0] > self.rect[0] and pos[0] < self.rect[0]+self.rect[2]) \
				and (pos[1] > self.rect[1] and pos[1] < self.rect[1]+self.rect[3])
			

	def __init__(self, offset, size):
		self.font = pygame.font.SysFont(None, 48)
		self.offset = offset
		self.size = size 
		cell_size = size[0]//self.DIMEN, size[1]//self.DIMEN
		self.grid = []
		self.setup_board(offset, cell_size)
		self.winner = self.P0
		self.wait = 0 #animation waittime, after eah move made wait for animation

	def copy(self):
		'''
			return deepcopy of board
		'''
		copy = Board(self.offset, self.size)
		for i in range(0,self.DIMEN):
			for j in range(0,self.DIMEN):
				copy.grid[i][j] = self.grid[i][j].copy()
		return copy

	def is_waiting(self):
		#waiting to help tell if board is waiting for animations to finish
		return self.wait > 0


	@staticmethod
	def toggle_player(owner):
		return (owner+1)%2


	def setup_board(self, offset, cell_size):
		self.pieces = {}
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
		center = (self.DIMEN-1)//2
		# set initial pieces
		a = self.grid[center][center+1]
		b = self.grid[center+1][center]
		c = self.grid[center][center]
		d = self.grid[center+1][center+1]
		self.pieces[self.P1] = {a:1, b:1}
		self.pieces[self.P2] = {c:1, d:1}
		a.owner = b.owner = self.P1
		c.owner = d.owner = self.P2

	def get_winner(self):
		return self.winner

	def get_score(self, player):
		return len(self.pieces[player].keys())

	def check_game_over(self):
		'''
			Returns winner if game is over, if game is not over returns P0
		'''
		winner = self.P0
		# p1_cell_count =  len( self.get_owned_cells(self.P1)) 
		# p2_cell_count = len( self.get_owned_cells(self.P2))
		has_empty = False
		i = 0
		# try to find any empty cell
		while not has_empty and i < self.DIMEN:
			j =0
			while not has_empty and j < self.DIMEN:
				if self.grid[i][j].owner == self.P0:
					has_empty = True
				j+=1
			i+=1

		# if player has no cells then they lose!
		# if p1_cell_count <= 0 :
		# 	winner = self.P2
		# elif p2_cell_count <= 0 :
		# 	winner = self.P1
		p1_score = self.get_score(self.P1)
		p2_score = self.get_score(self.P2)
		if p1_score <= 0 :
			winner = self.P2
		elif p2_score <= 0 :
			winner = self.P1
		# if the board has no empty, pick winner by number of owned cells
		elif not has_empty:
			print("FULL BOARD!")
			# if p1_cell_count > p2_cell_count:
			# 	winner = self.P1  
			# elif p1_cell_count < p2_cell_count:
			# 	winner = self.P2
			if p1_score > p2_score:
				winner = self.P1  
			elif p1_score < p2_score:
				winner = self.P2
			else:
				winner = self.TIE
		# if both players have no moves then TIE
		else: 
			p1_moves =  self.get_all_moves(self.P1)
			p2_moves = self.get_all_moves(self.P2)
			if p1_moves == False and p2_moves == False:
				winner = self.TIE  

		self.winner = winner
		return self.winner != self.P0
		
	def get_all_moves(self, player):
		'''return false if player has no moves else returns list of all moves (cell_from, cell_to)'''
		moves = False
		move = Board.NO_MOVES 
		# for each cell try to find a move to pick
		for cell_from in self.get_owned_cells(player):
			for  cell_to in self.get_moves(cell_from):
				if not moves:
					moves = []
				moves.append((cell_from, cell_to))
		return moves

	def draw(self, screen):
		self.wait-= 1
		if self.wait < 0:
			self.wait = 0
		for row in self.grid:
			for cell in row:
				cell.draw(screen)
		score_text = self.font.render('Black %d  White %d' % \
					(self.get_score(self.P1), self.get_score(self.P2)), True, (255, 255, 255))
		score_text_rect =	(self.offset[0]+self.size[0]//2-score_text.get_width()//2,\
							self.offset[1]+self.size[1]+score_text.get_height()) 
		screen.blit(score_text,score_text_rect)

	def get_intersecting_cell(self, pos):
		for row in self.grid:
			for cell in row:
				if cell.does_intersect(pos):
					return cell
		return None

	# def get_owned_cells(self, owner):
	# 	cells = []
	# 	for row in self.grid:
	# 		for cell in row:
	# 			if cell.owner == owner:
	# 				cells.append(cell)
	# 	return cells
	def get_owned_cells(self, player):
		return list(self.pieces[player].keys())		

	def get_moves(self, cell):
		'''
			get_moves
			 	find all lines from the current cell to the nearest empty cell such that all cells in between do not 
				have the same owner as the moving cell
				Do this by searching immediate neighbors then following the lines from neighbor to empty while
				owner is the opponent
	 		cell : current cell
	 		Returns a list of cells that are potential moves
		'''
		moves = []
		if cell.owner == self.P0:
			return moves # empty cell!
		i,j = cell.grid_pos
		# get each index of the neighbor and check if the move is valid
		neighbor = None
		for di in range(-1,2):
			for dj in range(-1,2):
				ni, nj = i+di, j+dj
				if (ni, nj) != (i,j):
					# check the neighbor, if it is opponent try to find move
					if ni >= 0 and ni < self.DIMEN and nj >= 0 and nj < self.DIMEN:
						neighbor = self.grid[ni][nj]
						if neighbor.owner != self.P0 and neighbor.owner != cell.owner:  
							# get the next cell in the same direction as neighbor 
							search = True
							while search:
								ni, nj = ni+di, nj+dj
								# if next cell is not beyond board
								if ni < 0 or ni >= self.DIMEN or nj < 0 or nj >= self.DIMEN:
									search = False # reached end of board 
								else:
									next_cell = self.grid[ni][nj]
									if next_cell.owner == self.P0: # found empty cell! add this cell to moves
										moves.append(next_cell)
										search = False
									elif next_cell.owner == cell.owner: # not opponent, cannot jump
										search = False
									#else keep searching
		return moves

	def is_move(self, move):
		valid = False
		cell_from, cell_to = move
		if cell_to.owner == self.P0:
			i,j = cell_from.grid_pos
			di, dj = self.get_move_delta(move)
			ni, nj = i+di, j+dj
			if (ni, nj) != (i,j):
				valid = True
				next_cell = None
				while valid and \
						ni >= 0 and ni < self.DIMEN and nj >= 0 and nj < self.DIMEN:
					next_cell = self.grid[ni][nj]
					# if cell is owned by opponent 
					if next_cell.owner == cell_from.owner or next_cell.owner == self.P0: 
						valid  = False
					ni, nj = ni+di, nj+dj
				# empty cell broke loop
				if next_cell.owner == self.P0:
					valid = True
				else:
					valid = False
		return valid

	def move_piece(self, move):
		self.wait = self.WAIT_TIME
		# flips all cells in between the line segment created by  to and from 
		# try for each cell from owned cells		
		cell_from, cell_to = move
		i, j =  cell_from.grid_pos
		di, dj = self.get_move_delta(move)
		ni, nj = i+di, j+dj
		next_cell = None
		continue_flipping = True
		while continue_flipping  and \
				ni >= 0 and ni < self.DIMEN and nj >= 0 and nj < self.DIMEN:
			next_cell = self.grid[ni][nj]
			# if cell is owned by opponent 
			if next_cell.owner != cell_from.owner and next_cell.owner != self.P0: 
				# add piece to new owner remove from old
				self.pieces[cell_from.owner][next_cell] = 1
				del self.pieces[next_cell.owner][next_cell]
				next_cell.flip() # flip owner and start animation
			else:
				continue_flipping  = False
			ni, nj = ni+di, nj+dj
		cell_to.owner = cell_from.owner
		self.pieces[cell_from.owner][cell_to] = 1


	def move(self, player, cell_to):
		'''
		for each player move from any owned cell to destination cell
		'''
		moves = self.get_all_moves(player)
		for move in moves:
			if move[1] == cell_to:
				self.move_piece(move)


	def get_move_delta(self, move):
		cell_from, cell_to = move
		i, j =  cell_from.grid_pos
		fi, fj =  cell_to.grid_pos
		di, dj = (fi-i), (fj-j)
		# clamp directions to ints between [-1,1]
		if di > 1:
			di = 1
		elif di < 0:
			di = -1
		if dj > 1:
			dj = 1
		if dj < 0:
			dj = -1
		return (di, dj)


class AI:
	def __init__(self, player, board):
		self.player = player
		# reference to the board
		self.board = board
		random.seed(datetime.datetime.now())

	def get_move(self):
		'''
			returns board state or potential move (cell_from, cell_to)
		'''
		move = Board.GAME_OVER
		if not self.board.check_game_over():
			move = Board.NO_MOVES # does not own any cells!
			get_all_moves = self.board.get_all_moves(self.player)
			#shuffle the cells
			if get_all_moves:
				moves = []
				while len(get_all_moves) > 0:
					moves.append(get_all_moves.pop(random.randint(0, len(get_all_moves)-1)))
				move = moves[random.randint(0, len(moves)-1)]
		return move

class Menu:
	def __init__(self, pos):
		self.pos = pos
		self.font_height = 56
		self.font = pygame.font.SysFont(None, self.font_height)
		# start button
		self.buttons = {}
		self.buttons['START'] = ((self.font.render('Start', True, (255, 255, 255),Board.ORANGE_COLOR),\
							(self.pos[0], self.pos[0])))

	def draw(self, screen):
		keys  = list(self.buttons.keys())
		for i in range(0, len(keys)):
			text, pos = self.buttons[keys[i]]
			screen.blit(text, (pos[0], pos[1]+i*text.get_height()  ))


	def get_intersecting_button(self, pos):
		keys  = list(self.buttons.keys())
		for i in range(0, len(keys)):
			button = self.buttons[keys[i]]
			button_pos = button[1]
			size = button[0].get_width(),button[0].get_height()
			if (pos[0] > button_pos[0] and pos[0] < button_pos[0]+size[0]) \
				and (pos[1] > button_pos[1] and pos[1] < button_pos[1]+size[1]):
				return keys[i]
		return None

def main():
	size = [550, 650]
	board = None
	player = None
	ai = None 
	selected_cell = None 
	potential_moves = None
	current_player = None
	winner = None
	start_clicked = False
	exit = False
	show_menu = True
	pygame.init()
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("138 Othello/Reversi ")
	clock = pygame.time.Clock()
	menu = Menu((size[0]//2,size[1]//2))
	# main while loop
	while not exit:
		mouse_clicked = False
		clock.tick(10)
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT:
				exit=True 
			elif event.type == pygame.KEYDOWN:
				a = None # do nothing
			elif event.type == pygame.MOUSEBUTTONDOWN:
				# if it is the current players turn!
				mouse_clicked = True
				mouse_pos = pygame.mouse.get_pos()

		# 
		screen.fill([0,0,0])
		if not show_menu:
			if winner != None:
				# handle game over prompt
				a = None
			# set winner if game over
			elif board.check_game_over():
				winner = board.get_winner()
				print('WINNER: PLAYER %d\nPlayer 1:%d\nPlayer 2:%d\n' % \
					(winner+1, board.get_score(board.P1),board.get_score(board.P2) ))

				# display winner!
			# make decision
			else:
				if not board.is_waiting():
					# player selection and is players turn
					if current_player == player:
						all_player_moves = board.get_all_moves(player)
						if not all_player_moves:
							current_player = board.toggle_player(current_player)
						# if player is selecting
						elif mouse_clicked:  
							#pick up piece an high light moves
							if selected_cell == None:
								cell = board.get_intersecting_cell(mouse_pos)
								# select piece if it is owned by player
								if cell and cell.owner == current_player:
									selected_cell = cell 
									potential_moves = board.get_moves(selected_cell)
							else:
								#try to place piece at cell
								cell = board.get_intersecting_cell(mouse_pos)
								if cell in potential_moves:
									# add the piece to the cell and flip all pieces in between
									board.move(current_player, cell)
									current_player = board.toggle_player(current_player)
								# unselect current piece if not selecting new piece
								if cell and cell.owner == current_player:
									selected_cell = cell 
									potential_moves = board.get_moves(selected_cell)
								else:
									selected_cell = None

					elif current_player == ai.player:
						move = ai.get_move()
						if move != Board.NO_MOVES:
							board.move(current_player,move[1])
						# update current player
						current_player = board.toggle_player(current_player)
			board.draw(screen)
			# if cell is celected highlight current piece, and any potential moves
			if selected_cell:
				# highlight the piece
				selected_cell.draw_highlight(screen, True)
				for move in potential_moves:
					move.draw_highlight(screen)
		
		else: #show_menu:
			if mouse_clicked: # handle menu input
				button_id = menu.get_intersecting_button(mouse_pos)
				if button_id == 'START':
					show_menu = False
					board = Board( (10, size[1]/12), (size[0], size[0]*0.95-10)  ) 
					player = Board.P1
					ai = AI(Board.P2, board) 
					selected_cell = None 
					potential_moves = []
					current_player = random.randint(Board.P1, Board.P2)
					winner = None
			menu.draw(screen)

		pygame.display.flip()


if __name__ == '__main__':
	main()
