import pygame
import turtle
import time
import random
import torch
from model import Linear_QNet
import os

# Load trained DQN models (CPU only)
# Blue AI Snake model
comp_model = Linear_QNet(11, 256, 3)
comp_model_path = '/model/model202-74'
if os.path.exists(comp_model_path):
    comp_model.load_state_dict(torch.load(comp_model_path, map_location=torch.device('cpu')))
    comp_model.eval()
else:
    print(f"Error: Trained model not found at {comp_model_path}. Please train the model first and place the file in the 'model' directory.")
    turtle.bye()
    exit()

# Orange AI Snake model
orange_model = Linear_QNet(11, 256, 3)
orange_model_path = 'model/model_g3_196-71'
if os.path.exists(orange_model_path):
    orange_model.load_state_dict(torch.load(orange_model_path, map_location=torch.device('cpu')))
    orange_model.eval()
else:
    print(f"Error: Trained orange model not found at {orange_model_path}. Please train the orange AI model first and place the file in the 'model' directory.")
    turtle.bye()
    exit()

# Initialize pygame mixer for audio
pygame.mixer.init()

apple_sound = pygame.mixer.Sound('apple.wav')

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
    Displays the main menu for the Rival Snake game.

    The menu includes:
        - A title: "TeamCAMZ-Rival Snake Beta".
        - Instructions to start the game by pressing the 'M' key.
        - Instructions to quit the game by pressing the 'Q' key.

    Event Listeners:
        - Pressing 'M' starts the game by calling the `start_game` function.
        - Pressing 'Q' exits the game by calling the `quit_game` function.
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
        """Clears the menu and starts the snake game."""
        menu_pen.clear()
        start_snake_game()

    def quit_game():
        """Exits the game by closing the Turtle graphics window."""
        turtle.bye()
        exit()

    wn.listen()
    wn.onkeypress(start_game, "m")
    wn.onkeypress(quit_game, "q")

def start_snake_game():
    """
    Initializes and starts a multi-snake game using the Turtle graphics library.

    This function sets up the game environment, including:
        - Player-controlled snake.
        - Two AI-controlled snakes.
        - Food and score tracking.

    Controls:
        - "W" or "Up Arrow": Move the player snake up.
        - "S" or "Down Arrow": Move the player snake down.
        - "A" or "Left Arrow": Move the player snake left.
        - "D" or "Right Arrow": Move the player snake right.
        - "Q": Quit the game.

    AI Behavior:
        The AI snakes use a Q-learning model to decide their movements based on the game state.
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
        """Changes the player's direction to left if not currently moving right."""
        if head.direction != "right":
            head.direction = "left"

    def go_right():
        """Changes the player's direction to right if not currently moving left."""
        if head.direction != "left":
            head.direction = "right"

    def go_up():
        """Changes the player's direction to up if not currently moving down."""
        if head.direction != "down":
            head.direction = "up"

    def go_down():
        """Changes the player's direction to down if not currently moving up."""
        if head.direction != "up":
            head.direction = "down"

    def quit_game():
        """Exits the game by closing the Turtle graphics window."""
        turtle.bye()
        exit()

    wn.listen()
    wn.onkeypress(go_up, "w")
    wn.onkeypress(go_up, "Up")
    wn.onkeypress(go_down, "s")
    wn.onkeypress(go_down, "Down")
    wn.onkeypress(go_left, "a")
    wn.onkeypress(go_left, "Left")
    wn.onkeypress(go_right, "d")
    wn.onkeypress(go_right, "Right")
    wn.onkeypress(quit_game, "q")

    def move_player():
        """
        Moves the player snake in the direction specified by `head.direction`.

        Directions:
            - "up": Moves the player upward by increasing the y-coordinate.
            - "down": Moves the player downward by decreasing the y-coordinate.
            - "left": Moves the player leftward by decreasing the x-coordinate.
            - "right": Moves the player rightward by increasing the x-coordinate.
        """
        if head.direction == "up":
            head.sety(head.ycor() + 20)
        elif head.direction == "down":
            head.sety(head.ycor() - 20)
        elif head.direction == "left":
            head.setx(head.xcor() - 20)
        elif head.direction == "right":
            head.setx(head.xcor() + 20)

    def move_ai_snake(snake_head, segments, q_model):
        """
        Controls the movement of an AI-controlled snake.

        Args:
            snake_head (turtle.Turtle): The head of the AI snake.
            segments (list): A list of Turtle objects representing the snake's body.
            q_model (torch.nn.Module): The Q-learning model used to predict the next move.
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
        points = {"l": (x-20,y), "r": (x+20,y), "u": (x,y+20), "d": (x,y-20)}
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
        pred = q_model(tensor)
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
        Main game loop for the Rival Snake game.

        Handles:
            - Player and AI snake movements.
            - Collision detection.
            - Food consumption and score updates.
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
        move_ai_snake(comp_head, comp_segments, comp_model)
        move_ai_snake(orange_head, orange_segments, orange_model)

        # Player boundary check
        if head.xcor() > 300 or head.xcor() < -300 or head.ycor() > 220 or head.ycor() < -220:
            head.goto(0, 0)
            head.direction = "stop"
            for seg in segments:
                seg.goto(1000, 1000)
            segments.clear()
            score = 0

        if head.distance(food)<20:
            apple_sound.play() 
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
