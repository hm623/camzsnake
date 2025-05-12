import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    """
    A neural network model for Q-learning with a single hidden layer.

    Attributes:
        linear1 (nn.Linear): The first linear layer that maps the input to the hidden layer.
        linear2 (nn.Linear): The second linear layer that maps the hidden layer to the output.
    """

    def __init__(self, input_size, hidden_size, output_size):
        """
        Initializes the Linear_QNet model.

        Args:
            input_size (int): The size of the input layer.
            hidden_size (int): The size of the hidden layer.
            output_size (int): The size of the output layer.
        """
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        """
        Performs a forward pass through the neural network.

        Args:
            x (torch.Tensor): The input tensor to the network.

        Returns:
            torch.Tensor: The output tensor after applying the layers and activation function.
        """
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        """
        Saves the current model's state dictionary to a file.

        Args:
            file_name (str): The name of the file to save the model to. Defaults to 'model.pth'.

        Notes:
            The method creates a directory named 'model' in the current working directory
            if it does not already exist. The model's state dictionary is then saved to
            the specified file within this directory.
        """
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    """
    A class to train a Q-learning model using PyTorch.

    Attributes:
        model (torch.nn.Module): The neural network model to be trained.
        lr (float): Learning rate for the optimizer.
        gamma (float): Discount factor for future rewards.
        optimizer (torch.optim.Optimizer): Optimizer for updating model parameters.
        criterion (torch.nn.Module): Loss function used for training.
    """

    def __init__(self, model, lr, gamma):
        """
        Initializes the QTrainer.

        Args:
            model (torch.nn.Module): The neural network model to be trained.
            lr (float): Learning rate for the optimizer.
            gamma (float): Discount factor for future rewards.
        """
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        """
        Performs a single training step for the reinforcement learning model.

        Args:
            state (list or np.ndarray): The current state of the environment.
            action (list or np.ndarray): The action taken by the agent.
            reward (float or list): The reward received after taking the action.
            next_state (list or np.ndarray): The next state of the environment after the action.
            done (bool or list): A flag indicating whether the episode has ended.

        Notes:
            - Converts input data to PyTorch tensors and ensures proper dimensions.
            - Computes the predicted Q-values for the current state using the model.
            - Updates the target Q-values based on the Bellman equation:
              Q_new = reward + gamma * max(next_predicted Q value) (if not done).
            - Calculates the loss between the predicted Q-values and the target Q-values.
            - Performs backpropagation and updates the model parameters using the optimizer.
        """
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # Predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action).item()] = Q_new

        # Calculate loss and backpropagate
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()



