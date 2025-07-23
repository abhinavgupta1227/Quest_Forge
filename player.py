# player.py (Updated with Absolute Path)
import json
import os
import math

# --- NEW: Build a reliable path to the data file ---
# This finds where the script is running and creates a full, absolute path.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(SCRIPT_DIR, "data", "player_profile.json")


class Player:
    def __init__(self):
        # The default data structure remains the same
        self.data = {
            "name": "", "age": "", "gender": "", "level": 1,
            "xp": 0, "xp_limit": 10000, "stats": {
                "Strength": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "0xp task for refresh": 0,
                    "Daily gym": 80, "Hit a new PR": 300, "50 seconds deadhang": 150,
                    "35 pushups in a row": 200, "50 squats in a row": 150,
                    "60 seconds plank": 100, "5 pull-ups": 500
                }},
                "Knowledge": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Read 10 pages of a book": 80, "Studying bca subject for 1hr": 100,
                    "aptitude questions 10": 100, "research latest tech": 150,
                    "learn a new language": 200, "15 minutes GK": 80,
                    "20minutes current affair": 100, "10 minutes vocabulary": 90,
                    "learn a new skill": 300
                }}
            }
        }

    def set_profile(self, name, age, gender):
        self.data["name"] = name
        self.data["age"] = age
        self.data["gender"] = gender

    def save_profile(self):
        # Ensure the 'data' directory exists
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        # Save to the absolute path
        with open(PROFILE_PATH, "w") as f:
            json.dump(self.data, f, indent=4)

    def load_profile(self):
        # Load from the absolute path
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r") as f:
                self.data = json.load(f)
            return True
        return False

    def add_xp(self, amount):
        self.data["xp"] += amount
        leveled_up = False
        while self.data["xp"] >= self.data["xp_limit"]:
            self.data["xp"] -= self.data["xp_limit"]
            self.data["level"] += 1
            self.data["xp_limit"] = math.floor(self.data["xp_limit"] * 1.15)
            leveled_up = True
        return leveled_up

    def add_stat_xp(self, stat_name, task_name):
        if stat_name not in self.data["stats"]: return None
        stat = self.data["stats"][stat_name]
        if task_name not in stat["tasks"]: return None

        xp_gain = stat["tasks"][task_name]
        stat["xp"] += xp_gain
        stat_leveled_up = False
        while stat["xp"] >= stat["xp_limit"]:
            stat["xp"] -= stat["xp_limit"]
            stat["level"] += 1
            stat["xp_limit"] = math.floor(stat["xp_limit"] * 1.20)
            stat_leveled_up = True

        player_leveled_up = self.add_xp(xp_gain)
        self.save_profile()

        return {"stat_leveled_up": stat_leveled_up, "player_leveled_up": player_leveled_up, "xp_gained": xp_gain}