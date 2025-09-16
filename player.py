# player.py 
import json
import os
import math
from datetime import date, timedelta
import random


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(SCRIPT_DIR, "data", "player_profile.json")

APP_DATA_PATH = os.getenv('APPDATA') or os.path.expanduser('~')
SAVE_DIR = os.path.join(APP_DATA_PATH, 'QuestForge', 'data')
PROFILE_PATH = os.path.join(SAVE_DIR, 'player_profile.json')

# --- Blueprints for Habits and Weekly Bosses ---
HABIT_BLUEPRINTS = {
    "Drink 4 litres of water": {"xp_value": 200, "penalty": -100},
    "Read for a book for 15 minutes":      {"xp_value": 250, "penalty": -100},
    "Meditate for 10 minutes":  {"xp_value": 200, "penalty": -100},
    "20 minutes Cardio":  {"xp_value": 200, "penalty": -100},
    "Login to Quest Forge":  {"xp_value": 100, "penalty": -50},
    "Clean bed":{"xp_value": 150, "penalty": -75},
    "Plan the day": {"xp_value": 200, "penalty": -60},
    "Morning warm water": {"xp_value": 200, "penalty": -100},
    "Go to gym": {"xp_value": 150, "penalty": -100},
    "Avoid sugar and junk food": {"xp_value": 200, "penalty": -100},
    "Take vitamins and supplements": {"xp_value": 200, "penalty": -70},
    "Eat 3 sources of protein": {"xp_value": 350, "penalty": -150},
}

