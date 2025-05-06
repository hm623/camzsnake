

import tkinter as tk
import subprocess

def run_script(script_name):
    """
    Executes a Python script using the subprocess module.

    Args:
        script_name (str): The name of the Python script to be executed.
    """
    subprocess.run(['python', script_name])

def create_window():
    
    """
    Creates and displays the main menu window for the Snake Game.

    The menu includes buttons to launch different game modes or exit the application.
    """

    window = tk.Tk()
    window.title("Snake Game Menu")

    label = tk.Label(window, text="Welcome to the Snake Game Menu!")
    label.pack(pady=10)

    button1 = tk.Button(window, text="Play Test2", command=lambda: run_script('test2.py'))
    button1.pack(pady=5)

    button2 = tk.Button(window, text="Play Obstacle", command=lambda: run_script('Obstacles.py'))
    button2.pack(pady=5)

    button3 = tk.Button(window, text="Play SecondRival", command=lambda: run_script('SecondRival.py'))
    button3.pack(pady=5)

    button4 = tk.Button(window, text="Exit", command=window.quit)
    button4.pack(pady=20)

    window.mainloop()

if __name__ == "__main__":
    create_window()