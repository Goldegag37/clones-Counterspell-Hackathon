import asyncio
import pygame
import sys
import os
import random

pygame.init()

clock = pygame.time.Clock()

# Screen size
screenSize = [1000, 650]
screen = pygame.display.set_mode((screenSize))
pygame.display.set_caption("Clones")

# Fonts
font = pygame.font.SysFont(None, 36)
bigFont = pygame.font.SysFont(None, 80)

# Global variables
score = 0
topScore = 0
speed = [5, 4]  # [greg , bot]
boxCount = 2  # Initial number of boxes
boxSize = 50  # Size of each box
boxMargin = 50  # Minimum margin from edges of the screen
boxes = []  # List to store box positions
gameState = "running"  # Tracks game state ('running' or 'game_over')

def generate_random_boxes(count, size, margin):
    """Generate random positions for boxes."""
    boxList = []
    max_attempts = 1000  # Limit attempts to avoid an infinite loop
    for _ in range(count):
        for _ in range(max_attempts):
            x = random.randint(margin, screenSize[0] - size - margin)
            y = random.randint(margin, screenSize[1] - size - margin)
            new_box = pygame.Rect(x, y, size, size)
            # Ensure no overlap with other boxes or the hat
            if not any(new_box.colliderect(existing) for existing in boxList) and not new_box.colliderect(hatRect):
                boxList.append(new_box)
                break
    return boxList

def handleBoxCollision():
    """Prevent the player from passing through boxes."""
    keys = pygame.key.get_pressed()

    for box in boxes:
        if gregRect.colliderect(box):  # Check for collision
            # Calculate overlap in both directions
            overlapX = min(box.right - gregRect.left, gregRect.right - box.left)
            overlapY = min(box.bottom - gregRect.top, gregRect.bottom - box.top)

            # Determine which side the collision happened and restrict movement
            if overlapX < overlapY:
                if gregRect.centerx < box.centerx and keys[pygame.K_RIGHT]:  # Moving right
                    gregRect.right = box.left
                elif gregRect.centerx > box.centerx and keys[pygame.K_LEFT]:  # Moving left
                    gregRect.left = box.right
            else:
                if gregRect.centery < box.centery and keys[pygame.K_DOWN]:  # Moving down
                    gregRect.bottom = box.top
                elif gregRect.centery > box.centery and keys[pygame.K_UP]:  # Moving up
                    gregRect.top = box.bottom

def advanceScore():
    """Update and display the score and top score."""
    global score, topScore
    topScore = max(score, topScore)
    
    # Render the score
    scoreTxt = font.render(f"Score: {score}", True, (255, 255, 255))
    topScoreTxt = font.render(f"Top Score: {topScore}", True, (255, 255, 255))
    
    # Blit the scores onto the screen
    screen.blit(scoreTxt, (10, 10))
    screen.blit(topScoreTxt, (10, 40))



    

def handleBotAI():
    """Move the bot towards the player and handle collision."""
    global botImage, score

    botDirectionX = gregRect.centerx - botRect.centerx
    botDirectionY = gregRect.centery - (botRect.centery + 40)
    distance = (botDirectionX ** 2 + botDirectionY ** 2) ** 0.5

    if distance < 20:  # Collision detected
        score = max(score - 1000, 0)  # Reduce score safely
        return False

    if distance != 0:  # Move bot towards player
        botDirectionX /= distance
        botDirectionY /= distance

    botRect.x += int(botDirectionX * speed[1])
    botRect.y += int(botDirectionY * speed[1])

    botImage = pygame.transform.flip(initBotImage, botDirectionX < 0, False)
    return False



def initBotSkin():
    global botRect, botImage, initBotImage

    # Load bot image
    imageDir = "images/bots"
    allFiles = os.listdir(imageDir)
    imageFiles = [file for file in allFiles if file.endswith('.png')]

    if imageFiles:
        botSkin = os.path.join(imageDir, random.choice(imageFiles))
    else:
        print("No image found")
        pygame.quit()
        sys.exit()

    initBotImage = pygame.transform.scale(pygame.image.load(botSkin), (96, 192))
    botImage = initBotImage
    botRect = botImage.get_rect()
    
def getRandPos():
    global initBotPos, initGregPos
    botPosX = random.randint(20, (screenSize[0] - 20)) 
    botPosY = random.randint(30, (screenSize[1] - 30))
    initBotPos = [botPosX, botPosY]

    gregPosX = random.randint(20, (screenSize[0] - 20)) 
    gregPosY = random.randint(30, (screenSize[1] - 30))
    initGregPos = [gregPosX, gregPosY]

def getRandObjPos():
    global objPos
    max_attempts = 1000
    for _ in range(max_attempts):
        objPosX = random.randint(boxMargin, screenSize[0] - boxMargin - hatRect.width)
        objPosY = random.randint(boxMargin, screenSize[1] - boxMargin - hatRect.height)
        objRect = pygame.Rect(objPosX, objPosY, hatRect.width, hatRect.height)

        if not any(objRect.colliderect(box) for box in boxes):
            objPos = [objPosX, objPosY]
            return

    print("Warning: Could not find a valid position for the hat after many attempts.")
    objPos = [boxMargin, boxMargin]

