import pygame, sys, random

class Block(pygame.sprite.Sprite):
	def __init__(self,path,xPos,yPos):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (xPos,yPos))

class Player(Block):
	def __init__(self,path,xPos,yPos,speed):
		super().__init__(path,xPos,yPos)
		self.speed = speed
		self.movement = 0

	def screen_constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screenHeight:
			self.rect.bottom = screenHeight

	def update(self,ball_group):
		self.rect.y += self.movement
		self.screen_constrain()

class Ball(Block):
	def __init__(self,path,xPos,yPos,speedX,speedY,paddles):
		super().__init__(path,xPos,yPos)
		self.speedX = speedX * random.choice((-1,1))
		self.speedY = speedY * random.choice((-1,1))
		self.paddles = paddles
		self.active = False
		self.scoreTime = 0

	def update(self):
		if self.active:
			self.rect.x += self.speedX
			self.rect.y += self.speedY
			self.collisions()
		else:
			self.restart_counter()
		
	def collisions(self):
		if self.rect.top <= 0 or self.rect.bottom >= screenHeight:
			pygame.mixer.Sound.play(pongSound)
			self.speedY *= -1

		if pygame.sprite.spritecollide(self,self.paddles,False):
			pygame.mixer.Sound.play(pongSound)
			collisionPaddle = pygame.sprite.spritecollide(self,self.paddles,False)[0].rect
			if abs(self.rect.right - collisionPaddle.left) < 10 and self.speedX > 0:
				self.speedX *= -1
			if abs(self.rect.left - collisionPaddle.right) < 10 and self.speedX < 0:
				self.speedX *= -1
			if abs(self.rect.top - collisionPaddle.bottom) < 10 and self.speedY < 0:
				self.rect.top = collisionPaddle.bottom
				self.speedY *= -1
				self.speedX *= -1
			if abs(self.rect.bottom - collisionPaddle.top) < 10 and self.speedY > 0:
				self.rect.bottom = collisionPaddle.top
				self.speedY *= -1
				self.speedX *= -1

	def reset_ball(self):
		self.active = False
		self.speedX *= random.choice((-1,1))
		self.speedX *= random.choice((-1,1))
		self.scoreTime = pygame.time.get_ticks()
		self.rect.center = (screenWidth/2,screenHeight/2)
		pygame.mixer.Sound.play(scoreSound)

	def restart_counter(self):
		currentTime = pygame.time.get_ticks()
		countdownNumber = 3

		if currentTime - self.scoreTime <= 700:
			countdownNumber = 3
		if 700 < currentTime - self.scoreTime <= 1400:
			countdownNumber = 2
		if 1400 < currentTime - self.scoreTime <= 2100:
			countdownNumber = 1
		if currentTime - self.scoreTime >= 2100:
			self.active = True

		timeCounter = basicFont.render(str(countdownNumber),True,accentColour)
		timeCounterRect = timeCounter.get_rect(center = (screenWidth/2,screenHeight/2 + 50))
		pygame.draw.rect(screen,bgColour,timeCounterRect)
		screen.blit(timeCounter,timeCounterRect)

class Opponent(Block):
	def __init__(self,path,xPos,yPos,speed):
		super().__init__(path,xPos,yPos)
		self.speed = speed

	def update(self,ball_group):
		if self.rect.top < ball_group.sprite.rect.y:
			self.rect.y += self.speed
		if self.rect.bottom > ball_group.sprite.rect.y:
			self.rect.y -= self.speed
		self.constrain()

	def constrain(self):
		if self.rect.top <= 0: self.rect.top = 0
		if self.rect.bottom >= screenHeight: self.rect.bottom = screenHeight

class GameManager:
	def __init__(self,ballGroup,paddleGroup):
		self.playerScore = 0
		self.opponentScore = 0
		self.ballGroup = ballGroup
		self.paddleGroup = paddleGroup

	def run_game(self):
		# Drawing the game objects
		self.paddleGroup.draw(screen)
		self.ballGroup.draw(screen)

		# Updating the game objects
		self.paddleGroup.update(self.ballGroup)
		self.ballGroup.update()
		self.reset_ball()
		self.draw_score()

	def reset_ball(self):
		if self.ballGroup.sprite.rect.right >= screenWidth:
			self.opponentScore += 1
			self.ballGroup.sprite.reset_ball()
		if self.ballGroup.sprite.rect.left <= 0:
			self.playerScore += 1
			self.ballGroup.sprite.reset_ball()

	def draw_score(self):
		playerScore = basicFont.render(str(self.playerScore),True,accentColour)
		opponentScore = basicFont.render(str(self.opponentScore),True,accentColour)

		playerScoreRect = playerScore.get_rect(midleft = (screenWidth / 2 + 40,screenHeight/2))
		opponent_score_rect = opponentScore.get_rect(midright = (screenWidth / 2 - 40,screenHeight/2))

		screen.blit(playerScore,playerScoreRect)
		screen.blit(opponentScore,opponent_score_rect)

# General setup
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
screenWidth = 1000
screenHeight = 750
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Pong')

# Global Variables
bgColour = pygame.Color('grey12')
accentColour = (255, 255, 255)
basicFont = pygame.font.Font('Assets\\Pixel.ttf', 26)
pongSound = pygame.mixer.Sound("Assets\\Sounds\\Pong.ogg")
scoreSound = pygame.mixer.Sound("Assets\\Sounds\\Score.ogg")
middleStrip = pygame.Rect(screenWidth/2 - 2,0,4,screenHeight)

# Game objects
player = Player('Assets\\Sprites\\Player-Paddle.png',20,screenWidth/2,5)
opponent = Opponent('Assets\\Sprites\\Opponent-Paddle.png',screenWidth - 20,screenHeight/2,5)
paddleGroup = pygame.sprite.Group()
paddleGroup.add(player)
paddleGroup.add(opponent)

ball = Ball('Assets\\Sprites\\Ball.png',screenWidth/2,screenHeight/2,4,4,paddleGroup)
ballSprite = pygame.sprite.GroupSingle()
ballSprite.add(ball)

gameManager = GameManager(ballSprite,paddleGroup)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				player.movement -= player.speed
			if event.key == pygame.K_s:
				player.movement += player.speed
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w:
				player.movement += player.speed
			if event.key == pygame.K_s:
				player.movement -= player.speed
	
	# Background Stuff
	screen.fill(bgColour)
	pygame.draw.rect(screen,accentColour,middleStrip)
	
	# Run the game
	gameManager.run_game()

	# Rendering
	pygame.display.flip()
	clock.tick(120)