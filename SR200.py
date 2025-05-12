import pygame
import turtle
import time
import random
import torch
from model import Linear_QNet
import os
model = Linear_QNet(11, 256, 3)
model_path = 'model/model202-74'
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
else:
    print(f"Error: Trained model not found at {model_path}. Please train the model first and place the .pth file in the 'model' directory.")
    turtle.bye()
    exit()

# Initialize pygame mixer for audio
pygame.mixer.init()

delay = 0.00  # 2x speedup
score = 0
high_score = 0
comp_score = 0
orange_score = 0

# Set up the screen
wn = turtle.Screen()
wn.title("Snake Game COMP491 Beta 3")
wn.bgcolor("white")
wn.setup(width=640, height=480)
wn.tracer(0)

def main_menu():

    """
    Displays the main menu for the TeamCAMZ-Rival Snake Beta game.

    The menu provides the following options:
    - Press 'M' to start the game and play against the computer.
    - Press 'Q' to quit the game.

    The function sets up the graphical interface for the menu using the turtle module,
    listens for user input, and binds the appropriate keys to their respective actions:
    - 'M' key starts the game by calling the `start_snake_game` function.
    - 'Q' key exits the game by closing the turtle graphics window and terminating the program.

    """

    wn.clear()
    wn.bgcolor("white")
    menu_pen = turtle.Turtle()
    menu_pen.speed(0)
    menu_pen.color("black")
    menu_pen.penup()
    menu_pen.hideturtle()
    menu_pen.goto(0, 200)
    menu_pen.write("TeamCAMZ-Rival Snake Beta", align="center", font=("Courier", 12, "bold"))
    menu_pen.goto(0, 100)
    menu_pen.write("Press M to Play Against the Computer", align="center", font=("Courier", 10, "normal"))
    menu_pen.goto(0, 50)
    menu_pen.write("Press Q to Quit", align="center", font=("Courier", 10, "normal"))

    def start_game():
        menu_pen.clear()
        start_snake_game()

    def quit_game():
        turtle.bye()
        exit()

    wn.listen()
    wn.onkeypress(start_game, "m")
    wn.onkeypress(quit_game, "q")

