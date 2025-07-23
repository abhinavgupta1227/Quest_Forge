# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

# main.py (Final Version with Corrected Indentation)
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from player import Player
import copy
import os
import threading

# --- Sound Libraries ---
from playsound import playsound
import pygame

# --- Windows-Specific Library for Maximizing ---
try:
    import win32gui
    import win32con
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

# Custom Animated Progress Bar
class AnimatedProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.target_value = 0
        self.current_value = 0
        self.animation_speed = 0.08

    def animate_to(self, target_value):
        self.target_value = target_value
        if not self.winfo_viewable():
            self.set(target_value)
            self.current_value = target_value
            return
        self._animate_step()

    def _animate_step(self):
        if abs(self.current_value - self.target_value) > 0.005:
            self.current_value += (self.target_value - self.current_value) * self.animation_speed
            self.set(self.current_value)
            self.after(16, self._animate_step)
        else:
            self.current_value = self.target_value
            self.set(self.current_value)

# In main.py, replace the existing QuestForgeApp class with this one.

class QuestForgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuestForge"); ctk.set_appearance_mode("dark")
        self.configure(fg_color=("#0d1117", "#0d1117"))

        # --- NEW: BIND THE GLOBAL CLICK EVENT ---
        # This tells the entire window to call _play_click_sound whenever
        # the left mouse button is clicked.
        self.bind("<Button-1>", self._play_click_sound)

        self.after(100, self.maximize_window)

        # --- Music and Sound ---
        self.playlist = ["ambient_1.mp3", "ambient_2.mp3", "ambient_3.mp3"]
        self.current_track_index = 0
        self._initialize_audio()
        
        # --- Player and UI Frame Setup ---
        self.player = Player()
        self.widgets_to_update = {}
        container = ctk.CTkFrame(self, fg_color="transparent"); container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (SetupFrame, GreetingFrame, MainAppFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame; frame.grid(row=0, column=0, sticky="nsew")
        if self.player.load_profile(): self.show_frame("GreetingFrame")
        else: self.show_frame("SetupFrame")

    def maximize_window(self):
        if IS_WINDOWS:
            try: win32gui.ShowWindow(self.winfo_id(), win32con.SW_MAXIMIZE)
            except Exception: self.state('zoomed')
        else: self.state('zoomed')

    # --- NEW: METHOD TO PLAY THE CLICK SOUND ---
    def _initialize_audio(self):
        """Initializes pygame mixer, loads sounds, and starts background music."""
        try:
            pygame.mixer.init()
            
            # --- NEW: Load the click sound and set its volume ---
            click_sound_path = os.path.join('Quest_forge', 'sounds', 'click_sound.mp3')
            self.click_sound = pygame.mixer.Sound(click_sound_path)
            # Set click volume to 40%. Adjust as needed.
            self.click_sound.set_volume(0.2)

            # Start background music in a thread
            music_thread = threading.Thread(target=self._play_music, daemon=True)
            music_thread.start()
        except Exception as e:
            print(f"Could not initialize audio: {e}")

    # --- UPDATED: This method now uses the pre-loaded sound ---
    def _play_click_sound(self, event=None):
        """Plays the pre-loaded click sound."""
        if self.click_sound:
            self.click_sound.play()

    def _play_music(self):
        if not self.playlist: return
        try:
            track_name = self.playlist[self.current_track_index]
            music_path = os.path.join('Quest_Forge','sounds', track_name)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.2) 
            pygame.mixer.music.play(loops=-1)
        except Exception as e: print(f"Could not play track {track_name}: {e}")
    
    def _change_track(self, direction):
        if not self.playlist: return
        pygame.mixer.music.stop()
        self.current_track_index += direction
        if self.current_track_index >= len(self.playlist):
            self.current_track_index = 0
        elif self.current_track_index < 0:
            self.current_track_index = len(self.playlist) - 1
        self._play_music()

    def show_frame(self, page_name):
        if page_name == "GreetingFrame": self.frames["GreetingFrame"].refresh_greeting()
        frame = self.frames[page_name]; frame.tkraise()

    def update_ui(self):
        p_data = self.player.data
        if 'main_level_label' in self.widgets_to_update:
            self.widgets_to_update['name_label'].configure(text=f"⚔️ {p_data['name']} ⚔️")
            self.widgets_to_update['info_label'].configure(text=f"🎂 Age: {p_data['age']} • ⚧️ Gender: {p_data['gender']}")
            self.widgets_to_update['main_level_label'].configure(text=f"🏆 LEVEL {p_data['level']} LEGENDARY HERO 🏆")
            xp_p = (p_data['xp']/p_data['xp_limit'])*100 if p_data['xp_limit']>0 else 0
            self.widgets_to_update['main_xp_label'].configure(text=f"💫 {p_data['xp']:,}/{p_data['xp_limit']:,} XP ({xp_p:.1f}%)")
            self.widgets_to_update['main_xp_bar'].animate_to(p_data['xp']/p_data['xp_limit'] if p_data['xp_limit']>0 else 0)
        
        for stat_name, stat_data in p_data['stats'].items():
            if stat_name in self.widgets_to_update:
                w = self.widgets_to_update[stat_name]
                w['header_btn'].configure(text=f"⚔️ {stat_name} - Level {stat_data['level']}")
                xp_p = (stat_data['xp']/stat_data['xp_limit'])*100 if stat_data['xp_limit']>0 else 0
                w['xp_label'].configure(text=f"💫 {stat_data['xp']:,}/{stat_data['xp_limit']:,} XP ({xp_p:.1f}%)")
                w['xp_progress'].animate_to(stat_data['xp']/stat_data['xp_limit'] if stat_data['xp_limit']>0 else 0)

