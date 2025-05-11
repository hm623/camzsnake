import pygame
import turtle
import time
import random

# Initialize pygame mixer
pygame.mixer.init()

delay = 0.1
score = 0
high_score = 0

# Store past positions of the player snake
player_history = []

# Setup screen
wn = turtle.Screen()
wn.title("Hardcore Snake Mode - TeamCAMZ")
wn.bgcolor("white")
wn.setup(width=800, height=800)
wn.tracer(0)

def start_hardcore_game():
    global head, food, segments, pen, score, high_score
    global blue_head, blue_direction
    global orange_head
    global black_head

    wn.clear()

    # Green player snake
    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("green")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"

    # Red food
    food = turtle.Turtle()
    food.speed(0)
    food.shape("circle")
    food.color("red")
    food.penup()
    food.goto(0, 100)

    segments = []

    # Blue AI snake (lawnmower pattern)
    blue_head = turtle.Turtle()
    blue_head.speed(0)
    blue_head.shape("square")
    blue_head.color("blue")
    blue_head.penup()
    blue_head.goto(-300, 300)
    blue_direction = "right"

    # Orange AI snake (chaotic movement)
    orange_head = turtle.Turtle()
    orange_head.speed(0)
    orange_head.shape("square")
    orange_head.color("orange")
    orange_head.penup()
    orange_head.goto(100, 100)

    # Black AI snake (hybrid: trail + chase)
    black_head = turtle.Turtle()
    black_head.speed(0)
    black_head.shape("square")
    black_head.color("black")
    black_head.penup()
    black_head.goto(-200, -200)

    # Score display
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 350)
    pen.write("Your Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

    # Controls
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

    def move_blue():
        global blue_direction
        if blue_direction == "right":
            blue_head.setx(blue_head.xcor() + 10)
            if blue_head.xcor() >= 390:
                blue_direction = "down"
        elif blue_direction == "down":
            blue_head.sety(blue_head.ycor() - 10)
            if blue_head.ycor() <= -390:
                blue_direction = "left"
        elif blue_direction == "left":
            blue_head.setx(blue_head.xcor() - 10)
            if blue_head.xcor() <= -390:
                blue_direction = "up"
        elif blue_direction == "up":
            blue_head.sety(blue_head.ycor() + 10)
            if blue_head.ycor() >= 390:
                blue_direction = "right"

    def move_orange():
        # Random angles to simulate chaotic motion
        if random.random() < 0.1:
            angle = random.randint(0, 360)
            orange_head.setheading(angle)
        orange_head.forward(15)

        if abs(orange_head.xcor()) > 390 or abs(orange_head.ycor()) > 390:
            orange_head.setheading(orange_head.heading() + 180)

    def move_black():
        # Shadow trail logic
        if len(player_history) > 20:
            target = player_history[-20]
            black_head.goto(target[0], target[1])

        # Hunter logic (occasional burst toward green snake)
        if random.random() < 0.05:
            if black_head.xcor() < head.xcor():
                black_head.setx(black_head.xcor() + 20)
            elif black_head.xcor() > head.xcor():
                black_head.setx(black_head.xcor() - 20)
            if black_head.ycor() < head.ycor():
                black_head.sety(black_head.ycor() + 20)
            elif black_head.ycor() > head.ycor():
                black_head.sety(black_head.ycor() - 20)

    def game_loop():
        global score, high_score, delay
        wn.update()

        # Save green snake's path
        player_history.append((head.xcor(), head.ycor()))
        if len(player_history) > 100:
            player_history.pop(0)

        # Move segments
        for i in range(len(segments)-1, 0, -1):
            x = segments[i-1].xcor()
            y = segments[i-1].ycor()
            segments[i].goto(x, y)
        if segments:
            segments[0].goto(head.xcor(), head.ycor())

        # Collision with border
        if abs(head.xcor()) > 390 or abs(head.ycor()) > 390:
            return game_over()

        # Eat food
        if head.distance(food) < 20:
            food.goto(random.randint(-390, 390), random.randint(-390, 390))
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("light green")
            new_segment.penup()
            segments.append(new_segment)
            delay = max(0.05, delay - 0.01)
            score += 10
            pygame.mixer.music.load("apple.wav")
            pygame.mixer.music.play()
            if score > high_score:
                high_score = score
            pen.clear()
            pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

        # Collision with any rival
        if head.distance(blue_head) < 20 or head.distance(orange_head) < 20 or head.distance(black_head) < 20:
            return game_over()

        move()
        move_blue()
        move_orange()
        move_black()

        wn.ontimer(game_loop, int(delay * 1000))

    def game_over():
        pygame.mixer.music.load("gameover.wav")
        pygame.mixer.music.play()
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"
        for s in segments:
            s.goto(1000, 1000)
        segments.clear()
        score = 0
        delay = 0.1
        pen.clear()
        pen.write(f"Your Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

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

start_hardcore_game()
wn.mainloop()