WEEKLY_BOSS_BLUEPRINT = [
    {"name": "The Dragon of Hoarding", "primary objective": "Declutter a significant area of your room or workspace.","stat objective": "Level up Mindfulness ", "xp_reward": 1500},
    {"name": "The Juggernaut of Sloth", "primary objective": "Complete a 'Triathlon of Tenacity' over the week: perform a total of 100 push-ups, run for a total of 5km, and hold a plank for a cumulative 5 minutes.","stat objective": "Level up Stamina and strength", "xp_reward": 1500},
    {"name": "The Golem of Unfinished Projects", "primary objective": "Choose one creative project (a video, art, story, etc.) and take it from idea to a finished 'version 1.0' this week.", "stat objective": "Level up Creativity & Mindfulness once each.", "xp_reward": 2000},
    {"name": "The Oracle of Obscurity", "primary objective": "The 'Deep Dive' challenge: Pick one complex topic, research it throughout the week, and write a one-page summary at the end.", "stat objective": "Level up Knowledge & Communication once each.", "xp_reward": 2200},
    {"name": "The Phantom of Isolation", "primary objective": "Act as an 'Ambassador.' Take the full initiative to plan, organize, and host a hangout or activity with friends or family.", "stat objective": "Level up Relationship & Communication once each.", "xp_reward": 2000},
    {"name": "The Mountain's Spirit", "primary objective": "Go on a long hike (2+ hours) or complete two separate 45-minute high-intensity cardio sessions.", "stat objective": "Level up Stamina & Health once each.", "xp_reward": 1800},
    {"name": "The Echo Chamber Wraith", "primary objective": "Create and publish a piece of content (e.g., a blog post, a 3-minute video, or a presentation).", "stat objective": "Level up Creativity & Communication once each.", "xp_reward": 1900},
    {"name": "The Sphinx of Silence", "primary objective": "Prepare and record yourself giving a 5-minute presentation on any topic you're passionate about. The goal is clarity and confidence.", "stat objective": "Level up Communication & Knowledge once each.", "xp_reward": 1800},
    {"name": "The Chaos Elemental", "primary objective": "Complete a 24-hour 'Digital Detox' with no social media or mindless entertainment (YouTube, Netflix, etc.).", "stat objective": "Level up Mindfulness & Health once each.", "xp_reward": 2500},
    {"name": "The Chrono-Mage's Curse", "primary objective": "Achieve a 'Flow State.' Dedicate two separate 90-minute blocks of deep, uninterrupted focus to a skill requiring fast reactions.", "stat objective": "Level up Reflexes & Mindfulness once each.", "xp_reward": 1700},
    {"name": "The Dragon of Debt", "primary objective": "Become a 'Financial Architect.' Perform a full audit of last month's spending and create a detailed budget for the next month.", "stat objective": "Level up Earning & Knowledge once each.", "xp_reward": 2000},
    {"name": "The Librarian's Ghost", "primary objective": "Finish reading an entire book this week (fiction or non-fiction).", "stat objective": "Level up Knowledge & Mindfulness once each.", "xp_reward": 1500},
    {"name": "The Gilded Golem", "primary objective": "Launch a 'Micro-Venture.' Spend 5 hours developing a marketable skill and send out three proposals or applications.", "stat objective": "Level up Earning & Creativity once each.", "xp_reward": 2200},
    {"name": "The Artisan's Block", "primary objective": "Create something physical with your hands (e.g., cook a complex new recipe, build a small piece of furniture, or complete a craft).", "stat objective": "Level up Creativity & Strength once each.", "xp_reward": 1600},
    {"name": "The Doppelgänger of Distraction", "primary objective": "Perform a 'Digital Reset': Unfollow 50+ unhelpful social media accounts and unsubscribe from 10+ email newsletters.", "stat objective": "Level up Mindfulness & Health once each.", "xp_reward": 1600},
    {"name": "The Behemoth of Barriers", "primary objective": "Attempt a new Personal Record (PR) in a major physical exercise. You must attempt it at least twice during the week.", "stat objective": "Level up Strength & Mindfulness once each.", "xp_reward": 2100},
    {"name": "The Mimic of Mediocrity", "primary objective": "The 'Journeyman's Trial.' Choose one skill you are a beginner at and complete 5 hours of deliberate practice.", "stat objective": "Level up Reflexes & Knowledge once each.", "xp_reward": 1800},
    {"name": "The Leviathan of Logistics", "primary objective": "Meal prep your lunches for the entire work/school week (e.g., 5 days). This includes planning, shopping, and cooking.", "stat objective": "Level up Health & Earning once each.", "xp_reward": 1600},
    {"name": "The Architect of Anarchy", "primary objective": "Plan your entire next week in detail (workouts, study, social, etc.) and follow the schedule with at least 80'%' accuracy.", "stat objective": "Level up Mindfulness & Stamina once each.", "xp_reward": 1700},
    {"name": "The Whisperwind of Rumor", "primary objective": "Have a deep, one-on-one conversation where your primary goal is to listen. For 30 minutes, do not talk about yourself unless asked.", "stat objective": "Level up Communication & Relationship once each.", "xp_reward": 1800},
    {"name": "The Empathy Vampire", "primary objective": "Do three unsolicited, significant acts of kindness for three different people.", "stat objective": "Level up Relationship & Health once each.", "xp_reward": 1900},
    {"name": "The Quick-Sand of Monotony", "primary objective": "The 'Explorer's Challenge.' Do three things you have never done before this week (can be small or large).", "stat objective": "Level up Stamina & Reflexes once each.", "xp_reward": 1500}
]



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
                    "0xp task for refresh": 0, "Daily gym": 150, "Hit a new PR": 600, "Deadhang till failure": 200, "Wall punch practice": 200, "Neck exercise": 200 ,"Pushups till failure": 200, "Squats till failure": 200, "60 seconds plank": 100, "Pull-ups till failure": 200, "Perform farmer's-walk with heavy weights": 300, "150kg deadlift": 400, "180kg deadlift": 700, "Grip-strength exercise": 200, "knuckle pushups till failure": 300, "Core-strengthening exercise": 350
                }},
                "Knowledge": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Read 10 pages of a book": 150, "Studying BCA subject for 1hr": 200, "aptitude questions 10": 400, "research latest tech": 200, "Practice new langauge": 600, "session of GK": 300, "10 minutes vocabulary": 300, "Listen to an informative podcast episode.": 300, "learn a new skill": 900, "complete a lesson on an online course": 200, "1 hr revision of a subject": 400
                }},
                "Relationships": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Call a friend": 100, "Spend time with family": 200, "Make a new friend": 600, "Help someone in need": 400, "Attend a social event": 300, "Do something for your loved ones": 400, "Send a thoughtful message/compliment": 150, "Plan a get-together": 300, "Reconnect with an old friend": 250, "Practice active listening": 100
                }},
                "Stamina": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Half an hour of inclined walking": 250, "Jogging for 10 minutes without stopping": 400, "Complete a HIIT workout": 550, "3 sets of sprints" : 600, "cardio session while breathing through the nose": 300, "Play any sport for an hour": 500, "Practice jumping ropes": 350
                }},
                "Mindfulness": {"level" : 1, "xp" : 0, "xp_limit": 1000, "tasks" : {
                    "Complete a 20-minute guided meditation": 200, "Practice breath-hold for 80seconds": 400, "Practice inhale-hold-exhale-hold for 10 minutes": 400, "Write down 3 things you are grateful for today": 200, "Write a journal reflecting your thoughts": 350, "20 minutes mindfull meditation": 300, "1 hr without technology just thinking": 600, "20 minutes mindful observation of your surroundings": 400, "Go for a peaceful ride with no music": 500
                }},
                "Reflexes": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Play a reaction-time game online (e.g., Human Benchmark)": 200, "Solve a Rubik's Cube": 400, "Practice throwing and catching a ball": 300, "Typing speed test": 200, "Practice catching something unexpectedly thrown to you": 500, "close range badminton" : 500, "Game with target practice": 300, "Throw a ball at a target" : 400, "20 minutes of Brainscale": 340
                }},
                "Communication": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Practice active listening in a conversation without planning your reply": 200, "Engage in a 10-minute conversation with someone you don't know well": 400, "Record speaking in hindi/ english for 5 minutes": 300, "Practice public speaking in front of a mirror": 500, "Practice storytelling": 300, "Practice speech exercises for clarity and pronunciation": 400, "Practice summarizing a complex topic in simple terms": 350, "Give a thoughtful feedback to someone": 250, "Practice humor": 300, "Speak publicly in  group setting": 600
                }},
                "Health": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Drink 3 litres of water daily": 300, "Get 7 hrs of sleep": 400, "Eat atleast 3 sources of protein in a day": 500, "Eat a fruit": 200, "Avoid junk food and sugar for a day": 300, "Session of stretching, mobility, and flexibility exercises": 400, "wake up early": 300, "Take the vitamins and supplements": 300, "10K steps a day": 300, "Skin/hair care routine": 500
                }},
                "Creativity": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Work on a video": 300, "Practice singing for 30 minutes": 400, "Play instruments for 30 minutes" : 400, "Brainstorm ideas for a new project": 500, "Cook something new" : 400, "Script a video" : 400, "Post on social media" : 400, "Color grade a video/photo": 350, "Record a creative video": 600, "Try new haircut/clothing/style": 600
                }},
                "Finance": {"level": 1, "xp": 0, "xp_limit": 1000, "tasks": {
                    "Find new stocks": 230, "watch a video on finance": 200, "Track your expenses for a week": 500, "Freelance something": 900, "Find good mutual funds": 350, "Brainstorm new business ideas": 400, "Earn money!!!!": 1000
                }}
            },
            "habits": {},
            "daily_todos": {
                "previous": {"date": yesterday.isoformat(), "tasks": []},
                "current":  {"date": today.isoformat(), "tasks": []},
                "next":     {"date": tomorrow.isoformat(), "tasks": []}
            },
            "daily_boss": {}, "weekly_boss": {}
        }
        for habit_name, props in HABIT_BLUEPRINTS.items():
            self.data["habits"][habit_name] = {"xp_value": props["xp_value"], "penalty": props["penalty"], "streak": 0, "completed_today": False,}

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
                self.data["habits"][habit_name] = {"xp_value": props["xp_value"], "penalty": props["penalty"], "streak": 0, "completed_today": False}
        if "daily_todos" not in self.data:
            today = date.today()
            self.data["daily_todos"] = {
                "previous": {"date": (today - timedelta(days=1)).isoformat(), "tasks": []},
                "current":  {"date": today.isoformat(), "tasks": []},
                "next":     {"date": (today + timedelta(days=1)).isoformat(), "tasks": []}
            }
        if "daily_boss" not in self.data: self.data["daily_boss"] = {}
        if "weekly_boss" not in self.data: self.data["weekly_boss"] = {}
        return True

    def add_xp(self, amount):
        self.data["xp"] = self.data.get("xp", 0) + amount; leveled_up = False
        while self.data["xp"] >= self.data["xp_limit"]:
            self.data["xp"] -= self.data["xp_limit"]; self.data["level"] += 1
            self.data["xp_limit"] = math.floor(self.data["xp_limit"] * 1)
            leveled_up = True
        return leveled_up

    def add_stat_xp(self, stat_name, task_name):
        if stat_name not in self.data["stats"]: return None
        stat = self.data["stats"][stat_name]
        if task_name not in stat["tasks"]: return None
        xp_gain = stat["tasks"][task_name]
        stat["xp"] += xp_gain; stat_leveled_up = False
        while stat["xp"] >= stat["xp_limit"]:
            stat["xp"] -= stat["xp_limit"]; stat["level"] += 1
            stat["xp_limit"] = math.floor(stat["xp_limit"] * 1.20)
            stat_leveled_up = True
        player_leveled_up = self.add_xp(xp_gain)
        self.save_profile()
        return {"stat_leveled_up": stat_leveled_up, "player_leveled_up": player_leveled_up, "xp_gained": xp_gain}

    def handle_daily_reset(self):
        today = date.today(); today_str = today.isoformat()
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
            self.generate_daily_boss()
            self.data["last_login_date"] = today_str
            self.save_profile()
            return True
        return False

    def handle_weekly_reset(self):
        today = date.today(); current_week_str = today.strftime("%Y-W%W")
        last_week_str = self.data.get("current_week", "2000-W01")
        if current_week_str > last_week_str:
            print("📅 New week detected! Generating new Weekly Boss.")
            self.generate_weekly_boss()
            self.data["current_week"] = current_week_str
            self.save_profile(); return True
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
    
    def generate_daily_boss(self):
        """Dynamically generates a daily boss from a random stat and task."""
        eligible_stats = {s: t['tasks'] for s, t in self.data['stats'].items() if t.get('tasks')}
        if not eligible_stats: return

        random_stat_name = random.choice(list(eligible_stats.keys()))
        tasks = eligible_stats[random_stat_name]
        
        eligible_tasks = {name: xp for name, xp in tasks.items() if xp > 0}
        if not eligible_tasks: 
            # If the chosen stat has no valid tasks, try again.
            self.generate_daily_boss()
            return

        random_task_name = random.choice(list(eligible_tasks.keys()))
        
        self.data['daily_boss'] = {
            "stat_name": random_stat_name,
            "task_name": random_task_name,
            "bonus_xp": 300,
            "is_defeated": False,
            "rerolls_left": 1
        }

    def reroll_daily_boss(self):
        """Uses a reroll charge to generate a new daily boss."""
        boss_data = self.data.get('daily_boss', {})
        if boss_data.get('rerolls_left', 0) > 0:
            boss_data['rerolls_left'] -= 1
            self.generate_daily_boss() 
            self.data['daily_boss']['rerolls_left'] = 0 # Ensure it's 0 after rerolling
            self.save_profile()
            return True
        return False
    
    def reroll_weekly_boss(self):
        if self.data['weekly_boss'].get('rerolls_left', 0) > 0:
            self.data['weekly_boss']['rerolls_left'] -= 1
            self.generate_weekly_boss()
            self.save_profile(); return True
        return False


    def complete_daily_boss(self):
        """Completes the daily boss quest, granting only the bonus XP."""
        boss = self.data.get('daily_boss')
        if boss and not boss.get('is_defeated', False):
            self.add_xp(boss['bonus_xp'])
            boss['is_defeated'] = True
            self.save_profile()
            return boss
        return None

    def generate_weekly_boss(self):
        boss_data = random.choice(WEEKLY_BOSS_BLUEPRINT)
        self.data['weekly_boss'] = {
            "name": boss_data["name"], "primary objective": boss_data["primary objective"], "stat objective": boss_data["stat objective"],
            "xp_reward": boss_data["xp_reward"], "is_defeated": False, "rerolls_left": 1
        }

    def complete_weekly_boss(self):
        boss = self.data.get('weekly_boss')
        if boss and not boss.get('is_defeated', False):
            self.add_xp(boss['xp_reward'])
            boss['is_defeated'] = True
            for stat in self.data['stats'].values():
                stat['xp'] += 100 
            self.save_profile(); return boss
        return None