# player.py (Final Version)
import json
import os
import math
from datetime import date, timedelta

# --- NEW, ROBUST SAVE PATH ---
# This finds the user's AppData\Roaming folder on Windows and creates a dedicated folder for our app's save data.
# This ensures every user gets their own separate save file in a persistent location.
APP_DATA_PATH = os.getenv('APPDATA') or os.path.expanduser('~')
SAVE_DIR = os.path.join(APP_DATA_PATH, 'QuestForge', 'data')
PROFILE_PATH = os.path.join(SAVE_DIR, 'player_profile.json')


DAILY_BOSS_BLUEPRINT = [
    {"name": "The Slumbering Giant", "objective": "Get 7-8 hours of quality sleep.", "xp_reward": 500},
    {"name": "The Gluttony Beast", "objective": "Go a full day without junk food or processed sugar.", "xp_reward": 400},
    {"name": "The Iron Golem", "objective": "Complete any 3 Strength tasks.", "xp_reward": 600},
    {"name": "The Sage's Challenge", "objective": "Read 20 pages of a non-fiction book.", "xp_reward": 450}
]

WEEKLY_BOSS_BLUEPRINT = [
    {"name": "The Hydra of Neglect", "objective": "Reconnect with 3 old friends you haven't spoken to this month.", "xp_reward": 2000},
    {"name": "The Titan of Comfort", "objective": "Do something that is significantly outside of your comfort zone.", "xp_reward": 2500},
    {"name": "The Dragon of Hoarding", "objective": "Declutter a significant area of your room or workspace.", "xp_reward": 1500}
]

HABIT_BLUEPRINTS = {
    "Drink 8 glasses of water": {"xp_value": 20, "penalty": -15},
    "Read for 15 minutes":      {"xp_value": 30, "penalty": -20},
    "Meditate for 10 minutes":  {"xp_value": 50, "penalty": -25},
    "Go for a 20-minute walk":  {"xp_value": 40, "penalty": -20},
}