# --- UI Frame Classes ---

class SetupFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("#0d1117", "#0d1117"))
        self.controller = controller

        main_frame = ctk.CTkFrame(self, width=1000, height=700, corner_radius=30, fg_color=("gray8", "#1a1a1a"), border_width=3, border_color=("#3b82f6", "#60a5fa"))
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=40)
        ctk.CTkLabel(title_frame, text="⚔️ QUESTFORGE CHARACTER CREATION ⚔️", font=("Orbitron", 36, "bold"), text_color=("#3b82f6", "#60a5fa")).pack()

        form_frame = ctk.CTkFrame(main_frame, fg_color=("gray10", "#2a2a2a"), corner_radius=20)
        form_frame.pack(pady=30, padx=60, fill="x")

        ctk.CTkLabel(form_frame, text="🏷️ Hero Name:", font=("Arial", 18, "bold")).pack(pady=(20, 5))
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Enter your legendary name...", height=50, corner_radius=15)
        self.entry_name.pack(pady=5, padx=30, fill="x")

        ctk.CTkLabel(form_frame, text="🎂 Age:", font=("Arial", 18, "bold")).pack(pady=(20, 5))
        self.entry_age = ctk.CTkEntry(form_frame, placeholder_text="How many years have you lived?", height=50, corner_radius=15)
        self.entry_age.pack(pady=5, padx=30, fill="x")

        ctk.CTkLabel(form_frame, text="⚧️ Gender:", font=("Arial", 18, "bold")).pack(pady=(20, 5))
        self.entry_gender = ctk.CTkEntry(form_frame, placeholder_text="Male/Female/Other", height=50, corner_radius=15)
        self.entry_gender.pack(pady=5, padx=30, fill="x")

        start_btn = ctk.CTkButton(form_frame, text="🚀 BEGIN QUEST", command=self.start_quest, font=("Orbitron", 20, "bold"), height=60)
        start_btn.pack(pady=50)

    def start_quest(self):
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        gender = self.entry_gender.get().strip()
        if not name or not age or not gender:
            messagebox.showerror("⚠️ Missing Information", "Please complete all fields!")
            return
        
        self.controller.player.set_profile(name, age, gender)
        self.controller.player.save_profile()
        self.controller.show_frame("GreetingFrame")

class GreetingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("#0d1117", "#0d1117"))
        self.controller = controller

        frame = ctk.CTkFrame(self, width=900, height=500, corner_radius=25, fg_color=("gray8", "#1a1a1a"), border_width=3, border_color=("#3b82f6", "#60a5fa"))
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.greet_label = ctk.CTkLabel(frame, text="", font=("Orbitron", 42, "bold"), text_color=("#3b82f6", "#60a5fa"))
        self.greet_label.pack(pady=(50, 20))
        
        ctk.CTkLabel(frame, text="🌟 Ready to Forge Your Destiny? 🌟", font=("Orbitron", 22), text_color=("#fbbf24", "#fde047")).pack(pady=15)
        
        ctk.CTkButton(frame, text="🚀 START ADVENTURE", command=lambda: self.controller.show_frame("MainAppFrame"), font=("Orbitron", 16, "bold"), height=45).pack(pady=40)
    
    def refresh_greeting(self):
        self.greet_label.configure(text=f"⚔️ Welcome, {self.controller.player.data['name']}! ⚔️")

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("#0d1117", "#0d1117"))
        self.controller = controller

        main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # --- Profile Section ---
        profile_section = ctk.CTkFrame(main_container, height=220, corner_radius=25, fg_color=("gray8", "#1a1a1a"), border_width=3, border_color=("#3b82f6", "#60a5fa"))
        profile_section.pack(fill="x", pady=(0, 25))
        player_info_frame = ctk.CTkFrame(profile_section, fg_color="transparent")
        player_info_frame.pack(expand=True, fill="both", pady=25)
        avatar_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent")
        avatar_frame.pack(pady=15)
        ctk.CTkFrame(avatar_frame, width=140, height=140, corner_radius=70, fg_color="transparent", border_width=4, border_color=("#fbbf24", "#fde047")).pack()
        avatar_bg = ctk.CTkFrame(avatar_frame, width=120, height=120, corner_radius=60, fg_color=("#1e40af", "#3b82f6"), border_width=3, border_color=("#fbbf24", "#fde047"))
        avatar_bg.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(avatar_bg, text="🧙‍♂️", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")
        details_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent")
        details_frame.pack(pady=20)
        name_label = ctk.CTkLabel(details_frame, text="", font=("Orbitron", 32, "bold"), text_color=("#3b82f6", "#60a5fa"))
        name_label.pack()
        info_label = ctk.CTkLabel(details_frame, text="", font=("Arial", 18), text_color=("#9ca3af", "#d1d5db"))
        info_label.pack(pady=8)
        self.controller.widgets_to_update.update({'name_label': name_label, 'info_label': info_label})
        
        # --- XP Section ---
        xp_section = ctk.CTkFrame(main_container, height=140, corner_radius=25, fg_color=("gray8", "#1a1a1a"), border_width=3, border_color=("#059669", "#10b981"))
        xp_section.pack(fill="x", pady=(0, 25))
        xp_content = ctk.CTkFrame(xp_section, fg_color="transparent")
        xp_content.pack(expand=True, fill="both", pady=25, padx=40)
        level_label = ctk.CTkLabel(xp_content, text="", font=("Orbitron", 28, "bold"), text_color=("#fbbf24", "#fde047"))
        level_label.pack(pady=(15, 25))
        xp_progress_frame = ctk.CTkFrame(xp_content, fg_color=("gray10", "#2a2a2a"), corner_radius=15, border_width=2, border_color=("#374151", "#4b5563"))
        xp_progress_frame.pack(fill="x", pady=10)
        main_xp_bar = AnimatedProgressBar(xp_progress_frame, height=30, progress_color=("#059669", "#10b981"), fg_color=("#374151", "#4b5563"), corner_radius=15)
        main_xp_bar.pack(fill="x", pady=15, padx=20)
        xp_label = ctk.CTkLabel(xp_progress_frame, text="", font=("Arial", 16, "bold"), text_color=("#e5e7eb", "#f3f4f6"))
        xp_label.pack(pady=5)
        self.controller.widgets_to_update.update({'main_level_label': level_label, 'main_xp_bar': main_xp_bar, 'main_xp_label': xp_label})
        
        # --- Two-Column Layout ---
        content_section = ctk.CTkFrame(main_container, corner_radius=20, fg_color="transparent")
        content_section.pack(fill="both", expand=True)
        left_column = ctk.CTkFrame(content_section, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=1, border_color=("#374151", "#4b5563"))
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
        right_column = ctk.CTkFrame(content_section, corner_radius=15, fg_color=("gray10", "#1a1a1a"), border_width=1, border_color=("#374151", "#4b5563"))
        right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # --- Left Column: Stats ---
        ctk.CTkLabel(left_column, text="⚔️ PLAYER STATISTICS ⚔️", font=("Orbitron", 20, "bold"), text_color=("#3b82f6", "#60a5fa")).pack(pady=20)
        for stat_name in self.controller.player.data['stats']:
            self._create_stat_dropdown(left_column, stat_name)
            
        # --- Right Column: Habits Placeholder ---
        ctk.CTkLabel(right_column, text="📋 DAILY HABITS 📋", font=("Orbitron", 20, "bold"), text_color=("#059669", "#10b981")).pack(pady=20)
        placeholder_frame = ctk.CTkFrame(right_column, fg_color=("gray15", "#2a2a2a"), corner_radius=15, border_width=1, border_color=("#374151", "#4b5563"))
        placeholder_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        ctk.CTkLabel(placeholder_frame, text="🚧 HABIT TRACKER COMING SOON 🚧", font=("Arial", 16, "italic"), text_color=("#6b7280", "#9ca3af")).place(relx=0.5, rely=0.5, anchor="center")
        
        # --- Bottom Control Bar ---
        control_bar = ctk.CTkFrame(main_container, height=60, corner_radius=15, fg_color=("gray15", "#1f1f1f"), border_width=1, border_color=("#374151", "#4b5563"))
        control_bar.pack(fill="x", pady=(20, 0), side="bottom")
        btn_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both", pady=10, padx=20)
        ctk.CTkButton(btn_frame, text="⏪ Prev Track", command=lambda: self.controller._change_track(-1)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Next Track ⏩", command=lambda: self.controller._change_track(1)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Exit", command=self.controller.destroy, fg_color=("#dc2626", "#ef4444"), hover_color=("#b91c1c", "#dc2626")).pack(side="right", padx=10)
        
        self.controller.update_ui()

    def _create_stat_dropdown(self, parent, stat_name):
        stat_data = self.controller.player.data['stats'][stat_name]
        container = ctk.CTkFrame(parent, fg_color=("gray15", "#2a2a2a"), corner_radius=20, border_width=2, border_color=("#374151", "#4b5563"))
        container.pack(fill="x", padx=15, pady=12)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)

        button = ctk.CTkButton(header, text="", font=("Orbitron", 18, "bold"), height=50, fg_color=("#1e40af", "#3b82f6"), hover_color=("#1d4ed8", "#2563eb"), corner_radius=15, anchor="w")
        button.pack(fill="x", pady=8)

        progress_frame = ctk.CTkFrame(header, fg_color=("gray20", "#333333"), corner_radius=12)
        progress_frame.pack(fill="x", pady=8)

        xp_bar = AnimatedProgressBar(progress_frame, height=12, progress_color=("#059669", "#10b981"), fg_color=("#374151", "#4b5563"), corner_radius=6)
        xp_bar.pack(fill="x", pady=8, padx=15)

        xp_label = ctk.CTkLabel(progress_frame, text="", font=("Arial", 14, "bold"), text_color=("#9ca3af", "#d1d5db"))
        xp_label.pack(pady=(0, 10))

        self.controller.widgets_to_update[stat_name] = {'header_btn': button, 'xp_progress': xp_bar, 'xp_label': xp_label}
        
        tasks_frame = ctk.CTkFrame(container, fg_color=("gray10", "#1f1f1f"))
        button.configure(command=lambda: tasks_frame.pack(fill="x", padx=15, pady=(0, 15)) if not tasks_frame.winfo_viewable() else tasks_frame.pack_forget())
        
        # This is the line that caused the error. Now properly formatted.
        for task_name, xp_reward in stat_data['tasks'].items():
            ctk.CTkButton(
                tasks_frame,
                text=f"🎯 {task_name} (+{xp_reward} XP)",
                font=("Arial", 14, "bold"),
                height=45,
                fg_color=("#065f46", "#059669"),
                hover_color=("#047857", "#10b981"),
                corner_radius=12,
                anchor="w",
                command=lambda s=stat_name, t=task_name: self._complete_task(s, t)
            ).pack(fill="x", padx=10, pady=6)
            
    def _complete_task(self, stat_name, task_name):
        try:
            playsound(os.path.join('Quest_Forge' , 'sounds', 'task_complete.mp3'), block=False)
        except Exception as e:
            print(f"Could not play task sound: {e}")
        
        old_data = copy.deepcopy(self.controller.player.data)
        status = self.controller.player.add_stat_xp(stat_name, task_name)
        if status:
            self._show_task_completion_popup(stat_name, task_name, status['xp_gained'], old_data)
        self.controller.update_ui()
    
    def _show_task_completion_popup(self, stat_name, task_name, xp_gained, old_data):
        popup = ctk.CTkToplevel()
        popup.title("🎉 Task Completed!")
        popup.transient()
        popup.grab_set()
        popup.attributes("-topmost", True)
        
        main_frame = ctk.CTkFrame(popup, fg_color=("gray8", "#1a1a1a"), corner_radius=25, border_width=3, border_color="#059669")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text=f"Completed: {task_name}\n+ {xp_gained} XP", font=("Orbitron", 20, "bold")).pack(pady=20)
        
        if self.controller.player.data['level'] > old_data['level']:
            ctk.CTkLabel(main_frame, text="🎊 PLAYER LEVEL UP! 🎊", font=("Orbitron", 22, "bold"), text_color="#fbbf24").pack(pady=10)
            
        ctk.CTkButton(main_frame, text="Continue", command=popup.destroy).pack(pady=10)

if __name__ == "__main__":
    app = QuestForgeApp()
    app.mainloop()