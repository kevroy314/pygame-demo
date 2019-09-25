# See https://www.pygame.org/docs/ref/draw.html for more demo code

# Import a library of functions called 'pygame'
import pygame
import numpy as np # import numpy for random generation
from flocking import get_triangle_points, update_locations # import the flocking logic

# Initialize the game engine
pygame.init()

# Set the height and width of the screen
size = [800, 600]
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Flocking pygame example")
 
#Loop until the user clicks the close button.
done = False # for deciding when to stop the simulation
clock = pygame.time.Clock() # for running simulation updates

# Define our simulation starting conditions and hyperparameters
N = 40                          # 40 gives a reasonably computable and nice result
speed = 5.0                     # 5 gives a nice result
interaction_radius = 100.0      # 100 gives a nice result
weights = (1.0, 0.1, 0.1)       # 1.0, 0.1, 0.1 gives a nice result
xs = np.random.randint(0, size[0], size=N) # X Location of each triangle (screen coordinates)
ys = np.random.randint(0, size[1], size=N) # Y Location of each triangle (screen coordinates)
os = np.random.random(size=N) * 2 * np.pi # Orientation of each triangle (radians)
cs = np.random.randint(0, 255, size=(N, 3)) # Colors of each triangle (RGB format)

while not done:
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10) # this is the frames per second of the simulation
     
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
 
    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.
     
    # Clear the screen and set the screen background
    screen.fill((255, 255, 255)) # Background color

    # Draw a circle to illustrate the interaction distance
    pygame.draw.circle(screen, (0, 128, 64, 64), (int(size[0]/2.), int(size[1]/2)), int(interaction_radius), 5)

    # This draws a triangle using the polygon command
    for x, y, o, c in zip(xs, ys, os, cs):
        pygame.draw.polygon(screen, c, get_triangle_points(x, y, o), 3)

    xs, ys, os = update_locations(xs, ys, os, size, speed=speed, interaction_radius=interaction_radius, weights=weights)

    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()

# Be IDLE friendly
pygame.quit()