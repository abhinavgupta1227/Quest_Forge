# main.py (Final Version with 3-Day To-Do List)
# -*- coding: utf-8 -*-
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

import customtkinter as ctk
from tkinter import messagebox
from player import Player
import copy
import os
import threading
from datetime import datetime

# Graceful imports...
try:
    from PIL import Image
    from customtkinter import CTkImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
try:
    import win32gui, win32con, ctypes
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.target_value = 0; self.current_value = 0; self.animation_speed = 0.12
        self.is_animating = False
    def animate_to(self, target_value):
        if not self.winfo_exists(): return
        self.target_value = target_value
        if not self.is_animating:
            self.is_animating = True; self._animate_step()
    def _animate_step(self):
        if not self.winfo_exists(): self.is_animating = False; return
        if abs(self.current_value - self.target_value) > 0.01:
            self.current_value += (self.target_value - self.current_value) * self.animation_speed
            self.set(self.current_value); self.after(16, self._animate_step)
        else:
            self.current_value = self.target_value; self.set(self.current_value); self.is_animating = False

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller; self.overrideredirect(True)
        width, height = 500, 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        transparent_color = '#00ff00' 
        self.attributes("-transparentcolor", transparent_color)
        self.configure(fg_color=transparent_color)
        self.lift(); self.attributes("-topmost", True)
        main_frame = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=30); main_frame.pack(fill="both", expand=True)
        if PIL_AVAILABLE:
            try:
                logo_path = os.path.join(SCRIPT_PATH, 'assets', 'logo.png')
                logo_image = Image.open(logo_path)
                logo_ctk = CTkImage(light_image=logo_image, dark_image=logo_image, size=(400, 400))
                logo_label = ctk.CTkLabel(main_frame, text="", image=logo_ctk, fg_color="transparent"); logo_label.pack(expand=True, pady=20)
            except Exception as e:
                print(f"Error loading splash screen logo: {e}")
        ctk.CTkLabel(main_frame, text="Loading...", font=("Arial", 16), text_color="gray60").pack(pady=(0, 30))
        self.after(5000, self.launch_main_app)
    def launch_main_app(self):
        self.destroy(); self.controller.setup_window(); self.controller.deiconify()

class SetupFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("#0d1117", "#0d1117"))
        self.controller = controller
        main_frame = ctk.CTkFrame(self, width=1000, height=700, corner_radius=30,fg_color=("gray8", "#1a1a1a"), border_width=3,border_color=("#3b82f6", "#60a5fa")); main_frame.place(relx=0.5, rely=0.5, anchor="center")
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); title_frame.pack(pady=40)
        ctk.CTkLabel(title_frame, text="⚔️ QUESTFORGE CHARACTER CREATION ⚔️", font=("Orbitron", 36, "bold"),text_color=("#3b82f6", "#60a5fa")).pack()
        form_frame = ctk.CTkFrame(main_frame, fg_color=("gray10", "#2a2a2a"), corner_radius=20, border_width=2,border_color=("#374151", "#4b5563")); form_frame.pack(pady=30, padx=60, fill="x")
        ctk.CTkLabel(form_frame, text="🏷️ Hero Name:", font=("Arial", 18, "bold"),text_color=("#e5e7eb", "#f3f4f6")).pack(pady=(30, 8))
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Enter your legendary name...", font=("Arial", 16), height=50,corner_radius=15); self.entry_name.pack(pady=5, padx=30, fill="x")
        ctk.CTkLabel(form_frame, text="🎂 Age:", font=("Arial", 18, "bold"),text_color=("#e5e7eb", "#f3f4f6")).pack(pady=(25, 8))
        self.entry_age = ctk.CTkEntry(form_frame, placeholder_text="How many years have you lived?", font=("Arial", 16), height=50,corner_radius=15); self.entry_age.pack(pady=5, padx=30, fill="x")
        ctk.CTkLabel(form_frame, text="⚧️ Gender:", font=("Arial", 18, "bold"),text_color=("#e5e7eb", "#f3f4f6")).pack(pady=(25, 8))
        self.entry_gender = ctk.CTkEntry(form_frame, placeholder_text="Male/Female/Other", font=("Arial", 16), height=50,corner_radius=15); self.entry_gender.pack(pady=5, padx=30, fill="x")
        ctk.CTkButton(form_frame, text="🚀 BEGIN QUEST", command=self.start_quest, font=("Orbitron", 20, "bold"),height=60, width=300,fg_color=("#059669", "#10b981"),hover_color=("#047857", "#059669"),corner_radius=30).pack(pady=50)
    def start_quest(self):
        name = self.entry_name.get().strip(); age = self.entry_age.get().strip(); gender = self.entry_gender.get().strip()
        if not name or not age or not gender: messagebox.showerror("⚠️ Missing Information", "Please complete all fields!"); return
        self.controller.player.set_profile(name, age, gender); self.controller.player.save_profile(); self.controller.show_frame("GreetingFrame")

class GreetingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("#0d1117", "#0d1117"))
        self.controller = controller
        main_frame = ctk.CTkFrame(self, width=900, height=600, corner_radius=25, fg_color=("gray8", "#1a1a1a"), border_width=3, border_color=("#3b82f6", "#60a5fa")); main_frame.place(relx=0.5, rely=0.5, anchor="center")
        if PIL_AVAILABLE:
            try:
                logo_path = os.path.join(SCRIPT_PATH, 'assets', 'logo.png')
                logo_image = Image.open(logo_path)
                logo_ctk = CTkImage(light_image=logo_image, dark_image=logo_image, size=(300, 300 * logo_image.height / logo_image.width))
                logo_label = ctk.CTkLabel(main_frame, text="", image=logo_ctk); logo_label.pack(pady=(40, 20))
            except Exception as e:
                print(f"Error loading greeting logo: {e}")
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); title_frame.pack(pady=10)
        self.greet_label = ctk.CTkLabel(title_frame, text="", font=("Orbitron", 42, "bold"), text_color=("#3b82f6", "#60a5fa")); self.greet_label.pack()
        ctk.CTkLabel(title_frame, text="🌟 Ready to Forge Your Destiny? 🌟", font=("Orbitron", 22), text_color=("#fbbf24", "#fde047")).pack(pady=15)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="🚀 START ADVENTURE", command=lambda: self.controller.show_frame("MainAppFrame"), font=("Orbitron", 16, "bold"), height=45, width=200, fg_color=("#059669", "#10b981"), hover_color=("#047857", "#059669"), corner_radius=25).pack(pady=10)
        ctk.CTkButton(button_frame, text="❌ Exit", command=self.controller.destroy, font=("Arial", 14), fg_color=("#dc2626", "#ef4444"), hover_color=("#b91c1c", "#dc2626"), width=100, height=35, corner_radius=20).pack(pady=10)
    def refresh_content(self):
        if self.controller.player.data['name']: self.greet_label.configure(text=f"⚔️ Welcome, {self.controller.player.data['name']}! ⚔️")

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("#0d1117", "#0d1117"))
        self.controller = controller; self.widgets_to_update = {}; self.built_task_frames = set()
        bottom_bar = ctk.CTkFrame(self, height=60, fg_color=("gray10", "#181818"), border_width=1, border_color=("gray15", "#2a2a2a")); bottom_bar.pack(side="bottom", fill="x", pady=(10, 0), padx=10)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent"); self.scrollable_frame.pack(side="top", fill="both", expand=True)
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        self.create_control_bar(bottom_bar)
        self.create_main_content(self.scrollable_frame)
        self.after(100, self.controller.update_ui)
    def create_control_bar(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent"); btn_frame.pack(expand=True, fill="both", pady=5, padx=20)
        ctk.CTkButton(btn_frame, text="⏪ Prev", command=lambda: self.controller._change_track(-1)).pack(side="left", padx=10)
        self.play_pause_btn = ctk.CTkButton(btn_frame, text="Pause ⏸️", command=self.controller._toggle_music); self.play_pause_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Next ⏩", command=lambda: self.controller._change_track(1)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Exit", command=self.controller.destroy, fg_color=("#dc2626", "#ef4444"), hover_color=("#b91c1c", "#dc2626")).pack(side="right", padx=10)
    def create_main_content(self, container):
        # ... (Profile and XP sections - no changes)
        profile_section = ctk.CTkFrame(container, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=2, border_color=("#3b82f6", "#60a5fa")); profile_section.pack(fill="x", pady=10, padx=10)
        player_info_frame = ctk.CTkFrame(profile_section, fg_color="transparent"); player_info_frame.pack(expand=True, fill="both", pady=10)
        # --- NEW: Player Level added to Profile ---
        level_display_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent")
        level_display_frame.pack(side="left", padx=(20, 15), pady=5)
        ctk.CTkLabel(level_display_frame, text="LEVEL", font=("Orbitron", 12, "bold"), text_color="gray60").pack()
        player_level_label = ctk.CTkLabel(level_display_frame, text="", font=("Orbitron", 40, "bold"), text_color=("#fbbf24", "#fde047"))
        player_level_label.pack()
        avatar_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent"); avatar_frame.pack(side="left", padx=(20, 15), pady=5)
        avatar_container = ctk.CTkFrame(avatar_frame, width=80, height=80, corner_radius=40, fg_color="transparent", border_width=3, border_color=("#fbbf24", "#fde047")); avatar_container.pack()
        avatar_bg = ctk.CTkFrame(avatar_container, width=68, height=68, corner_radius=34, fg_color=("#1e40af", "#3b82f6")); avatar_bg.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(avatar_bg, text="🧙‍♂️", font=("Arial", 40)).place(relx=0.5, rely=0.5, anchor="center")
        details_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent"); details_frame.pack(side="left", fill="x", expand=True, pady=5)
        name_label = ctk.CTkLabel(details_frame, text="", font=("Orbitron", 28, "bold"), text_color=("#3b82f6", "#60a5fa")); name_label.pack(anchor="center", pady=(5,0))
        info_label = ctk.CTkLabel(details_frame, text="", font=("Arial", 16), text_color=("#9ca3af", "#d1d5db")); info_label.pack(anchor="center", pady=2)
        self.widgets_to_update.update({'player_level_label': player_level_label, 'name_label': name_label, 'info_label': info_label})
        xp_section = ctk.CTkFrame(container, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=2, border_color=("#059669", "#10b981")); xp_section.pack(fill="x", pady=10, padx=10)
        xp_content = ctk.CTkFrame(xp_section, fg_color="transparent"); xp_content.pack(expand=True, fill="both", pady=10, padx=15)
        level_label = ctk.CTkLabel(xp_content, text="", font=("Orbitron", 24, "bold"), text_color=("#fbbf24", "#fde047")); level_label.pack(pady=5)
        xp_progress_frame = ctk.CTkFrame(xp_content, fg_color=("gray10", "#2a2a2a"), corner_radius=15, border_width=2, border_color=("#374151", "#4b5563")); xp_progress_frame.pack(fill="x")
        main_xp_bar = AnimatedProgressBar(xp_progress_frame, height=22, progress_color=("#059669", "#10b981"), fg_color=("#374151", "#4b5563"), corner_radius=11); main_xp_bar.pack(fill="x", pady=8, padx=12)
        xp_label = ctk.CTkLabel(xp_progress_frame, text="", font=("Arial", 14, "bold"), text_color=("#e5e7eb", "#f3f4f6")); xp_label.pack(pady=(0, 5))
        self.widgets_to_update.update({'main_level_label': level_label, 'main_xp_bar': main_xp_bar, 'main_xp_label': xp_label})
        
        top_content_section = ctk.CTkFrame(container, fg_color="transparent"); top_content_section.pack(fill="x", pady=10, padx=10)
        top_content_section.grid_columnconfigure(0, weight=6); top_content_section.grid_columnconfigure(1, weight=4)
        left_column = ctk.CTkFrame(top_content_section, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=1, border_color=("#374151", "#4b5563")); left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_column = ctk.CTkFrame(top_content_section, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=1, border_color=("#374151", "#4b5563")); right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(left_column, text="⚔️ STATISTICS ⚔️", font=("Orbitron", 18, "bold"), text_color=("#3b82f6", "#60a5fa")).pack(pady=15)
        for stat_name in self.controller.player.data['stats']: self._create_stat_dropdown(left_column, stat_name)
        
        ctk.CTkLabel(right_column, text="📋 DAILY HABITS 📋", font=("Orbitron", 18, "bold"), text_color=("#059669", "#10b981")).pack(pady=15)
        self._create_habit_tracker_ui(right_column)
        
        self._create_daily_todo_ui(container)
        self._create_boss_ui(container)

    def _create_boss_ui(self, parent):
        boss_section = ctk.CTkFrame(parent, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=1, border_color=("#374151", "#4b5563"))
        boss_section.pack(fill="x", pady=(20, 10), padx=10)
        
        grid_container = ctk.CTkFrame(boss_section, fg_color="transparent")
        grid_container.pack(fill="x", expand=True, padx=10, pady=10)
        grid_container.grid_columnconfigure(0, weight=1)
        grid_container.grid_columnconfigure(1, weight=1)

        # --- Daily Boss Frame ---
        daily_frame = ctk.CTkFrame(grid_container, fg_color=("gray12", "#222222"), border_width=1, border_color=("#c2410c", "#c2410c"))
        daily_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(daily_frame, text="🔥 DAILY BOSS 🔥", font=("Orbitron", 18, "bold"), text_color=("#fb923c", "#fb923c")).pack(pady=10)
        
        daily_boss_name = ctk.CTkLabel(daily_frame, text="Loading...", font=("Arial", 16, "bold"), wraplength=350)
        daily_boss_name.pack(pady=(5, 0), padx=10)
        daily_boss_obj = ctk.CTkLabel(daily_frame, text="Loading...", font=("Arial", 14), text_color="gray80", wraplength=350)
        daily_boss_obj.pack(pady=(0, 10), padx=10)
        daily_boss_reward = ctk.CTkLabel(daily_frame, text="+??? XP", font=("Arial", 14, "italic"), text_color=("#059669", "#10b981"))
        daily_boss_reward.pack(pady=5)
        daily_boss_btn = ctk.CTkButton(daily_frame, text="Complete Quest", fg_color="#c2410c", hover_color="#9a3412", command=self.controller.player.complete_daily_boss)
        daily_boss_btn.pack(pady=10)

        # --- Weekly Boss Frame ---
        weekly_frame = ctk.CTkFrame(grid_container, fg_color=("gray12", "#222222"), border_width=1, border_color=("#be185d", "#be185d"))
        weekly_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        ctk.CTkLabel(weekly_frame, text="💀 WEEKLY BOSS 💀", font=("Orbitron", 18, "bold"), text_color=("#f472b6", "#f472b6")).pack(pady=10)
        
        weekly_boss_name = ctk.CTkLabel(weekly_frame, text="Loading...", font=("Arial", 16, "bold"), wraplength=350)
        weekly_boss_name.pack(pady=(5, 0), padx=10)
        weekly_boss_obj = ctk.CTkLabel(weekly_frame, text="Loading...", font=("Arial", 14), text_color="gray80", wraplength=350)
        weekly_boss_obj.pack(pady=(0, 10), padx=10)
        weekly_boss_reward = ctk.CTkLabel(weekly_frame, text="+??? XP", font=("Arial", 14, "italic"), text_color=("#059669", "#10b981"))
        weekly_boss_reward.pack(pady=5)
        weekly_boss_btn = ctk.CTkButton(weekly_frame, text="Complete Quest", fg_color="#be185d", hover_color="#9d174d", command=self.controller.player.complete_weekly_boss)
        weekly_boss_btn.pack(pady=10)

        self.widgets_to_update['bosses'] = {
            'daily_name': daily_boss_name, 'daily_obj': daily_boss_obj, 'daily_reward': daily_boss_reward, 'daily_btn': daily_boss_btn,
            'weekly_name': weekly_boss_name, 'weekly_obj': weekly_boss_obj, 'weekly_reward': weekly_boss_reward, 'weekly_btn': weekly_boss_btn
        }

    def _on_mousewheel(self, event):
        # Multiplier for scroll speed (e.g., 3x faster)
        multiplier = 25
        self.scrollable_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120) * multiplier), "units")

    def _create_habit_tracker_ui(self, parent):
        habits_container = ctk.CTkFrame(parent, fg_color="transparent"); habits_container.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.widgets_to_update['habits'] = {}
        for habit_name, habit_data in self.controller.player.data.get("habits", {}).items():
            habit_frame = ctk.CTkFrame(habits_container, fg_color=("gray15", "#2a2a2a"), corner_radius=10); habit_frame.pack(fill="x", pady=5)
            checkbox_var = ctk.BooleanVar(value=habit_data.get("completed_today", False))
            checkbox = ctk.CTkCheckBox(habit_frame, text="", variable=checkbox_var, command=lambda name=habit_name: self._complete_habit_callback(name)); checkbox.pack(side="left", padx=10, pady=10)
            text_frame = ctk.CTkFrame(habit_frame, fg_color="transparent"); text_frame.pack(side="left", fill="x", expand=True, padx=(0,10), pady=10)
            ctk.CTkLabel(text_frame, text=f"{habit_name} (+{habit_data['xp_value']} XP)", font=("Arial", 14), anchor="w").pack(fill="x")
            streak_label = ctk.CTkLabel(text_frame, text=f"🔥 Streak: {habit_data['streak']}", font=("Arial", 12, "italic"), text_color="gray60", anchor="w"); streak_label.pack(fill="x")
            self.widgets_to_update['habits'][habit_name] = {'checkbox_var': checkbox_var, 'streak_label': streak_label}

    def _complete_habit_callback(self, habit_name):
        self.controller.player.complete_habit(habit_name); self.controller.update_ui()

    def _create_stat_dropdown(self, parent, stat_name):
        stat_data = self.controller.player.data['stats'][stat_name]; container = ctk.CTkFrame(parent, fg_color=("gray15", "#2a2a2a"), corner_radius=15, border_width=1, border_color=("#374151", "#4b5563")); container.pack(fill="x", padx=10, pady=6)
        header = ctk.CTkFrame(container, fg_color="transparent"); header.pack(fill="x", padx=8, pady=8)
        button = ctk.CTkButton(header, text="", font=("Orbitron", 16, "bold"), height=40, fg_color=("#1e40af", "#3b82f6"), hover_color=("#1d4ed8", "#2563eb"), corner_radius=12, anchor="w"); button.pack(fill="x")
        progress_frame = ctk.CTkFrame(header, fg_color=("gray20", "#333333"), corner_radius=10); progress_frame.pack(fill="x", pady=6)
        xp_bar = AnimatedProgressBar(progress_frame, height=10, progress_color=("#059669", "#10b981"), fg_color=("#374151", "#4b5563"), corner_radius=5); xp_bar.pack(fill="x", pady=6, padx=10)
        xp_label = ctk.CTkLabel(progress_frame, text="", font=("Arial", 12, "bold"), text_color=("#9ca3af", "#d1d5db")); xp_label.pack(pady=(0, 6))
        self.widgets_to_update[stat_name] = {'header_btn': button, 'xp_progress': xp_bar, 'xp_label': xp_label}
        tasks_frame = ctk.CTkFrame(container, fg_color=("gray10", "#1f1f1f"))
        button.configure(command=lambda s=stat_name, t_frame=tasks_frame: self._toggle_tasks(s, t_frame))

    def _toggle_tasks(self, stat_name, tasks_frame):
        if stat_name not in self.built_task_frames:
            stat_data = self.controller.player.data['stats'][stat_name]
            for task_name, xp_reward in stat_data['tasks'].items():
                ctk.CTkButton(tasks_frame,text=f"🎯 {task_name} (+{xp_reward} XP)",font=("Arial",14,"normal"),height=40,fg_color=("#065f46","#059669"),hover_color=("#047857","#10b981"),corner_radius=10,anchor="w",command=lambda s=stat_name, t=task_name: self._complete_task(s, t)).pack(fill="x", padx=8, pady=4)
            self.built_task_frames.add(stat_name)
        if tasks_frame.winfo_viewable(): tasks_frame.pack_forget()
        else: tasks_frame.pack(fill="x", padx=10, pady=(0, 10))

    def _complete_task(self, stat_name, task_name):
        if PYGAME_AVAILABLE:
            try:
                sound_path = os.path.join(SCRIPT_PATH, 'sounds', 'task_complete.mp3')
                pygame.mixer.Sound(sound_path).play()
            except Exception as e: print(f"Could not play task sound: {e}")
        old_data = copy.deepcopy(self.controller.player.data); status = self.controller.player.add_stat_xp(stat_name, task_name)
        if status: self._show_task_completion_popup(stat_name, task_name, status['xp_gained'], old_data)
        self.controller.update_ui()
    
    def _show_task_completion_popup(self, stat_name, task_name, xp_gained, old_data):
        popup = ctk.CTkToplevel(); popup.title("🎉 Task Completed!"); popup.transient(); popup.grab_set(); popup.attributes("-topmost", True)
        main_frame = ctk.CTkFrame(popup, fg_color=("gray8", "#1a1a1a"), corner_radius=25, border_width=3, border_color="#059669"); main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=f"Completed: {task_name}\n+ {xp_gained} XP", font=("Orbitron", 20, "bold")).pack(pady=20)
        if self.controller.player.data['level'] > old_data['level']: ctk.CTkLabel(main_frame, text="🎊 PLAYER LEVEL UP! 🎊", font=("Orbitron", 22, "bold"), text_color="#fbbf24").pack(pady=10)
        ctk.CTkButton(main_frame, text="Continue", command=popup.destroy).pack(pady=10)
    
    def _create_daily_todo_ui(self, parent):
        todo_section = ctk.CTkFrame(parent, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=1, border_color=("#374151", "#4b5563")); todo_section.pack(fill="x", pady=(20, 10), padx=10)
        ctk.CTkLabel(todo_section, text="🎯 DAILY QUESTS 🎯", font=("Orbitron", 18, "bold"), text_color=("#8b5cf6", "#a78bfa")).pack(pady=15)
        self.todo_day_frames = {}
        day_keys = {"previous": "Yesterday", "current": "Today", "next": "Tomorrow"}
        grid_container = ctk.CTkFrame(todo_section, fg_color="transparent"); grid_container.pack(fill="x", expand=True, padx=10, pady=10)
        for i, (day_key, day_name) in enumerate(day_keys.items()):
            grid_container.grid_columnconfigure(i, weight=1, minsize=220)
            day_frame = ctk.CTkFrame(grid_container, fg_color=("gray12", "#222222"), border_width=1, border_color=("gray20", "#333333")); day_frame.grid(row=0, column=i, sticky="nsew", padx=5)
            date_str = self.controller.player.data["daily_todos"][day_key]["date"]
            date_obj = datetime.fromisoformat(date_str)
            title_text = f"{day_name} ({date_obj.strftime('%d %b')})"
            ctk.CTkLabel(day_frame, text=title_text, font=("Arial", 14, "bold")).pack(pady=8)
            add_task_frame = ctk.CTkFrame(day_frame, fg_color="transparent"); add_task_frame.pack(fill="x", padx=4, pady=2)
            entry = ctk.CTkEntry(add_task_frame, placeholder_text="New Quest..."); entry.pack(side="left", fill="x", expand=True)
            add_button = ctk.CTkButton(add_task_frame, text="+", width=28, command=lambda d=day_key, e=entry: self._add_todo_callback(d, e)); add_button.pack(side="left", padx=(4,0))
            tasks_container = ctk.CTkScrollableFrame(day_frame, fg_color=("gray10", "#1a1a1a")); tasks_container.pack(fill="both", expand=True, padx=4, pady=4)
            self.todo_day_frames[day_key] = tasks_container

    def _add_todo_callback(self, day_key, entry_widget):
        task_text = entry_widget.get().strip()
        if task_text:
            self.controller.player.add_todo(day_key, task_text)
            entry_widget.delete(0, 'end'); self.controller.update_ui()
    
    def _toggle_todo_callback(self, day_key, task_index):
        self.controller.player.toggle_todo_status(day_key, task_index); self.controller.update_ui()

    def _delete_todo_callback(self, day_key, task_index):
        self.controller.player.delete_todo(day_key, task_index); self.controller.update_ui()

    def update_ui(self, p_data):
        if 'name_label' in self.widgets_to_update and self.widgets_to_update['name_label'].winfo_exists():
            self.widgets_to_update['player_level_label'].configure(text=f"{p_data['level']}")
            self.widgets_to_update['name_label'].configure(text=f"⚔️ {p_data['name']} ⚔️")
            self.widgets_to_update['info_label'].configure(text=f"🎂 Age: {p_data['age']} • ⚧️ Gender: {p_data['gender']}")
            self.widgets_to_update['main_level_label'].configure(text=f"🏆 LEVEL {p_data['level']} LEGENDARY HERO 🏆")
            xp_p=(p_data['xp']/p_data['xp_limit'])*100 if p_data['xp_limit']>0 else 0
            self.widgets_to_update['main_xp_label'].configure(text=f"💫 {p_data['xp']:,}/{p_data['xp_limit']:,} XP ({xp_p:.1f}%)")
            self.widgets_to_update['main_xp_bar'].animate_to(p_data['xp']/p_data['xp_limit'] if p_data['xp_limit']>0 else 0)
        for stat_name,stat_data in p_data['stats'].items():
            if stat_name in self.widgets_to_update and self.widgets_to_update[stat_name]['header_btn'].winfo_exists():
                w=self.widgets_to_update[stat_name]
                w['header_btn'].configure(text=f"⚔️ {stat_name} - Level {stat_data['level']}")
                xp_p=(stat_data['xp']/stat_data['xp_limit'])*100 if stat_data['xp_limit']>0 else 0
                w['xp_label'].configure(text=f"💫 {stat_data['xp']:,}/{stat_data['xp_limit']:,} XP ({xp_p:.1f}%)")
                w['xp_progress'].animate_to(stat_data['xp']/stat_data['xp_limit'] if stat_data['xp_limit']>0 else 0)
        if 'habits' in self.widgets_to_update:
            for habit_name, widgets in self.widgets_to_update['habits'].items():
                if habit_name in p_data['habits']:
                    habit_data = p_data['habits'][habit_name]
                    widgets['checkbox_var'].set(habit_data['completed_today'])
                    widgets['streak_label'].configure(text=f"🔥 Streak: {habit_data['streak']}")
        
        if hasattr(self, 'todo_day_frames'):
            for day_key, container in self.todo_day_frames.items():
                for widget in container.winfo_children(): widget.destroy()
                if day_key in p_data.get('daily_todos', {}):
                    for i, task_obj in enumerate(p_data['daily_todos'][day_key]['tasks']):
                        task_frame = ctk.CTkFrame(container, fg_color="transparent"); task_frame.pack(fill="x", pady=3)
                        task_frame.grid_columnconfigure(0, weight=0); task_frame.grid_columnconfigure(1, weight=1); task_frame.grid_columnconfigure(2, weight=0)

                        task_var = ctk.BooleanVar(value=task_obj['done'])
                        task_check = ctk.CTkCheckBox(task_frame, text="", variable=task_var, command=lambda d=day_key, idx=i: self._toggle_todo_callback(d, idx))
                        task_check.grid(row=0, column=0, sticky="w", padx=(0, 5))
                        
                        wraplength = container.winfo_reqwidth() - 80
                        task_label = ctk.CTkLabel(task_frame, text=task_obj['task'], anchor="w", wraplength=wraplength, justify="left")
                        if task_obj['done']: task_label.configure(font=("Arial", 12, "overstrike"), text_color="gray50")
                        else: task_label.configure(font=("Arial", 12))
                        task_label.grid(row=0, column=1, sticky="ew")

                        delete_btn = ctk.CTkButton(task_frame, text="🗑️", width=28, fg_color="transparent", hover_color="#552222", command=lambda d=day_key, idx=i: self._delete_todo_callback(d, idx))
                        delete_btn.grid(row=0, column=2, sticky="e", padx=(5,0))
                
        if 'bosses' in self.widgets_to_update:
            # Daily Boss
            if p_data.get('daily_boss'):
                boss = p_data['daily_boss']
                widgets = self.widgets_to_update['bosses']
                widgets['daily_name'].configure(text=boss['name'])
                widgets['daily_obj'].configure(text=boss['objective'])
                widgets['daily_reward'].configure(text=f"⚔️ +{boss['xp_reward']:,} XP ⚔️")
                if boss['is_defeated']:
                    widgets['daily_btn'].configure(text="Defeated ✅", state="disabled", fg_color="gray30")
                else:
                    widgets['daily_btn'].configure(text="Complete Quest", state="normal", fg_color="#c2410c")

            # Weekly Boss
            if p_data.get('weekly_boss'):
                boss = p_data['weekly_boss']
                widgets = self.widgets_to_update['bosses']
                widgets['weekly_name'].configure(text=boss['name'])
                widgets['weekly_obj'].configure(text=boss['objective'])
                widgets['weekly_reward'].configure(text=f"👑 +{boss['xp_reward']:,} XP 👑")
                if boss['is_defeated']:
                    widgets['weekly_btn'].configure(text="Defeated ✅", state="disabled", fg_color="gray30")
                else:
                    widgets['weekly_btn'].configure(text="Complete Quest", state="normal", fg_color="#be185d")

            

class QuestForgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuestForge"); self.withdraw()
        self.player = Player()
        self.profile_loaded = self.player.load_profile()
        if self.profile_loaded:
            self.player.handle_daily_reset()
            self.player.handle_weekly_reset()
        
        self.playlist = ["ambient_1.mp3", "ambient_2.mp3", "ambient_3.mp3"]
        self.current_track_index, self.music_is_paused = 0, False
        self.click_sound = None
        if PYGAME_AVAILABLE: self._initialize_audio()
        self.bind("<Button-1>", self._play_click_sound)

        container = ctk.CTkFrame(self, fg_color="transparent"); container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (SetupFrame, GreetingFrame, MainAppFrame):
            frame = F(container, self); self.frames[F.__name__] = frame; frame.grid(row=0, column=0, sticky="nsew")
    
    def setup_window(self):
        self.after(0, self._setup_window_task)
    def _setup_window_task(self):
        if IS_WINDOWS:
            try:
                icon_path = os.path.join(SCRIPT_PATH, 'assets', 'logo.ico')
                self.iconbitmap(icon_path)
            except Exception as e: print(f"Icon Error: {e}")
        self.geometry("1600x900")
        self.after(50, self.maximize_window)
        if self.profile_loaded: self.show_frame("GreetingFrame")
        else: self.show_frame("SetupFrame")

    def maximize_window(self):
        try:
            if IS_WINDOWS: self.state('zoomed')
        except Exception as e: print(f"Maximize Error: {e}")
    
    def _initialize_audio(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            click_sound_path = os.path.join(SCRIPT_PATH, 'sounds', 'click_sound.mp3')
            self.click_sound = pygame.mixer.Sound(click_sound_path)
            self.click_sound.set_volume(0.4)
            music_thread = threading.Thread(target=self._play_music, daemon=True); music_thread.start()
        except Exception as e: print(f"Audio Init Error: {e}")

    def _play_click_sound(self, event=None):
        if self.click_sound:
            self.click_sound.play()

    def _play_music(self):
        if not self.playlist: return
        try:
            track_name = self.playlist[self.current_track_index]
            music_path = os.path.join(SCRIPT_PATH, 'sounds', track_name)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.2); pygame.mixer.music.play()
            if self.music_is_paused: pygame.mixer.music.pause()
        except Exception as e: print(f"Music Play Error: {e}")
    
    def _change_track(self, direction):
        if not self.playlist: return
        self.current_track_index = (self.current_track_index + direction) % len(self.playlist)
        self._play_music()

    def _toggle_music(self):
        btn = self.frames["MainAppFrame"].play_pause_btn
        if self.music_is_paused: pygame.mixer.music.unpause(); self.music_is_paused = False; btn.configure(text="Pause ⏸️")
        else: pygame.mixer.music.pause(); self.music_is_paused = True; btn.configure(text="Play ▶️")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "GreetingFrame": frame.refresh_content()
        frame.tkraise()
    
    def update_ui(self):
        if "MainAppFrame" in self.frames and self.frames["MainAppFrame"].winfo_exists():
            self.frames["MainAppFrame"].update_ui(self.player.data)

if __name__ == "__main__":
    if IS_WINDOWS:
        try:
            myappid = 'mycompany.questforge.1.0'; ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception: pass
    
    app = QuestForgeApp()
    splash = SplashScreen(app)
    app.mainloop()