if True:  # Load player image
    initPlayerImage = pygame.transform.scale(pygame.image.load('images/greg.png'), (21, 72))
    gregImage = initPlayerImage
    gregRect = gregImage.get_rect()

if True:  # Load HAT
    initHatImage = pygame.transform.scale(pygame.image.load('images/hat.png'), (30, 24))
    hatImage = initHatImage
    hatRect = hatImage.get_rect()

def resetGame():
    """Reset all game variables to their initial state."""
    global score, botRect, gregRect, gregImage, botImage, initGregPos, initBotPos, hatRect, hatWait, boxes
    initBotSkin()
    getRandPos()
    getRandObjPos()
    score = 0
    botRect.center = initBotPos
    gregRect.center = initGregPos
    hatRect.center = objPos
    gregImage = initPlayerImage
    botImage = initBotImage
    hatWait = False
    boxes = generate_random_boxes(boxCount, boxSize, boxMargin)  # Generate initial boxes


def gameOverScreen():
    """Render the game over screen."""
    screen.fill((128, 128, 128))
    game_over_txt = font.render("Game Over", True, (255, 255, 255))
    score_txt = font.render(f"Your score was: {score}", True, (255, 255, 255))
    top_score_txt = font.render(f"The high score is: {topScore}", True, (255, 255, 255))
    restart_txt = font.render("Press R to restart, or Q to quit", True, (255, 255, 255))

    screen.blit(game_over_txt, (screenSize[0] // 2 - game_over_txt.get_width() // 2, screenSize[1] // 2 - 100))
    screen.blit(score_txt, (screenSize[0] // 2 - score_txt.get_width() // 2, screenSize[1] // 2 - 50))
    screen.blit(top_score_txt, (screenSize[0] // 2 - top_score_txt.get_width() // 2, screenSize[1] // 2))
    screen.blit(restart_txt, (screenSize[0] // 2 - restart_txt.get_width() // 2, screenSize[1] // 2 + 50))
    pygame.display.update()

async def main():
    """Main game loop."""
    global gregImage, botImage, clock, running, score, hatWait, speed, font, boxes
    running = True
    gameWon = False
    resetGame()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    resetGame()  # Restart
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()

        # Player controls
        if keys[pygame.K_LEFT] and gregRect.left > 1:
            gregRect.x -= speed[0]
            gregImage = pygame.transform.flip(initPlayerImage, True, False)

        if keys[pygame.K_RIGHT] and gregRect.right < screenSize[0] - 1:
            gregRect.x += speed[0]
            gregImage = initPlayerImage

        if keys[pygame.K_UP] and gregRect.top > 1:
            gregRect.y -= speed[0]

        if keys[pygame.K_DOWN] and gregRect.bottom < screenSize[1] - 1:
            gregRect.y += speed[0]

        # if keys[pygame.K_0]:  # Debugging: jump to high score
            # score = 40000

        # Adjust difficulty based on score
        if score < 10000:
            backColor = (100, 100, 100)
            speed[1] = 4
            boxCount = 2 

        if score > 10000:
            backColor = (80, 80, 80)
            speed[1] = 5
            boxCount = 3

        if score > 20000:
            backColor = (70, 70, 70)
            speed[1] = 6
            boxCount = 4 

        if score > 30000:
            backColor = (50, 50, 50)
            speed[1] = 7
            boxCount = 5 

        if score >= 39999:
            backColor = (50, 100, 50)
            speed[1] = 0
            boxCount = 0 
            botRect.center = (-40, -40)
            score = 39999
            hatRect.center = (-20, -20)
            winTex = bigFont.render("You Win!", True, (255, 255, 255))
            gameWon = True

        # Check bot collision
        handleBotAI()

        # Handle box collisions
        handleBoxCollision()

        # Hat collection
        if gregRect.colliderect(hatRect):
            score += 250
            hatRect.center = [-20, -20]
            boxes = generate_random_boxes(boxCount, boxSize, boxMargin)  # Generate new boxes
            getRandObjPos()
            hatRect.center = objPos


        # Render everything
        screen.fill(backColor)  # Clear the screen with background color

        # Draw elements
        screen.blit(botImage, botRect)
        screen.blit(gregImage, gregRect)
        screen.blit(hatImage, hatRect)

        # Draw the boxes
        for box in boxes:
            pygame.draw.rect(screen, (0, 0, 50), box)
        
        score += 1

        # Display score
        advanceScore()

        # Show "You Win" if applicable
        if gameWon:
            screen.blit(winTex, (screenSize[0] // 2 - winTex.get_width() // 2, screenSize[1] // 2))

        # pygame.display.flip()  # Update the display
        pygame.display.update()
        clock.tick(60)  # Limit the frame rate

        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
