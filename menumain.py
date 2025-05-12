

import tkinter as tk
import subprocess

def run_script(script_name):
    """
        Executes a Python script by invoking it as a subprocess.
        Args:
            script_name (str): The name or path of the Python script to execute.
        Returns:
            None
    """
    subprocess.run(['python', script_name])

def create_window():
   
    """
        Creates the main menu window for the Snake Game.
        This function initializes a Tkinter window with a title and several buttons:
        - A welcome label at the top.
        - Buttons to launch different game modes by running corresponding scripts:
            - "Play Test2" runs 'test2.py'.
            - "Play Obstacle" runs 'Obstacles.py'.
            - "Play SecondRival" runs 'SecondRival.py'.
        - An "Exit" button to close the application.
        The window remains open until the user chooses to exit.

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