import json
import os

class Player:
    def __init__(self):
        self.data = {
            "name": "",
            "age": "",
            "gender": "",
            "level": 0,
            "xp": 0,
            "xp_limit": 10000,
            "stats": {
                "Strength": {
                    "level": 1,
                    "xp": 0,
                    "xp_limit": 1000,
                    "tasks": {
                        "Daily gym" : 80,
                        "Hit a new PR" : 300,
                        "50 seconds deadhang" : 150,
                        "35 pushups in a row" : 200,
                        "50 squats in a row" : 150,
                        "60 seconds plank" : 100,
                        "5 pull-ups" : 500
                    }
                },
                "Knowledge": {
                    "level": 1,
                    "xp": 0,
                    "xp_limit": 1000,
                    "tasks": {
                        "Read 10 pages of a book" : 80,
                        "Studying bca subject for 1hr" : 100,
                        "aptitude questions 10" : 100,
                        "research latest tech" : 150,
                        "learn a new language" : 200,
                        "15 minutes GK" : 80,
                        "20minutes current affair" : 100,
                        "10 minutes vocabulary" : 90,
                        "learn a new skill" : 300

                    }
                },

            }
        }

    def set_profile(self, name, age, gender):
        """Sets the player's basic info."""
        self.data["name"] = name
        self.data["age"] = age
        self.data["gender"] = gender

    def save_profile(self):
        """Saves the player profile to data/player_profile.json."""
        os.makedirs("data", exist_ok=True)
        with open("data/player_profile.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def load_profile(self):
        """Loads the player profile if it exists; returns True/False."""
        if os.path.exists("data/player_profile.json"):
            with open("data/player_profile.json", "r") as f:
                self.data = json.load(f)
            return True
        return False

    def add_xp(self, amount):
        """Adds XP, updates level if XP limit reached."""
        self.data["xp"] += amount
        while self.data["xp"] >= self.data["xp_limit"]:
            self.data["xp"] -= self.data["xp_limit"]
            self.data["level"] += 1
            print(f"Level up! New level: {self.data['level']}")
        self.save_profile()
    
    def add_stat_xp(self, stat_name, task_name):
        """Adds XP to a stat and main XP based on task completed."""
        if stat_name not in self.data["stats"]:
            print(f"Stat '{stat_name}' does not exist.")
            return

        stat = self.data["stats"][stat_name]

        if task_name not in stat["tasks"]:
            print(f"Task '{task_name}' not found in {stat_name}.")
            return

        xp_gain = stat["tasks"][task_name]

        # Add XP to the stat
        stat["xp"] += xp_gain
        print(f"[{stat_name}] +{xp_gain} XP | {stat['xp']}/{stat['xp_limit']} XP")

        # Level up the stat if XP exceeds XP limit
        while stat["xp"] >= stat["xp_limit"]:
            stat["xp"] -= stat["xp_limit"]
            stat["level"] += 1
            print(f"[{stat_name}] leveled up! New level: {stat['level']}")

        # Add XP to main player XP
        self.data["xp"] += xp_gain
        print(f"[Player XP] +{xp_gain} XP | {self.data['xp']}/{self.data['xp_limit']} XP")

        # Level up player if main XP exceeds limit
        while self.data["xp"] >= self.data["xp_limit"]:
            self.data["xp"] -= self.data["xp_limit"]
            self.data["level"] += 1
            print(f"[Player] leveled up! New level: {self.data['level']}")

        self.save_profile()

        
        


    

if __name__ == "__main__":
    player = Player()
    if player.load_profile():
        print("Profile loaded:", player.data)
    else:
        print("No existing profile, creating new one.")
        player.set_profile("TestUser", "19", "Male")
        player.save_profile()
        print("Profile created:", player.data)

    # Test XP addition
    player.add_stat_xp("Knowledge", "aptitude questions 10")  # <-- try adding Strength XP

    print("Updated profile:", player.data)