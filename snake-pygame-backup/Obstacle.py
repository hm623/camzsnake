import pygame
import turtle
import time
import random
import os

# Initialize pygame mixer for audio
pygame.mixer.init()

delay = 0.1

# Score
global score, high_score
score = 0
high_score = 0

# Set up the screen
wn = turtle.Screen()
wn.title("Snake Game COMP491 Beta 3")
wn.bgcolor("white")
wn.setup(width=800, height=600)
wn.tracer(0)  # Turns off the screen updates

# List to store obstacles
obstacles = []

def main_menu():
    """
    Displays the main menu for the Snake Game - Obstacle Challenge.

    The menu includes options to start the obstacle play mode or quit the game.
    It uses the turtle graphics library to render the menu on the screen.

    Menu Options:
        - Press 'M' to start the obstacle play mode.
        - Press 'Q' to quit the game.

    The function sets up event listeners for the key presses and defines
    the corresponding actions for starting the game or exiting the application.
    """
    wn.clear()
    wn.bgcolor("white")
    menu_pen = turtle.Turtle()
    menu_pen.speed(0)
    menu_pen.color("black")
    menu_pen.penup()
    menu_pen.hideturtle()
    menu_pen.goto(0, 200)
    menu_pen.write("Snake Game Team CAMZ - Obstacle Challenge", align="center", font=("Courier", 36, "bold"))
    
    menu_pen.goto(0, 100)
    menu_pen.write("Press M to Start Obstacle Play", align="center", font=("Courier", 24, "normal"))
    menu_pen.goto(0, 50)
    menu_pen.write("Press Q to Quit", align="center", font=("Courier", 24, "normal"))
    
    def start_game():
        """Clears the menu and starts the snake game."""
        menu_pen.clear()
        start_snake_game()
    
    def quit_game():
        """Exits the game by closing the Turtle graphics window."""
        turtle.bye()
    
    wn.listen()
    wn.onkeypress(start_game, "m")  # Press 'm' to start main play
    wn.onkeypress(quit_game, "q")   # Press 'q' to quit

def create_obstacles(num_obstacles):
    """
    Creates a specified number of obstacles at random positions on the screen.

    Args:
        num_obstacles (int): The number of obstacles to create.

    Returns:
        None
    """
    global obstacles
    obstacles.clear()  # Clear any previous obstacles
    for _ in range(num_obstacles):
        obstacle = turtle.Turtle()
        obstacle.speed(0)
        obstacle.shape("square")
        obstacle.color("black")
        obstacle.penup()
        x = random.randint(-19, 19) * 20
        y = random.randint(-14, 14) * 20
        obstacle.goto(x, y)
        obstacles.append(obstacle)

def start_snake_game():
    """
    Initializes and starts the snake game using the Turtle graphics library.

    This function sets up the game environment, including the snake, food, 
    obstacles, and score display. It also defines the movement and game logic, 
    such as collision detection, score updates, and game over conditions. 
    The game loop is initiated to handle continuous updates and interactions.

    Keyboard Controls:
        - 'W' or 'Up Arrow': Move up
        - 'S' or 'Down Arrow': Move down
        - 'A' or 'Left Arrow': Move left
        - 'D' or 'Right Arrow': Move right
    """
    global head, food, segments, pen, score, high_score, obstacles
    wn.clear()
    
    # Snake head
    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("green")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"

    # Snake food
    food = turtle.Turtle()
    food.speed(0)
    food.shape("circle")
    food.color("red")
    food.penup()
    food.goto(0, 100)

    segments = []

    # Pen
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 500)
    pen.write("Your Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

    # Create obstacles
    create_obstacles(20)  # You can change the number of obstacles here

    def go_up():
        """Changes the snake's direction to up if it is not currently moving down."""
        if head.direction != "down":
            head.direction = "up"

    def go_down():
        """Changes the snake's direction to down if it is not currently moving up."""
        if head.direction != "up":
            head.direction = "down"

    def go_left():
        """Changes the snake's direction to left if it is not currently moving right."""
        if head.direction != "right":
            head.direction = "left"

    def go_right():
        """Changes the snake's direction to right if it is not currently moving left."""
        if head.direction != "left":
            head.direction = "right"

    def move():
        """
        Moves the snake's head in the current direction by updating its position.

        The movement is determined by the value of `head.direction`, which can be
        "up", "down", "left", or "right". The position is adjusted by 20 units
        in the corresponding direction.
        """
        if head.direction == "up":
            head.sety(head.ycor() + 20)
        elif head.direction == "down":
            head.sety(head.ycor() - 20)
        elif head.direction == "left":
            head.setx(head.xcor() - 20)
        elif head.direction == "right":
            head.setx(head.xcor() + 20)
    
    def game_loop():
        """
        The main game loop for the snake game.

        This function handles the game's logic, including:
        - Updating the game window.
        - Moving the snake's segments.
        - Checking for collisions with the border, food, and obstacles.
        - Playing appropriate sound effects for events like eating food or game over.
        - Updating the score and high score.
        - Restarting the game when necessary.

        Note:
            The loop is recursively called using a timer to maintain the game's flow.
        """
        wn.update()

        # Move segments in reverse order
        for index in range(len(segments) - 1, 0, -1):
            x = segments[index - 1].xcor()
            y = segments[index - 1].ycor()
            segments[index].goto(x, y)

        # Move first segment to head's position
        if len(segments) > 0:
            segments[0].goto(head.xcor(), head.ycor())

        # Check for a collision with the border
        if head.xcor() > 390 or head.xcor() < -390 or head.ycor() > 290 or head.ycor() < -290:
            pygame.mixer.music.load("gameover.wav")
            pygame.mixer.music.play()
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "stop"
            for segment in segments:
                segment.goto(1000, 1000)
            segments.clear()
            global score, high_score, delay
            score = 0
            delay = 0.1
            pen.clear()
            pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

        # Check for a collision with the food
        if head.distance(food) < 20:
            x = random.randint(-19, 19) * 20
            y = random.randint(-14, 14) * 20
            food.goto(x, y)

            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("light green")
            new_segment.penup()
            segments.append(new_segment)
            delay = max(0.05, delay - 0.06)
            score += 10
            
            pygame.mixer.music.load("apple.wav")
            pygame.mixer.music.play()

            if score > high_score:
                high_score = score
            pen.clear()
            pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

        # Check for collision with obstacles
        for obstacle in obstacles:
            if head.distance(obstacle) < 20:
                pygame.mixer.music.load("gameover.wav")
                pygame.mixer.music.play()
                time.sleep(1)
                head.goto(0, 0)
                head.direction = "stop"
                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()
                score = 0
                delay = 0.1
                pen.clear()
                pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))
                break

        move()
        wn.ontimer(game_loop, int(delay * 1000))
    
    # Keyboard bindings
    wn.listen()
    wn.onkeypress(go_up, "w")
    wn.onkeypress(go_down, "s")
    wn.onkeypress(go_left, "a")
    wn.onkeypress(go_right, "d")
    wn.onkeypress(go_up, "Up")
    wn.onkeypress(go_down, "Down")
    wn.onkeypress(go_left, "Left")
    wn.onkeypress(go_right, "Right")    
    game_loop()

# Start the menu
main_menu()
wn.mainloop()