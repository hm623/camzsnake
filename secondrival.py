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

# Directions for computer rivals
global comp_direction, orange_direction
comp_direction = "right"
orange_direction = "up"

# Set up the screen
wn = turtle.Screen()
wn.title("Snake Game COMP491 Beta 3")
wn.bgcolor("white")
wn.setup(width=800, height=800)
wn.tracer(0)

def main_menu():
    """
    Displays the main menu for the Snake Game.
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
    wn.onkeypress(start_game, "m")
    wn.onkeypress(quit_game, "q")

def start_snake_game():
    """
    Starts the Snake Game with rival snakes.
    """
    global head, food, segments, pen, score, high_score
    global comp_head, comp_segments, comp_direction
    global orange_head, orange_direction

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

    segments = []

    # Rival Snake 1 (Blue - AI lawn mower)
    comp_head = turtle.Turtle()
    comp_head.speed(0)
    comp_head.shape("square")
    comp_head.color("blue")
    comp_head.penup()
    comp_head.goto(200, 200)
    comp_head.direction = "right"
    comp_segments = []

    # Rival Snake 2 (Orange - chaotic AI)
    orange_head = turtle.Turtle()
    orange_head.speed(0)
    orange_head.shape("square")
    orange_head.color("orange")
    orange_head.penup()
    orange_head.goto(-200, -200)
    orange_head.direction = "up"
    orange_segments = []

    # Score Pen
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 350)
    pen.write("Your Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

    # Player Controls
    

    def go_left():
        if head.direction != "right":
            head.direction = "left"

    def go_right():
        if head.direction != "left":
            head.direction = "right"

    def go_up():
        if head.direction != "down":
            head.direction = "up"

    def go_down():
        if head.direction != "up":
            head.direction = "down"

    def move():
        if head.direction == "up":
            head.sety(head.ycor() + 20)
        elif head.direction == "down":
            head.sety(head.ycor() - 20)
        elif head.direction == "left":
            head.setx(head.xcor() - 20)
        elif head.direction == "right":
            head.setx(head.xcor() + 20)

    # Move Rival 1 (Blue) in lawn-mower pattern
    def move_computer():
        global comp_direction
        if comp_direction == "right":
            comp_head.setx(comp_head.xcor() + 10)
            if comp_head.xcor() >= 390:
                comp_direction = "down"
        elif comp_direction == "down":
            comp_head.sety(comp_head.ycor() - 10)
            if comp_head.ycor() <= -390:
                comp_direction = "left"
        elif comp_direction == "left":
            comp_head.setx(comp_head.xcor() - 10)
            if comp_head.xcor() <= -390:
                comp_direction = "up"
        elif comp_direction == "up":
            comp_head.sety(comp_head.ycor() + 10)
            if comp_head.ycor() >= 390:
                comp_direction = "right"

    # Move Rival 2 (Orange) in chaotic/randomized fashion
    def move_orange():
        global orange_direction

        # Occasionally change direction randomly
        if random.randint(1, 10) == 1:
            orange_direction = random.choice(["up", "down", "left", "right", "diag_ul", "diag_ur", "diag_dl", "diag_dr"])

        # Move based on current direction
        if orange_direction == "up":
            orange_head.sety(orange_head.ycor() + 15)
        elif orange_direction == "down":
            orange_head.sety(orange_head.ycor() - 15)
        elif orange_direction == "left":
            orange_head.setx(orange_head.xcor() - 15)
        elif orange_direction == "right":
            orange_head.setx(orange_head.xcor() + 15)
        elif orange_direction == "diag_ul":
            orange_head.setx(orange_head.xcor() - 10)
            orange_head.sety(orange_head.ycor() + 10)
        elif orange_direction == "diag_ur":
            orange_head.setx(orange_head.xcor() + 10)
            orange_head.sety(orange_head.ycor() + 10)
        elif orange_direction == "diag_dl":
            orange_head.setx(orange_head.xcor() - 10)
            orange_head.sety(orange_head.ycor() - 10)
        elif orange_direction == "diag_dr":
            orange_head.setx(orange_head.xcor() + 10)
            orange_head.sety(orange_head.ycor() - 10)

        # Bounce off walls
        if orange_head.xcor() >= 390 or orange_head.xcor() <= -390 or orange_head.ycor() >= 390 or orange_head.ycor() <= -390:
            orange_direction = random.choice(["up", "down", "left", "right", "diag_ul", "diag_ur", "diag_dl", "diag_dr"])

    def game_loop():
        global score, high_score, delay
        wn.update()

        for index in range(len(segments)-1, 0, -1):
            x = segments[index-1].xcor()
            y = segments[index-1].ycor()
            segments[index].goto(x, y)

        if len(segments) > 0:
            segments[0].goto(head.xcor(), head.ycor())

        if head.xcor() > 390 or head.xcor() < -390 or head.ycor() > 390 or head.ycor() < -390:
            game_over()

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
            pygame.mixer.music.load("apple.wav")
            pygame.mixer.music.play()
            if score > high_score:
                high_score = score
            pen.clear()
            pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

        # Collision detection
        if head.distance(comp_head) < 20 or head.distance(orange_head) < 20:
            game_over()

        for segment in comp_segments:
            if head.distance(segment) < 20:
                game_over()

        move()
        move_computer()
        move_orange()
        wn.ontimer(game_loop, int(delay * 1000))

    def game_over():
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
        comp_segments.clear()
        orange_head.goto(-200, -200)
        orange_head.direction = "up"
        score = 0
        delay = 0.1
        pen.clear()
        pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

    # Bind keys
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

main_menu()
wn.mainloop()
