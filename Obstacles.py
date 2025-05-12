import pygame
import turtle
import time
import random
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Convert all coordinates to grid cells
def to_grid(pos, grid_unit=20):
    
    """
    Converts a position in pixel coordinates to grid coordinates.
    Args:
        pos (list or tuple): A 2D position represented as (x, y) in pixel coordinates.
        grid_unit (int, optional): The size of each grid cell in pixels. Defaults to 20.
    Returns:
        list: A 2D position represented as [x, y] in grid coordinates.
    
    """

    return [int(pos[0] // grid_unit), int(pos[1] // grid_unit)]

def get_hint_path():

    """
    Generates a list of directions to guide the snake from its current position to the food
    while avoiding obstacles and the snake's own body. The function uses an AI model to 
    compute the path based on the current game state.
    Global Variables:
        head: The snake's head object, providing its current position.
        food: The food object, providing its current position.
        segments: A list of the snake's body segment objects, providing their positions.
        obstacles: A list of obstacle objects, providing their positions.
    Grid Details:
        - The grid size is defined as 96 columns by 54 rows.
        - Each grid cell is assumed to be 20 pixels in size.
    Steps:
        1. Converts the positions of the snake's head, food, body, and obstacles to grid coordinates.
        2. Constructs a prompt describing the game state and requests a path from an AI model.
        3. Parses the AI's response to extract a list of directions (UP, DOWN, LEFT, RIGHT).
        4. Highlights the computed path on the grid.
    Exceptions:
        - Handles errors in the AI response or parsing of directions.
        - Logs any issues encountered during the process.
    Note:
        This function requires the `openai` library for interacting with the AI model.
    
    """

    global head, food, segments, obstacles
    grid_size = [96, 54]  # assuming 20px per grid cell on a 1920x1080 canvas
    grid_unit = 20

    head_pos = to_grid((head.xcor(), head.ycor()))
    food_pos = to_grid((food.xcor(), food.ycor()))
    snake_body = [to_grid((seg.xcor(), seg.ycor())) for seg in segments]
    obs_pos = [to_grid((obs.xcor(), obs.ycor())) for obs in obstacles]

    prompt = f"""
            You are helping in a Snake game played on a grid. The grid size is {grid_size[0]} columns by {grid_size[1]} rows.
            The snake's head is at {head_pos}.
            Its body is at {snake_body}.
            The food is at {food_pos}.
            The obstacles are at {obs_pos}.

            Generate a list of directions (UP, DOWN, LEFT, RIGHT) that safely guide the snake from its head to the food.
            Avoid all obstacles and the snake's own body.
            Make sure the final grid position exactly matches the food location.
            Respond only with a Python list, like ["RIGHT", "UP", "UP", "LEFT"]. No extra words.
            """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        raw_output = response['choices'][0]['message']['content'].strip()

        try:
            start = raw_output.index("[")
            end = raw_output.index("]", start) + 1
            directions = eval(raw_output[start:end])  # safely extract the list
            highlight_path(head_pos, directions, grid_unit)
        except Exception as parse_err:
            print("Hint failed to parse directions:", parse_err)
            print("Raw output from GPT:", raw_output)

    except Exception as e:
        print("Hint failed:", e)


def highlight_path(start_pos, directions, unit):

    """
    Highlights a path on the grid based on a starting position and a sequence of directions.
    This function uses a turtle object to visually mark the path on the grid. It updates the 
    position based on the given directions and stamps the turtle at each step. At the end, 
    it checks if the path ends exactly on the food's position.
    Args:
        start_pos (list): The starting position on the grid as a list [x, y].
        directions (list): A list of strings representing movement directions 
                           ("UP", "DOWN", "LEFT", "RIGHT").
        unit (int): The size of one grid unit, used to calculate the turtle's movement.
    Returns:
        None
    
    """

    hint_turtle.clearstamps()
    pos = start_pos.copy()
    for direction in directions:
        if direction == "UP":
            pos[1] += 1
        elif direction == "DOWN":
            pos[1] -= 1
        elif direction == "LEFT":
            pos[0] -= 1
        elif direction == "RIGHT":
            pos[0] += 1

        x, y = pos[0]*unit, pos[1]*unit
        hint_turtle.goto(x, y)
        hint_turtle.stamp()
    if pos == to_grid((food.xcor(), food.ycor())):
        print("Path ends exactly on food!")
    else:
        print("Path missed the food!")


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
    The menu includes options to start the obstacle play or quit the game.
    It uses the turtle graphics library to render the menu on the screen.
    Menu Options:
    - Press 'M' to start the obstacle play.
    - Press 'Q' to quit the game.
    Functions:
    - start_game: Clears the menu and starts the snake game.
    - quit_game: Exits the game by closing the turtle graphics window.
    This function sets up event listeners for the key presses and handles
    the corresponding actions.
    
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
        menu_pen.clear()
        start_snake_game()
        

    
    def quit_game():
        turtle.bye()
    
    wn.listen()
    wn.onkeypress(start_game, "m")  # Press 'm' to start main play
    wn.onkeypress(quit_game, "q")   # Press 'q' to quit

def create_obstacles(num_obstacles):

    """
    Creates a specified number of obstacles at random positions on the screen.
    This function clears any existing obstacles and generates new ones. Each
    obstacle is represented as a turtle object with a square shape and black
    color. The obstacles are placed at random positions within a predefined
    grid.
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
    Initializes and starts the snake game.
    This function sets up the game environment, including the snake, food, 
    obstacles, and score display. It also defines the movement and game logic 
    for the snake, handles collisions, and manages the game loop.
    Key Features:
    - Initializes the snake, food, and obstacles.
    - Displays the current score and high score.
    - Handles keyboard input for controlling the snake's movement.
    - Implements game logic for collisions with borders, food, and obstacles.
    - Plays sound effects for specific events (e.g., eating food, game over).
    - Continuously updates the game state through a recursive game loop.
    Keyboard Controls:
    - 'W' or 'Up Arrow': Move the snake up.
    - 'S' or 'Down Arrow': Move the snake down.
    - 'A' or 'Left Arrow': Move the snake left.
    - 'D' or 'Right Arrow': Move the snake right.
    - 'H': Get a hint path (if implemented).
    Note:
    - The function uses the `turtle` module for graphics and `pygame` for sound effects.
    - The number of obstacles can be adjusted by modifying the `create_obstacles` call.
    
    """

    global head, food, segments, pen, score, high_score, obstacles
    wn.clear()
    
    # Snake head
    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("green")
    head.penup()
    head.goto(0,0)
    head.direction = "stop"

    # Snake food
    food = turtle.Turtle()
    food.speed(0)
    food.shape("circle")
    food.color("red")
    food.penup()
    food.goto(0,100)

    segments = []

    # Pen
    pen = turtle.Turtle()
    global hint_turtle
    hint_turtle = turtle.Turtle()
    hint_turtle.penup()
    hint_turtle.shape("square")
    hint_turtle.color("blue")
    hint_turtle.shapesize(1, 1)
    hint_turtle.hideturtle()

    pen.speed(0)
    pen.shape("square")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 500)
    pen.write("Your Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

    # Create obstacles
    create_obstacles(20)  # You can change the number of obstacles here

    # Functions
    def go_up():
        if head.direction != "down":
            head.direction = "up"

    def go_down():
        if head.direction != "up":
            head.direction = "down"

    def go_left():
        if head.direction != "right":
            head.direction = "left"

    def go_right():
        if head.direction != "left":
            head.direction = "right"

    def move():

        """
        Moves the snake's head in the current direction by updating its position.
        The movement is determined by the value of the `head.direction` attribute:
        - "up": Increases the y-coordinate of the head by 20 units.
        - "down": Decreases the y-coordinate of the head by 20 units.
        - "left": Decreases the x-coordinate of the head by 20 units.
        - "right": Increases the x-coordinate of the head by 20 units.
        Assumes that `head` is an object with `direction`, `setx`, `sety`, `xcor`, 
        and `ycor` attributes/methods.
        
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
        The main game loop for the snake game. This function handles the following:
        - Updates the game window.
        - Moves the snake segments to follow the head.
        - Checks for collisions with the border, food, and obstacles.
        - Plays appropriate sound effects for game events.
        - Updates the score and high score when the snake eats food.
        - Resets the game state when the snake collides with the border or obstacles.
        - Continuously schedules itself to run based on the current game delay.
        Note:
        - The function uses global variables such as `score`, `high_score`, `delay`, `segments`, `head`, `food`, `obstacles`, and `pen`.
        - Sound effects are played using the `pygame.mixer` module.
        - The game loop is recursively scheduled using `wn.ontimer`.
        
        """

        wn.update()

        # Move segments in reverse order
        for index in range(len(segments)-1, 0, -1):
            x = segments[index-1].xcor()
            y = segments[index-1].ycor()
            segments[index].goto(x, y)

        # Move first segment to head's position
        if len(segments) > 0:
            segments[0].goto(head.xcor(), head.ycor())

        # Check for a collision with the border
        if head.xcor()>390 or head.xcor()<-390 or head.ycor()>290 or head.ycor()<-290:
            pygame.mixer.music.load("gameover.wav")  # Load the game over sound
            pygame.mixer.music.play()  # Play the game over sound
            time.sleep(1)  # Give time for the sound to play
            head.goto(0,0)
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
            
            # Play sound when the snake eats the fruit
            pygame.mixer.music.load("apple.wav")
            pygame.mixer.music.play()

            if score > high_score:
                high_score = score
            pen.clear()
            pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

        # Check for collision with obstacles
        for obstacle in obstacles:
            if head.distance(obstacle) < 20:
                pygame.mixer.music.load("gameover.wav")  # Load the game over sound
                pygame.mixer.music.play()  # Play the game over sound
                time.sleep(1)  # Give time for the sound to play
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
    wn.onkeypress(get_hint_path, "h")
    
    game_loop()

# Start the menu
main_menu()
wn.mainloop()