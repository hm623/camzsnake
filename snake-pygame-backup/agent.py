import torch 
import random 
import numpy as np
from collections import deque 
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer 
from helper  import plot
import csv
import os 


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

csv_path = "training_log_2.csv"
if not os.path.exists(csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Game", "Score", "Record", "Mean Score"])


class Agent: 

    """
    Agent class for implementing a reinforcement learning agent to play the Snake game.

    Attributes:
        n_games (int): Number of games played by the agent.
        epsilon (float): Exploration rate for randomness in action selection.
        gamma (float): Discount rate for future rewards.
        memory (deque): Replay memory to store experiences with a fixed maximum size.
        model (Linear_QNet): Neural network model for Q-learning.
        trainer (QTrainer): Trainer for optimizing the Q-learning model.
    """

    def __init__(self):

        """
        Initializes the agent with default parameters and components.

        Attributes:
            n_games (int): Counter for the number of games played.
            epsilon (float): Exploration rate for randomness in actions.
            gamma (float): Discount rate for future rewards in Q-learning.
            memory (deque): A deque to store experiences with a maximum length of MAX_MEMORY.
            model (Linear_QNet): Neural network model for Q-learning with input size 11, 
                hidden layer size 256, and output size 3.
            trainer (QTrainer): Trainer object for optimizing the model using Q-learning.
        """
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # auto removes old experiences
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):

        """
        Computes the current state of the game for the agent.

        The state is represented as a list of binary values indicating:
        - Danger in the current direction, to the right, or to the left.
        - The current movement direction of the snake.
        - The relative position of the food with respect to the snake's head.

        Args:
            game (SnakeGameAI): The current instance of the game.

        Returns:
            np.ndarray: A binary array representing the state of the game.
        """

        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_d)) or
            (dir_r and game.is_collision(point_u)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.food.x < head.x,  # food left
            game.food.x > head.x,  # food right
            game.food.y < head.y,  # food up
            game.food.y > head.y   # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):

        """
        Stores a single experience tuple in the agent's memory.

        Args:
            state (object): The current state of the environment.
            action (object): The action taken by the agent.
            reward (float): The reward received after taking the action.
            next_state (object): The state of the environment after the action.
            done (bool): A flag indicating whether the episode has ended.

        Note:
            If the memory is full, the oldest experience will be removed to make space for the new one.
        """

        self.memory.append((state, action, reward, next_state, done)) # pop oldest if full

    def train_long_memory(self):

        """
        Trains the agent using a batch of experiences from its memory.

        This method retrieves a batch of experiences from the agent's memory
        and uses them to train the model. If the memory contains more experiences
        than the defined batch size, a random sample of the specified batch size
        is taken. Otherwise, the entire memory is used. The experiences consist
        of states, actions, rewards, next states, and done flags, which are then
        passed to the trainer for a single training step.
        """

        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):

        """
        Trains the agent's model using a single step of experience.

        This method performs a short-term training step using the provided
        state, action, reward, next state, and done flag. It is typically
        used during the gameplay loop to update the model incrementally
        after each action.

        Args:
            state (array-like): The current state of the environment.
            action (array-like): The action taken by the agent.
            reward (float): The reward received after taking the action.
            next_state (array-like): The state of the environment after the action.
            done (bool): A flag indicating whether the episode has ended.
        """

        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):

        """
        Determines the next action for the agent based on the current state.

        The method uses an epsilon-greedy strategy to balance exploration and exploitation.
        With a probability determined by the epsilon value, the agent will either choose
        a random action (exploration) or select the action with the highest predicted value
        from the model (exploitation).

        Args:
            state (list or array-like): The current state of the environment, represented
                as a list or array of features.

        Returns:
            list: A one-hot encoded list representing the chosen action. For example,
                [1, 0, 0] corresponds to the first action, [0, 1, 0] to the second, and
                [0, 0, 1] to the third.
        """

        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


# 👇 Function to start training (outside of the Agent class!)
def train():

    """
    Trains the agent to play the Snake game using reinforcement learning.

    This function initializes the agent and the game environment, then enters
    an infinite loop where the agent plays the game, learns from its actions,
    and updates its model. The training process involves:
    
    - Retrieving the current state of the game.
    - Deciding the next move based on the agent's policy or a random action.
    - Performing the move and receiving feedback (reward, game status, score).
    - Training the agent's short-term memory and storing the experience.
    - Resetting the game and updating the agent's long-term memory when the game ends.
    - Saving the model if a new high score is achieved.
    - Logging the game number, score, record, and mean score to a CSV file.

    The function also maintains and updates lists for plotting scores and mean scores.

    Note:
        This function runs indefinitely until manually stopped.
    """

    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:
        # Get current state
        state_old = agent.get_state(game)

        # Get move based on model or random
        final_move = agent.get_action(state_old)

        # Perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # Train short memory and remember experience
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save(f"model_g3_{agent.n_games}-{score}")

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            #plot_scores.append(score)
            #total_score += score
            #mean_score = total_score / agent.n_games
            #plot_mean_scores.append(mean_score)
            #plot(plot_scores, plot_mean_scores)
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)

            # Append to CSV file
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([agent.n_games, score, record, mean_score])



# 👇 Run training only if file is run directly
if __name__ == '__main__':
    train()