def start_snake_game():

    """
    Initializes and starts the snake game with multiple players, including AI-controlled snakes.
    This function sets up the game environment, including the player-controlled snake, 
    two AI-controlled snakes, food, and score tracking. It also defines controls for 
    the player and handles the game loop, which updates the game state and checks for 
    collisions or interactions.
    Features:
    - Player-controlled snake with keyboard controls (W/A/S/D or arrow keys).
    - Two AI-controlled snakes (blue and orange) with basic decision-making.
    - Food spawning and score tracking for all snakes.
    - Boundary collision detection and reset for all snakes.
    - Dynamic game loop with periodic updates.
    Controls:
    - W/Up Arrow: Move up
    - A/Left Arrow: Move left
    - S/Down Arrow: Move down
    - D/Right Arrow: Move right
    - Q: Quit the game
    Global Variables:
    - score: Tracks the player's score.
    - high_score: Tracks the highest score achieved.
    - delay: Controls the speed of the game loop.
    - comp_score: Tracks the score of the blue AI snake.
    - orange_score: Tracks the score of the orange AI snake.
    Dependencies:
    - Requires the `turtle` module for graphics.
    - Requires the `torch` module for AI decision-making.
    - Requires the `random` module for food placement.
    Note:
    - The game window must be initialized as `wn` before calling this function.
    - The AI snakes rely on a pre-trained model (`model`) for decision-making.
    
    """

    global score, high_score, delay, comp_score, orange_score
    wn.clear()

    # Player Snake
    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("green")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"

    # Food
    food = turtle.Turtle()
    food.speed(0)
    food.shape("circle")
    food.color("red")
    food.penup()
    food.goto(0, 100)

    # Tail segments
    segments = []
    comp_segments = []
    orange_segments = []

    # AI Snakes
    comp_head = turtle.Turtle()
    comp_head.speed(0)
    comp_head.shape("square")
    comp_head.color("blue")
    comp_head.penup()
    comp_head.goto(200, 150)
    comp_head.direction = "right"

    orange_head = turtle.Turtle()
    orange_head.speed(0)
    orange_head.shape("square")
    orange_head.color("orange")
    orange_head.penup()
    orange_head.goto(-200, -150)
    orange_head.direction = "up"

    # Score Pen
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 200)
    pen.write(f"You: {score}   Blue AI: {comp_score}   Orange AI: {orange_score}   High: {high_score}", align="center", font=("Courier", 8, "normal"))

    # Controls
    def go_left():
        if head.direction != "right": head.direction = "left"
    def go_right():
        if head.direction != "left": head.direction = "right"
    def go_up():
        if head.direction != "down": head.direction = "up"
    def go_down():
        if head.direction != "up": head.direction = "down"

    def quit_game():
        wn.bye()

    wn.listen()
    wn.onkeypress(go_up, "w"); wn.onkeypress(go_up, "Up")
    wn.onkeypress(go_down, "s"); wn.onkeypress(go_down, "Down")
    wn.onkeypress(go_left, "a"); wn.onkeypress(go_left, "Left")
    wn.onkeypress(go_right, "d"); wn.onkeypress(go_right, "Right")
    wn.onkeypress(quit_game, "q")


    


    def move_player():
        if head.direction == "up": head.sety(head.ycor() + 20)
        elif head.direction == "down": head.sety(head.ycor() - 20)
        elif head.direction == "left": head.setx(head.xcor() - 20)
        elif head.direction == "right": head.setx(head.xcor() + 20)

    def move_ai_snake(snake_head, segments):

        """
        Controls the movement of an AI-controlled snake in the game.
        Args:
            snake_head (turtle.Turtle): The head of the AI snake, represented as a Turtle object.
            segments (list): A list of Turtle objects representing the body segments of the snake.
        Behavior:
            - The function determines the next move for the AI snake based on its current direction,
              position, and proximity to the food.
            - It checks for collisions with the game boundaries and resets the snake's position
              if a collision occurs.
            - The AI uses a trained model to predict the next direction to move based on the current
              state of the game.
            - If the snake eats the food, a new food position is generated, and a new segment is added
              to the snake's body. The score is updated based on the snake's color.
        Global Variables:
            comp_score (int): The score of the blue snake.
            orange_score (int): The score of the orange snake.
        Notes:
            - The function uses PyTorch for tensor operations and model predictions.
            - The snake's movement is constrained to a grid with 20-pixel steps.'
            
        """        

        global comp_score, orange_score
        def collision(x, y):
            if x > 300 or x < -300 or y > 220 or y < -220:
                if snake_head.color()[0] == "blue":
                    snake_head.goto(200, 150); snake_head.direction = "right"
                    for seg in segments: seg.goto(1000,1000)
                    segments.clear()
                else:
                    snake_head.goto(-200, -150); snake_head.direction = "up"
                    for seg in segments: seg.goto(1000,1000)
                    segments.clear()
                return True
            return False

        dirs = ["right","down","left","up"]
        idx = dirs.index(snake_head.direction)
        x,y = snake_head.xcor(), snake_head.ycor()
        points = {("l"): (x-20,y), ("r"): (x+20,y), ("u"): (x,y+20), ("d"): (x,y-20)}
        dirs_bool = {d: snake_head.direction==d for d in ["left","right","up","down"]}
        state = [
            (dirs_bool["right"] and collision(*points["r"])) or
            (dirs_bool["left"] and collision(*points["l"])) or
            (dirs_bool["up"] and collision(*points["u"])) or
            (dirs_bool["down"] and collision(*points["d"])),
            (dirs_bool["up"] and collision(*points["r"])) or
            (dirs_bool["down"] and collision(*points["l"])) or
            (dirs_bool["left"] and collision(*points["u"])) or
            (dirs_bool["right"] and collision(*points["d"])),
            (dirs_bool["up"] and collision(*points["l"])) or
            (dirs_bool["down"] and collision(*points["r"])) or
            (dirs_bool["left"] and collision(*points["d"])) or
            (dirs_bool["right"] and collision(*points["u"])),
            dirs_bool["left"], dirs_bool["right"], dirs_bool["up"], dirs_bool["down"],
            food.xcor()<x, food.xcor()>x, food.ycor()>y, food.ycor()<y
        ]
        tensor = torch.tensor(state, dtype=torch.float)
        pred = model(tensor)
        m = torch.argmax(pred).item()
        new_dir = dirs[idx] if m==0 else dirs[(idx+1)%4] if m==1 else dirs[(idx-1)%4]
        snake_head.direction = new_dir
        if new_dir=="right": snake_head.setx(x+20)
        elif new_dir=="left": snake_head.setx(x-20)
        elif new_dir=="up": snake_head.sety(y+20)
        else: snake_head.sety(y-20)

        if snake_head.distance(food)<20:
            food.goto(random.randint(-280,280), random.randint(-200,200))
            new_seg = turtle.Turtle(); new_seg.speed(0)
            new_seg.shape("square"); new_seg.color(snake_head.color()[0]); new_seg.penup()
            segments.append(new_seg)
            if snake_head.color()[0] == "blue": comp_score +=1
            else: orange_score +=1

    def game_loop():

        """
        Main game loop for the snake game.

        This function handles the following:
        - Updates the game window.
        - Moves the player's snake and AI-controlled snakes.
        - Checks for boundary collisions for the player's snake.
        - Handles food consumption by the player's snake and updates the score.
        - Updates the game scoreboard.
        - Recursively schedules the next iteration of the game loop.

        Global Variables:
        - score: The current score of the player.
        - high_score: The highest score achieved in the game.
        - delay: The delay between game loop iterations.
        - segments: List of turtle segments representing the player's snake.
        - comp_segments: List of turtle segments representing the blue AI snake.
        - orange_segments: List of turtle segments representing the orange AI snake.
        - head: The player's snake head turtle object.
        - comp_head: The blue AI snake head turtle object.
        - orange_head: The orange AI snake head turtle object.
        - food: The food turtle object.
        - pen: The turtle object used for displaying the scoreboard.
        - wn: The game window object.

        Notes:
        - The player's snake grows when it eats food.
        - The game resets the player's snake and score if it collides with the boundary.
        - The function uses `wn.ontimer` to schedule itself for continuous execution.

        """

        global score, high_score, delay
        wn.update()
        for i in range(len(segments)-1,0,-1): segments[i].goto(segments[i-1].pos())
        if segments: segments[0].goto(head.pos())
        for i in range(len(comp_segments)-1,0,-1): comp_segments[i].goto(comp_segments[i-1].pos())
        if comp_segments: comp_segments[0].goto(comp_head.pos())
        for i in range(len(orange_segments)-1,0,-1): orange_segments[i].goto(orange_segments[i-1].pos())
        if orange_segments: orange_segments[0].goto(orange_head.pos())

        move_player()
        move_ai_snake(comp_head, comp_segments)
        move_ai_snake(orange_head, orange_segments)

        # Player boundary check
        if head.xcor() > 300 or head.xcor() < -300 or head.ycor() > 220 or head.ycor() < -220:
            head.goto(0, 0)
            head.direction = "stop"
            for seg in segments:
                seg.goto(1000, 1000)
            segments.clear()
            score = 0

        if head.distance(food)<20:
            food.goto(random.randint(-280,280), random.randint(-200,200))
            new_seg = turtle.Turtle(); new_seg.speed(0)
            new_seg.shape("square"); new_seg.color("green"); new_seg.penup()
            segments.append(new_seg)
            score+=1
            if score>high_score: high_score=score

        pen.clear()
        pen.write(f"You: {score}  Blue AI: {comp_score}  Orange AI: {orange_score}  High: {high_score}", align="center", font=("Courier", 8, "normal"))
        wn.ontimer(game_loop, int(delay*1000))

    game_loop()

main_menu()
wn.mainloop()
