
/* Includes ------------------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
int threshold = 400;
/* Private variables ---------------------------------------------------------*/
SerialDevice serialDevice = new SerialDevice(this);

Snake snake;
Food food;

void setup() {
  size(640, 360);
  background(102);
  textAlign(CENTER, CENTER);
  textSize(64);
  text("Starting...", width / 2, (height - 40) / 2);
  textSize(16);
  text("www.freenove.com", width / 2, height - 20);
  frameRate(1000 / 40);

  food = new Food(new GridMap(new Size(width, height), 20, 2));
  snake = new Snake(new GridMap(new Size(width, height), 20, 2));
}

void draw() {
  if (!serialDevice.active())
  {
    if (!serialDevice.start())
    {
      delay(1000);
      return;
    }
  }

  int[] analogs = new int[2];
  analogs = serialDevice.requestAnalogs(2);
  if (analogs != null)
  {
    if (analogs[1] < 512 - threshold)
    {    
      if (snake.direction != Direction.DOWN)
        snake.nextDirection = Direction.UP;
    } 
    else if (analogs[1] > 512 + threshold) {
      if (snake.direction != Direction.UP)
        snake.nextDirection = Direction.DOWN;
    }
    if (analogs[0] < 512 - threshold) {
      if (snake.direction != Direction.RIGHT)
        snake.nextDirection = Direction.LEFT;
    } 
    else if (analogs[0] > 512 + threshold) {
      if (snake.direction != Direction.LEFT)
        snake.nextDirection = Direction.RIGHT;
    }
  }

  background(102);
  if (snake.gameState == GameState.WELCOME)
  {
    rectMode(CENTER);
    stroke(0, 0, 0);
    fill(0, 0, 0, 50);
    rect(width / 2, height / 2, width / 2, height / 3);
    fill(255, 255, 255);
    textSize(24);
    textAlign(CENTER, CENTER);
    text("Snake Game", width / 2, height / 2 - 24);
    text("Press Space to start", width / 2, height / 2 + 24);
  } 
  else if (snake.gameState == GameState.PLAYING)
  {
    if (snake.body[0].x == food.position.x && snake.body[0].y == food.position.y)
    {
      snake.grow();
      food.generate(snake.body, snake.length);
      snake.speedUp();
    }
    snake.step();
    showGame();
  } 
  else if (snake.gameState == GameState.LOSE)
  {
    showGame();
    rectMode(CENTER);
    stroke(0, 0, 0);
    fill(0, 0, 0, 50);
    rect(width / 2, height / 2, width / 2, height / 3);
    fill(255, 255, 255);
    textSize(24);
    textAlign(CENTER, CENTER);
    text("You lose!", width / 2, height / 2 - 24);
    text("Press Space to start", width / 2, height / 2 + 24);
  }
}

void showGame()
{
  snake.display();
  food.display();

  fill(255, 255, 255);
  textSize(16);
  textAlign(LEFT, CENTER);
  text("Press Enter to get help", 20, height - 20);
  textAlign(RIGHT, CENTER);
  text("Press Space to restart game", width - 20, height - 20);
  textAlign(LEFT, CENTER);
  text("Score: " + (snake.length - 3), 20, 20);
  textAlign(RIGHT, CENTER);
  text("Speed: " + ((50 - snake.speed) / 5 + 1), width - 20, 20);
}

void keyPressed() {
  if (key == CODED) 
  {
    if (keyCode == UP) 
    {
      if (snake.direction != Direction.DOWN)
        snake.nextDirection = Direction.UP;
    } 
    else if (keyCode == DOWN) {
      if (snake.direction != Direction.UP)
        snake.nextDirection = Direction.DOWN;
    } 
    else if (keyCode == LEFT) {
      if (snake.direction != Direction.RIGHT)
        snake.nextDirection = Direction.LEFT;
    } 
    else if (keyCode == RIGHT) {
      if (snake.direction != Direction.LEFT)
        snake.nextDirection = Direction.RIGHT;
    }
  } 
  else
  {
    if (key == '\n' || key == '\r')
    {
      link("COMP491 CAMZ");
    } 
    else if (key == ' ')
    {
      snake.reset();
      food.generate(snake.body, snake.length);
      snake.gameState = GameState.PLAYING;
    }
  }
}