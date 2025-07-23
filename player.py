# player.py (Refactored)
import json
import os
import math # Import math for scaling

class Player:
    def __init__(self):
        # The default data structure remains the same
        self.data = {
            "name": "",
            "age": "",
            "gender": "",
            "level": 1, # Start at level 1, not 0
            "xp": 0,
            "xp_limit": 10000,
            "stats": {
                "Strength": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
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
        os.makedirs("data", exist_ok=True)
        with open("data/player_profile.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def load_profile(self):
        if os.path.exists("data/player_profile.json"):
            with open("data/player_profile.json", "r") as f:
                self.data = json.load(f)
            return True
        return False

    def add_xp(self, amount):
        """Adds XP to the main player, handles level-ups, and returns level-up status."""
        self.data["xp"] += amount
        leveled_up = False
        while self.data["xp"] >= self.data["xp_limit"]:
            self.data["xp"] -= self.data["xp_limit"]
            self.data["level"] += 1
            # Increase next XP limit (e.g., by 15%)
            self.data["xp_limit"] = math.floor(self.data["xp_limit"] * 1.15)
            leveled_up = True
        return leveled_up

    def add_stat_xp(self, stat_name, task_name):
        """Adds XP to a stat and main player. Returns a dictionary of changes."""
        if stat_name not in self.data["stats"]:
            return None # Indicate failure

        stat = self.data["stats"][stat_name]
        if task_name not in stat["tasks"]:
            return None # Indicate failure

        xp_gain = stat["tasks"][task_name]
        
        # Add XP to the stat and check for level up
        stat["xp"] += xp_gain
        stat_leveled_up = False
        while stat["xp"] >= stat["xp_limit"]:
            stat["xp"] -= stat["xp_limit"]
            stat["level"] += 1
            # Increase next stat XP limit (e.g., by 20%)
            stat["xp_limit"] = math.floor(stat["xp_limit"] * 1.20)
            stat_leveled_up = True

        # *** REFACTORED PART ***
        # Call the main add_xp method and get its status
        player_leveled_up = self.add_xp(xp_gain)

        self.save_profile()

        # Return a rich status object for the UI to use
        return {
            "stat_leveled_up": stat_leveled_up,
            "player_leveled_up": player_leveled_up,
            "xp_gained": xp_gain
        }