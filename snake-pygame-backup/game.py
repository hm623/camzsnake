import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
#font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    """
    Represents the possible directions for movement in the game.

    Attributes:
        RIGHT (int): Represents movement to the right.
        LEFT (int): Represents movement to the left.
        UP (int): Represents upward movement.
        DOWN (int): Represents downward movement.
    """
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# RGB colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 20

class SnakeGameAI:
    """
    Represents the Snake Game with AI integration.

    Attributes:
        w (int): The width of the game window (default is 640).
        h (int): The height of the game window (default is 480).
        display (pygame.Surface): The game display surface.
        clock (pygame.time.Clock): The game clock to control the frame rate.
        direction (Direction): The current direction of the snake's movement.
        head (Point): The current position of the snake's head.
        snake (list of Point): The list of points representing the snake's body.
        score (int): The current score of the game.
        food (Point): The position of the food on the game board.
        frame_iteration (int): The number of frames since the last reset.
    """

    def __init__(self, w=640, h=480):
        """
        Initializes the game with the given width and height.

        Args:
            w (int): The width of the game window. Default is 640.
            h (int): The height of the game window. Default is 480.
        """
        self.w = w
        self.h = h
        # Initialize display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        """
        Resets the game state to its initial configuration.

        This method initializes or resets the following attributes:
        - direction: Sets the initial direction of the snake to the right.
        - head: Places the snake's head at the center of the game area.
        - snake: Initializes the snake's body as a list of points, starting
          with the head and extending to the left.
        - score: Resets the player's score to 0.
        - food: Places a new food item at a random location on the game board.
        - frame_iteration: Resets the frame iteration counter to 0.
        """
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        """
        Places food at a random location on the game grid.

        The food's position is determined by generating random x and y coordinates
        within the bounds of the game area, ensuring it aligns with the grid defined
        by BLOCK_SIZE. If the generated position coincides with the snake's body,
        the function recursively calls itself to generate a new position.
        """
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        """
        Executes a single step in the game based on the provided action.

        Args:
            action (list): A list of three integers representing the action to take.
                [1, 0, 0] - Continue moving in the current direction.
                [0, 1, 0] - Turn right.
                [0, 0, 1] - Turn left.

        Returns:
            tuple: A tuple containing:
                - reward (int): The reward for the current step. Positive if food is eaten,
                  negative if game over, and zero otherwise.
                - game_over (bool): True if the game is over, False otherwise.
                - score (int): The current score of the game.
        """
        self.frame_iteration += 1
        # Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Move
        self._move(action)  # Update the head
        self.snake.insert(0, self.head)

        # Check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # Place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # Update UI and clock
        self._update_ui()
        self.clock.tick(SPEED)

        return reward, game_over, self.score

    def is_collision(self, pt=None):
        """
        Checks for collisions in the game.

        Args:
            pt (Point, optional): The point to check for collision. If not provided,
                the snake's head position is used.

        Returns:
            bool: True if a collision is detected (either with the boundary or
            the snake itself), otherwise False.
        """
        if pt is None:
            pt = self.head
        # Hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Hits itself
        if pt in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        """
        Updates the game UI by rendering the snake, food, and score on the display.

        - Fills the display with a black background.
        - Draws the snake on the display using blue rectangles for each segment.
        - Draws the food on the display as a red rectangle.
        - Renders the current score at the top-left corner of the display.
        - Updates the display to reflect the changes.
        """
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):
        """
        Updates the direction of the snake and moves its head to the next position
        based on the given action.

        Args:
            action (list): A list of three integers representing the action to take.
                [1, 0, 0] - Continue moving in the current direction.
                [0, 1, 0] - Turn right.
                [0, 0, 1] - Turn left.
        """
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # No change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # Right turn
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # Left turn

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)
