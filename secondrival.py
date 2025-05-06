import pygame
import turtle
import time
import random

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
wn.setup(width=800, height=800)  # Set window size to 800x800
wn.tracer(0)  # Turns off the screen updates

def main_menu():

    """
    Displays the main menu for the Snake Game.

    Provides options to start the game or quit.
    """

    wn.clear()
    wn.bgcolor("white")
    menu_pen = turtle.Turtle()
    menu_pen.speed(0)
    menu_pen.color("black")
    menu_pen.penup()
    menu_pen.hideturtle()
    menu_pen.goto(0, 200)
    menu_pen.write("TeamCAMZ-Rival Snake Beta", align="center", font=("Courier", 36, "bold"))
    
    menu_pen.goto(0, 100)
    menu_pen.write("Press M to Play Against the Computer", align="center", font=("Courier", 24, "normal"))
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

def start_snake_game():

    """
    Starts the Snake Game with a computer-controlled rival snake.

    Initializes the player snake, computer snake, food, and game logic.
    """

    global head, food, segments, pen, score, high_score, comp_head, comp_segments, comp_direction
    wn.clear()
    
    # Snake head (Player Snake)
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

    # Computer Snake (AI Snake)
    comp_head = turtle.Turtle()
    comp_head.speed(0)
    comp_head.shape("square")
    comp_head.color("blue")
    comp_head.penup()
    comp_head.goto(200, 200)
    comp_head.direction = "right"  # Initial direction

    comp_segments = []

    # Initialize the comp_direction to make sure the computer snake starts moving
    comp_direction = "right"  # Start moving right

    # Pen
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 350)  # Adjusted position for a better fit on the smaller screen
    pen.write("Your Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

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
        if head.direction == "up":
            head.sety(head.ycor() + 20)
        elif head.direction == "down":
            head.sety(head.ycor() - 20)
        elif head.direction == "left":
            head.setx(head.xcor() - 20)
        elif head.direction == "right":
            head.setx(head.xcor() + 20)

    def move_computer():
        global comp_direction

        # Move the computer snake like a lawn mower
        if comp_direction == "right":
            comp_head.setx(comp_head.xcor() + 10)
            if comp_head.xcor() >= 390:  # Right edge of the 800x800 screen (400)
                comp_direction = "down"
        elif comp_direction == "down":
            comp_head.sety(comp_head.ycor() - 10)
            if comp_head.ycor() <= -390:  # Bottom edge of the 800x800 screen (-400)
                comp_direction = "left"
        elif comp_direction == "left":
            comp_head.setx(comp_head.xcor() - 10)
            if comp_head.xcor() <= -390:  # Left edge of the 800x800 screen (-400)
                comp_direction = "up"
        elif comp_direction == "up":
            comp_head.sety(comp_head.ycor() + 10)
            if comp_head.ycor() >= 390:  # Top edge of the 800x800 screen (400)
                comp_direction = "right"

    def game_loop():

        """
        Updates the game state, including movement, collisions, and scoring.
        """

        global score, high_score, delay
        wn.update()

        # Move player segments in reverse order
        for index in range(len(segments)-1, 0, -1):
            x = segments[index-1].xcor()
            y = segments[index-1].ycor()
            segments[index].goto(x, y)

        # Move first segment to head's position
        if len(segments) > 0:
            segments[0].goto(head.xcor(), head.ycor())

        # Check for a collision with the border
        if head.xcor() > 390 or head.xcor() < -390 or head.ycor() > 390 or head.ycor() < -390:
            game_over()

        # Check for a collision with the food
        if head.distance(food) < 20:
            food.goto(random.randint(-390, 390), random.randint(-390, 390))
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("light green")
            new_segment.penup()
            segments.append(new_segment)
            delay -= 0.1
            score += 10
            
            # Play sound when the snake eats the fruit
            pygame.mixer.music.load("apple.wav")
            pygame.mixer.music.play()

            if score > high_score:
                high_score = score
            pen.clear()
            pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))
        
        # Check for a collision with the computer snake
        if head.distance(comp_head) < 20:
            game_over()

        # Check for a collision between the player snake and computer snake segments
        for segment in comp_segments:
            if head.distance(segment) < 20:
                game_over()

        move()
        move_computer()

        wn.ontimer(game_loop, int(delay * 1000))

    def game_over():

        """
        Resets the game state and plays a game-over sound.
        """

        pygame.mixer.music.load("gameover.wav")
        pygame.mixer.music.play()
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"
        for segment in segments:
            segment.goto(1000, 1000)
        segments.clear()
        comp_head.goto(200, 200)
        comp_head.direction = "right"
        for segment in comp_segments:
            segment.goto(1000, 1000)
        comp_segments.clear()
        global score, high_score, delay
        score = 0
        delay = 0.1
        pen.clear()
        pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

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
