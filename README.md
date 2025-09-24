⚔️ QuestForge: Gamify Your Life ⚔️
Welcome to QuestForge, a desktop application designed to turn your real-life goals and habits into an exciting role-playing game (RPG). Instead of just ticking off a to-do list, you'll level up your character, improve your stats, and defeat powerful bosses—all by being productive in your daily life.

This app is built to be your personal command center for self-improvement, making the journey of a thousand miles feel like a single, epic quest.

✨ Features
Character Progression: Create your hero and watch them level up as you complete tasks.

Stat Tracking: Improve 10 different real-life stats, from Strength and Knowledge to Relationships and Mindfulness.

Task System: Each stat has a customizable list of tasks that grant XP upon completion.

Daily Habits: Build powerful streaks by completing your daily habits. Be careful—missing a day comes with a penalty!

3-Day To-Do List: A "Yesterday, Today, Tomorrow" system to manage your daily quests effectively.

Dynamic Boss Encounters:

Daily Boss: A randomly generated quest from your own task list, offering a bonus XP reward. Comes with a daily reroll!

Weekly Boss: A challenging, pre-written main quest designed to push your limits and grant massive rewards.

Immersive Experience: Includes background music and sound effects to make your progress feel more rewarding.

Fully Customizable: Easily change tasks, habits, and bosses to perfectly match your own life goals.

🚀 Getting Started: Running the App
Want to run QuestForge on your own machine? Here’s how to get started in just a few minutes.

Step 1: Clone the Repository
First, you need to get the code. Open your terminal or Git Bash and run the following command to clone the project to your computer:

git clone [https://github.com/YOUR_USERNAME/QuestForge.git](https://github.com/YOUR_USERNAME/QuestForge.git)
cd QuestForge

(Remember to replace YOUR_USERNAME with your actual GitHub username!)

Step 2: Set Up a Python Environment (Recommended)
It's best practice to create a virtual environment to keep the project's dependencies separate from your system's Python installation.

# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Step 3: Install Required Libraries
The app depends on a few Python libraries. Install them all with this single command:

pip install customtkinter Pillow pygame

If you plan to package the app into an .exe, you'll also need PyInstaller:

pip install pyinstaller

Step 4: Run the App!
You're all set! To launch the app in development mode, simply run:

python main.py

The app window should appear, and you can start your adventure!

🛠️ Customizing Your QuestForge
The real power of QuestForge is making it your own. You can change almost everything about the game's content by editing a single file: player.py.

1. Customizing Your Stat Tasks
Open player.py. Inside the Player class, you'll find the self.data dictionary. This is where you can edit the tasks for each stat.

Example: To add a new task to the Strength stat, simply add a new entry to its tasks dictionary:

"Strength": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
    "Daily gym": 150,
    "Hit a new PR": 600,
    "Go for a 30-minute bike ride": 250, # <-- Your new task!
    # ... other tasks
}},

You can add, remove, or edit any task and its XP value for any stat.

2. Customizing Daily Habits
At the top of player.py, you'll find the HABIT_BLUEPRINTS dictionary. You can change these to match the habits you want to build.

HABIT_BLUEPRINTS = {
    "Drink 8 glasses of water": {"xp_value": 20, "penalty": -15},
    "Read for 15 minutes":      {"xp_value": 30, "penalty": -20},
    "Practice Duolingo for 10 mins": {"xp_value": 40, "penalty": -20}, # <-- Your new habit!
}

3. Customizing Weekly Bosses
The WEEKLY_BOSS_BLUEPRINT list at the top of player.py contains all possible weekly challenges. Feel free to edit these or add your own epic quests!

WEEKLY_BOSS_BLUEPRINT = [
    {"name": "The Librarian's Ghost", "primary objective": "Finish reading an entire book this week.", "stat objective": "Level up Knowledge & Mindfulness once each.", "xp_reward": 1500},
    # Add your new boss here
]

📦 Building Your Own Executable (.exe)
Once you've customized the app to your liking, you can package it into a single .exe file that you can put on your desktop or share with friends.

Step 1: A "Clean Build" (Recommended)
Before packaging, it's a good idea to delete the dist and build folders if they exist in your project directory. This ensures your new .exe is built completely fresh.

Step 2: Run the PyInstaller Command
Open your terminal, make sure you are in the root QuestForge directory, and run the following command:

python -m PyInstaller --onefile --windowed --icon="assets/logo.ico" --add-data "assets;assets" --add-data "sounds;sounds" main.py

--onefile: Bundles everything into a single executable.

--windowed: Hides the black console window when you run the app.

--add-data: Tells PyInstaller to include your assets and sounds folders inside the .exe.

Step 3: Find Your App!
After the command finishes, a new folder named dist will be created. Inside it, you will find main.exe.

You can rename this file to QuestForge.exe, move it anywhere you like, and run it! Congratulations, you've forged your own personalized productivity app.