class Player:
    def __init__(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        self.data = {
            "name": "", "age": "", "gender": "", "level": 1,
            "xp": 0, "xp_limit": 10000,
            "last_login_date": "2000-01-01",
            "current_week": "2000-W01",
            "stats": {
                "Strength": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "0xp task for refresh": 0, "Daily gym": 150, "Hit a new PR": 600, "Deadhang till failure": 200,
                    "Pushups till failure": 200, "Squats till failure": 200, "60 seconds plank": 100, "Pull-ups till failure": 200,
                    "Perform farmer's-walk with heavy weights": 300, "150kg deadlift": 400, "180kg deadlift": 700,
                    "Grip-strength exercise": 200, "knuckle pushups till failure": 300, "Core-strengthening exercise": 350
                }},
                "Knowledge": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Read 10 pages of a book": 150, "Studying BCA subject for 1hr": 200, "aptitude questions 10": 400,
                    "research latest tech": 200, "Practice new langauge": 600, "session of GK": 300, "10 minutes vocabulary": 300,
                    "Listen to an informative podcast episode.": 300, "learn a new skill": 900, "complete a lesson on an online course": 200,
                    "1 hr revision of a subject": 400
                }},
                "Relationships": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Call a friend": 100, "Spend time with family": 200, "Make a new friend": 600, "Help someone in need": 400,
                    "Attend a social event": 300, "Do something for your loved ones": 400, "Send a thoughtful message/compliment": 150,
                    "Plan a get-together": 300, "Reconnect with an old friend": 250, "Practice active listening": 100
                }},
                "Stamina": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Half an hour of inclined walking": 250, "Jogging for 10 minutes without stopping": 400, "Complete a HIIT workout": 550,
                    "3 sets of sprints" : 600, "cardio session while breathing through the nose": 300, "Play any sport for an hour": 500,
                    "Practice jumping ropes": 350
                }},
                "Mindfulness": {"level" : 1, "xp" : 0, "xp_limit": 1000, "tasks" : {
                    "Complete a 20-minute guided meditation": 200, "Practice breath-hold for 80seconds": 400,
                    "Practice inhale-hold-exhale-hold for 10 minutes": 400, "Write down 3 things you are grateful for today": 200,
                    "Write a journal reflecting your thoughts": 350, "20 minutes mindfull meditation": 300,
                    "1 hr without technology just thinking": 600, "20 minutes mindful observation of your surroundings": 400,
                    "Go for a peaceful ride with no music": 500, 
                }},
                "Reflexes": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Play a reaction-time game online (e.g., Human Benchmark)": 200, "Solve a Rubik's Cube": 400,
                    "Practice throwing and catching a ball": 300, "Typing speed test": 200,
                    "Practice catching something unexpectedly thrown to you": 500, "close range badminton" : 500,
                    "Game with target practice": 300, "Throw a ball at a target" : 400, "20 minutes of Brainscale": 340
                }},
                "Communication": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Practice active listening in a conversation without planning your reply": 200,
                    "Engage in a 10-minute conversation with someone you don't know well": 400, "Record speaking in hindi/ english for 5 minutes": 300,
                    "Practice public speaking in front of a mirror": 500, "Practice storytelling": 300,
                    "Practice speech exercises for clarity and pronunciation": 400, "Practice summarizing a complex topic in simple terms": 350,
                    "Give a thoughtful feedback to someone": 250, "Practice humor": 300, "Speak publicly in  group setting": 600
                }},
                "Health": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Drink 3 litres of water daily": 300, "Get 7 hrs of sleep": 400, "Eat atleast 3 sources of protein in a day": 500,
                    "Eat a fruit": 200, "Avoid junk food and sugar for a day": 300, "Session of stretching, mobility, and flexibility exercises": 400,
                    "wake up early": 300, "Take the vitamins and supplements": 300, "10K steps a day": 300, "Skin/hair care routine": 500
                }},
                "Creativity": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Work on a video": 300, "Practice singing for 30 minutes": 400, "Play instruments for 30 minutes" : 400,
                    "Brainstorm ideas for a new project": 500, "Cook something new" : 400, "Script a video" : 400,
                    "Post on social media" : 400, "Color grade a video/photo": 350, "Record a creative video": 600,
                    "Try new haircut/clothing/style": 600
                }},
                "Finance": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Find new stocks": 230, "watch a video on finance": 200, "Track your expenses for a week": 500,
                    "Freelance something": 900, "Find good mutual funds": 350, "Brainstorm new business ideas": 400, "Earn money!!!!": 1000
                }}
            },
            "habits": {},
            "daily_todos": {
                "previous": {"date": yesterday.isoformat(), "tasks": []},
                "current":  {"date": today.isoformat(), "tasks": []},
                "next":     {"date": tomorrow.isoformat(), "tasks": []}
            }
        }
        for habit_name, props in HABIT_BLUEPRINTS.items():
            self.data["habits"][habit_name] = {
                "xp_value": props["xp_value"], "penalty": props["penalty"],
                "streak": 0, "completed_today": False
            }

    def set_profile(self, name, age, gender):
        self.data["name"] = name; self.data["age"] = age; self.data["gender"] = gender
        self.data["last_login_date"] = date.today().isoformat()

    def save_profile(self):
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def load_profile(self):
        if not os.path.exists(PROFILE_PATH): return False
        with open(PROFILE_PATH, "r", encoding="utf-8") as f: self.data = json.load(f)
        if "habits" not in self.data: self.data["habits"] = {}
        for habit_name, props in HABIT_BLUEPRINTS.items():
            if habit_name not in self.data["habits"]:
                self.data["habits"][habit_name] = {
                    "xp_value": props["xp_value"], "penalty": props["penalty"],
                    "streak": 0, "completed_today": False
                }
        if "daily_todos" not in self.data:
            today = date.today()
            self.data["daily_todos"] = {
                "previous": {"date": (today - timedelta(days=1)).isoformat(), "tasks": []},
                "current":  {"date": today.isoformat(), "tasks": []},
                "next":     {"date": (today + timedelta(days=1)).isoformat(), "tasks": []}
            }
        return True

    def add_xp(self, amount):
        self.data["xp"] = self.data.get("xp", 0) + amount
        leveled_up = False
        while self.data["xp"] >= self.data["xp_limit"]:
            self.data["xp"] -= self.data["xp_limit"]; self.data["level"] += 1
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
            stat["xp"] -= stat["xp_limit"]; stat["level"] += 1
            stat["xp_limit"] = math.floor(stat["xp_limit"] * 1.20)
            stat_leveled_up = True
        player_leveled_up = self.add_xp(xp_gain)
        self.save_profile()
        return {"stat_leveled_up": stat_leveled_up, "player_leveled_up": player_leveled_up, "xp_gained": xp_gain}

    def handle_daily_reset(self):
        today = date.today()
        today_str = today.isoformat()
        last_login_str = self.data.get("last_login_date", "2000-01-01")
        if today_str > last_login_str:
            print("🌅 New day detected! Resetting...")
            for habit_data in self.data["habits"].values():
                if not habit_data["completed_today"]:
                    self.add_xp(habit_data["penalty"]); habit_data["streak"] = 0
                habit_data["completed_today"] = False
            
            self.data["daily_todos"]["previous"] = self.data["daily_todos"]["current"]
            self.data["daily_todos"]["current"] = self.data["daily_todos"]["next"]
            self.data["daily_todos"]["next"] = {"date": (today + timedelta(days=1)).isoformat(), "tasks": []}
            self.data["daily_todos"]["previous"]["date"] = (today - timedelta(days=1)).isoformat()
            self.data["daily_todos"]["current"]["date"] = today_str

            self.generate_daily_boss() # <--- ADD THIS LINE


            self.data["last_login_date"] = today_str
            self.save_profile()
            return True
        return False
    
    # --- ADD THIS ENTIRE NEW METHOD INSIDE THE PLAYER CLASS ---
    def handle_weekly_reset(self):
        """Checks if it's a new week and generates a new weekly boss."""
        today = date.today()
        # %W treats Monday as the first day of the week (00-53)
        current_week_str = today.strftime("%Y-W%W")
        last_week_str = self.data.get("current_week", "2000-W01")

        if current_week_str > last_week_str:
            print("📅 New week detected! Generating new Weekly Boss.")
            if 'generate_weekly_boss' in dir(self):
                self.generate_weekly_boss()
            
            self.data["current_week"] = current_week_str
            self.save_profile()
            return True
        return False

    def complete_habit(self, habit_name):
        if habit_name not in self.data["habits"]: return None
        habit = self.data["habits"][habit_name]
        if not habit["completed_today"]:
            habit["completed_today"] = True; habit["streak"] += 1
            self.add_xp(habit["xp_value"]); self.save_profile()
            return habit
        return None

    def add_todo(self, day_key, task_description):
        if day_key in self.data["daily_todos"]:
            self.data["daily_todos"][day_key]["tasks"].append({"task": task_description, "done": False})
            self.save_profile(); return True
        return False

    def toggle_todo_status(self, day_key, task_index):
        XP_PER_TODO = 80
        if day_key in self.data["daily_todos"] and 0 <= task_index < len(self.data["daily_todos"][day_key]["tasks"]):
            task = self.data["daily_todos"][day_key]["tasks"][task_index]
            task["done"] = not task["done"]
            self.add_xp(XP_PER_TODO if task["done"] else -XP_PER_TODO)
            self.save_profile(); return True
        return False
        
    def delete_todo(self, day_key, task_index):
        XP_PER_TODO = 80
        if day_key in self.data["daily_todos"] and 0 <= task_index < len(self.data["daily_todos"][day_key]["tasks"]):
            task = self.data["daily_todos"][day_key]["tasks"].pop(task_index)
            if task["done"]: self.add_xp(-XP_PER_TODO)
            self.save_profile(); return True
        return False
    
    # --- ADD THESE 4 NEW METHODS INSIDE THE PLAYER CLASS ---

    def generate_daily_boss(self):
        import random
        boss_data = random.choice(DAILY_BOSS_BLUEPRINT)
        self.data['daily_boss'] = {
            "name": boss_data["name"],
            "objective": boss_data["objective"],
            "xp_reward": boss_data["xp_reward"],
            "is_defeated": False
        }

    def generate_weekly_boss(self):
        import random
        boss_data = random.choice(WEEKLY_BOSS_BLUEPRINT)
        self.data['weekly_boss'] = {
            "name": boss_data["name"],
            "objective": boss_data["objective"],
            "xp_reward": boss_data["xp_reward"],
            "is_defeated": False
        }

    def complete_daily_boss(self):
        if self.data.get('daily_boss') and not self.data['daily_boss']['is_defeated']:
            self.add_xp(self.data['daily_boss']['xp_reward'])
            self.data['daily_boss']['is_defeated'] = True
            self.save_profile()

    def complete_weekly_boss(self):
        if self.data.get('weekly_boss') and not self.data['weekly_boss']['is_defeated']:
            self.add_xp(self.data['weekly_boss']['xp_reward'])
            self.data['weekly_boss']['is_defeated'] = True
            self.save_profile()