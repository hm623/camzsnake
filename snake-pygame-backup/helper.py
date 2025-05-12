import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):

    """
    Plots the scores and mean scores of a game during training.
    This function visualizes the progress of training by plotting the scores 
    achieved in each game and the corresponding mean scores over time. It 
    updates the plot dynamically to reflect the latest data.
    Args:
        scores (list): A list of integers representing the scores achieved in each game.
        mean_scores (list): A list of floats representing the mean scores over time.
    Returns:
        None
    
    """

    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    
