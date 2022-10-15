import pygame
pygame.init()
import numpy as np

class Maze:

	def __init__(self, gameDisplay, x_i, y_i, x_l, y_l, color, goal = False):
		self.gameDisplay = gameDisplay
		self.x_i = x_i
		self.y_i = y_i
		self.x_l = x_l
		self.y_l = y_l
		self.color = color
		self.goal = goal

	def makeWall(self):
		pygame.draw.rect(self.gameDisplay, self.color, (self.x_i, self.y_i, self.x_l, self.y_l))


class Genes:
	
	def __init__(self, mutation = 0.01, numOfMoves = 500):
		self.numOfMoves = numOfMoves
		self.moves = [np.random.randint(low = 0, high = 4) for _ in range(self.numOfMoves)]
		self.mutation = mutation

	def mutate(self):
		# more creative ways to mutate
		for move in self.moves:
			if np.random.uniform(0, 1) < self.mutation: move = np.random.randint(low = 0, high = 4)


class Player:

	def __init__(self, gameDisplay, windowHeight, windowWidth, size = 5, color = (0, 0, 255), mutation  = 0.01, numOfMoves = 500 ):
		self.gameDisplay = gameDisplay
		self.size = size
		self.gene = Genes(mutation = mutation, numOfMoves = numOfMoves)
		self.geneIndex = 0
		self.x = windowWidth // 2
		self.color = color
		self.y = windowHeight - 2* self.size
		self.dead = False
		self.windowWidth = windowWidth
		self.windowHeight = windowHeight
		self.fitness = 0
		self.steps = 0
		self.probability = 0
		self.stx = self.x
		self.sty = self.y
		self.lead = False

	def setFitness(self):
		# more type of fitness scores
		self.fitness += (1 / (np.sqrt((self.y - 10)**2 + (self.x - self.windowWidth // 2) ** 2)))
		if not self.dead: self.fitness += 0.05
		return self.fitness

	def crossOver(parentOne, parentTwo):
		# todo: add more ways to cross over 
		child = Player(parentTwo.gameDisplay, parentOne.windowHeight, parentTwo.windowWidth)
		index = np.random.randint(low = 0, high = parentTwo.gene.numOfMoves)
		for idx in range(child.gene.numOfMoves):
			if idx < index: child.gene.moves[idx] = parentOne.gene.moves[idx]
			else: child.gene.moves[idx] = parentTwo.gene.moves[idx]
		return child

	def showPlayer(self):
		pygame.draw.circle(self.gameDisplay, self.color, (self.x, self.y), self.size)

	def moveUp(self):
		self.y -= self.size
		if self.y <= 0: 
			self.y += self.size
			self.dead = True
			self.color = (255, 0, 0)

	def moveDown(self):
		self.y += self.size
		if self.y >= self.windowHeight: 
			self.y -= self.size
			self.dead = True
			self.color = (255, 0, 0)

	def moveRight(self):
		self.x += self.size
		if self.x >= self.windowWidth: 
			self.x -= self.size
			self.dead = True
			self.color = (255, 0, 0)

	def moveLeft(self):
		self.x -= self.size
		if self.x <= 0: 
			self.x += self.size
			self.dead = True
			self.color = (255, 0, 0)


class Population:

	def __init__(self, gameDisplay, windowWidth, windowHeight, mutation = 0.1, populationSize = 50, numOfMoves = 500):
		self.populationSize = populationSize
		self.gameDisplay = gameDisplay
		self.windowWidth = windowWidth
		self.windowHeight = windowHeight
		self.players = [Player(self.gameDisplay, self.windowHeight, self.windowWidth, numOfMoves = numOfMoves, mutation=mutation) for _ in range(self.populationSize)]
		self.generation = 0
		self.matingPool = []
		self.bestFitness = 0

	def allDead(self):
		for player in self.players:
			if not player.dead: return False
		return True

	def evolve(self):
		self.computeFitness()
		self.naturalSelection()
		self.generate()

	def generate(self):
		self.players = []
		for _ in range(self.populationSize):
			p1, p2 = self.matingPool[np.random.randint(0,len(self.matingPool)-1)], self.matingPool[np.random.randint(0,len(self.matingPool)-1)]
			child = p1.crossOver(p2)
			child.gene.mutate()
			self.players.append(child)
		self.generation+=1

	def naturalSelection(self):
		self.matingPool = []
		maxFit = 0
		for player in self.players:
			if player.fitness > maxFit: maxFit = player.fitness

		for player in self.players:
			score = int((player.fitness / maxFit) * 100)
			while score > 0:
				self.matingPool.append(player)
				score -= 1

	# def pickSomeone(self):
	# 	index = np.random.randint(0, self.populationSize-1)
	# 	r = np.random.random()
	# 	while r > 0:
	# 		r -= self.players[index].fitness
	# 		index = (index + 1) % self.populationSize
	# 	return self.players[index - 1]

	# def generate(self):
	# 	matingPool = []
	# 	for player in self.players: player.probability = player.fitness / self.bestFitness
	# 	while len(self.players) != len(matingPool):
	# 		parentOne = self.pickSomeone()
	# 		parentTwo = self.pickSomeone()
	# 		child = parentOne.crossOver(parentTwo)
	# 		child.gene.mutate()
	# 		matingPool.append(child)
	# 	self.players = matingPool
	# 	self.generation += 1

	def computeFitness(self):
		self.bestFitness = 0
		for player in self.players: 
			fitn = player.setFitness()
			if fitn > self.bestFitness: self.bestFitness = fitn


class Environment:

	def __init__(self, windowWidth = 800, windowHeight = 600):
		self.windowWidth = windowWidth
		self.windowHeight = windowHeight
		self.backGround = (125, 125, 125)
		self.black = (0, 0, 0)
		self.white = (255, 255, 255)
		self.fps = pygame.time.Clock()
		self.gameDisplay = pygame.display.set_mode((self.windowWidth, self.windowHeight))
		self.population = Population(self.gameDisplay, self.windowWidth, self.windowHeight,populationSize = 500, mutation = 0.03, numOfMoves = 2000)
		self.Wall = [
			Maze(self.gameDisplay, 0, self.windowHeight // 3, (3*self.windowWidth) // 4, 10, self.black),\
			# Maze(self.gameDisplay,self.windowWidth // 9, 2*self.windowHeight // 3, (self.windowWidth),10,self.black),
			Maze(self.gameDisplay, self.windowWidth // 2, 10, 30, 30, self.white, goal = True)
		]

	def On(self):
		while True:
			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					pygame.quit()
					return

			for player in self.population.players:
				if not player.dead:
					if player.gene.moves[player.geneIndex] == 0:
						player.moveUp()
					elif player.gene.moves[player.geneIndex] == 1:
						player.moveDown()
					elif player.gene.moves[player.geneIndex] == 2:
						player.moveRight()
					elif player.gene.moves[player.geneIndex] == 3:
						player.moveLeft()
					player.geneIndex = (player.geneIndex + 1) % player.gene.numOfMoves
					player.steps += 1
				if player.geneIndex == player.gene.numOfMoves - 1: ######TO BE OPTIMIZED
					player.dead = True
				player.geneIndex %= player.gene.numOfMoves

			if self.population.allDead(): 
				self.population.evolve()
				#print('Generation : ',self.population.generation,'Best Score : ',self.population.bestFitness)

			self.gameDisplay.fill(self.backGround)
			for Wall in self.Wall: Wall.makeWall()
			self.collide()
			for player in self.population.players: player.showPlayer()
			self.sayMessage(msg = ''.join(['mutationsGeneration : ', str(self.population.generation)]),xpos = 10,color = (0, 0, 0))
			self.sayMessage(msg = ''.join(['Last Gen Score Score : ', str(np.sqrt(self.population.bestFitness))]),xpos = 10, ypos = 25, color = (0, 0, 0))
			pygame.display.update()


	def makeMsgObject(self,msg, fontDefination, color):
		surface = fontDefination.render(msg, True, color)
		return surface, surface.get_rect()

	def sayMessage(self, msg,fontType = 'freesansbold.ttf', fontSize = 12, xpos = 410, ypos = 10, color = (255, 255, 255)):
		fontDefination = pygame.font.Font(fontType,fontSize)
		msgSurface, messageRectangle = self.makeMsgObject(msg, fontDefination, color)
		messageRectangle = (xpos, ypos)
		self.gameDisplay.blit(msgSurface, messageRectangle)

	def isDead(self, player, hurdle):
		if (player.y <= hurdle.y_i + hurdle.y_l and player.y + player.size >= hurdle.y_i) \
			and (player.x <= hurdle.x_i + hurdle.x_l and player.x + player.size >= hurdle.x_i): 
				if hurdle.goal:
					player.color = (0, 255, 0)
					#player.fitness += np.interp(50, (0, self.windowWidth), (0, 100))
					player.fitness = 10

				else: 
					player.color = (255, 0, 0)
					player.fitness -= 10
				player.dead = True

	def collide(self):
		for hurdle in self.Wall:
			for player in self.population.players:
				self.isDead(player, hurdle)



if __name__ == '__main__':
	e = Environment()
	e.On()

