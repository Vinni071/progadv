import pygame

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Player position
player1_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

# Load player image
player1_image = pygame.image.load("6444840-removebg-preview.png").convert_alpha()
player1_image = pygame.transform.scale(player1_image, (80, 80))

mark_image = pygame.image.load("7530653-pixel-art-ship-vetor-removebg-preview.png").convert_alpha()  # Nova imagem
mark_image = pygame.transform.scale(mark_image, (80, 80))

# Load background image
bg_img = pygame.image.load("pic5507181.jpg")
bg_img = pygame.transform.scale(bg_img, (1280, 720))

# List to store marks
marks = []

# Main loop
while running:
    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Pressing spacebar
                # Add current position of the player to the list
                marks.append((player1_pos.x, player1_pos.y))

    # Movement controls for player 1
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player1_pos.y -= 700 * dt
    if keys[pygame.K_s]:
        player1_pos.y += 700 * dt
    if keys[pygame.K_a]:
        player1_pos.x -= 700 * dt
    if keys[pygame.K_d]:
        player1_pos.x += 700 * dt

    # Draw background
    screen.blit(bg_img, (0, 0))

    # Draw the marks
    for mark in marks:
        player1_image = pygame.image.load("7530653-pixel-art-ship-vetor-removebg-preview.png")
        player1_image = pygame.transform.scale(player1_image, (80, 80))
        screen.blit(player1_image, mark)  # Draw images at saved positions
        

    # Draw the player
    screen.blit(player1_image, player1_pos)

    # Update the display
    pygame.display.update()

    # Limit FPS to 60 and calculate delta time
    dt = clock.tick(60) / 1000

pygame.quit()
