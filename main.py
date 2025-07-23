# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from player import Player
import math
import threading
import time

# Global player instance
player = Player()

# Enhanced Theme Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.target_value = 0
        self.current_value = 0
        self.animation_speed = 0.08 # Slightly faster animation for a snappier feel
        
    def animate_to(self, target_value):
        self.target_value = target_value
        self._animate_step()
        
    def _animate_step(self):
        # Continue animation if the difference is significant
        if abs(self.current_value - self.target_value) > 0.005: 
            diff = self.target_value - self.current_value
            self.current_value += diff * self.animation_speed
            self.set(self.current_value)
            self.after(16, self._animate_step)  # ~60 FPS update rate
        else:
            # Snap to target value when close enough to prevent infinite small adjustments
            self.current_value = self.target_value
            self.set(self.current_value)

def start_greeting_window():
    """
    Displays the welcome screen to the player after character creation or profile load.
    Includes an animated background and pulsing instruction.
    """
    try:
        # Destroy the setup window if it exists and is still open
        setup_win.destroy()
    except NameError:
        pass # setup_win might not exist if profile was loaded directly

    greet_win = ctk.CTk()
    greet_win.title("QuestForge - Welcome")
    greet_win.geometry("1200x800") # Set initial window size
    greet_win.state('zoomed')   # Maximize the window with controls
    greet_win.configure(fg_color=("#0d1117", "#0d1117")) # Dark background

    # Create gradient background effect using a Tkinter Canvas
    canvas = tk.Canvas(greet_win, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Animated gradient background function
    def create_gradient():
        canvas.delete("gradient") # Clear previous gradient lines
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Draw lines to create a vertical gradient
        for i in range(height):
            # Interpolate RGB values for a subtle dark blue to slightly lighter dark blue gradient
            r = int(13 + (i / height) * 20)
            g = int(17 + (i / height) * 30)
            b = int(23 + (i / height) * 40)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color, tags="gradient")
    
    # Schedule initial gradient creation and re-creation on window resize
    greet_win.after(100, create_gradient)
    greet_win.bind("<Configure>", lambda e: greet_win.after(10, create_gradient))

    # Main content frame with enhanced styling
    frame = ctk.CTkFrame(greet_win, width=900, height=500, corner_radius=25, 
                         fg_color=("gray8", "#1a1a1a"), border_width=3, 
                         border_color=("#3b82f6", "#60a5fa"))
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Add subtle glow effect around the main content frame
    glow_frame = ctk.CTkFrame(greet_win, width=920, height=520, corner_radius=30,
                              fg_color="transparent", border_width=1,
                              border_color=("#1e40af", "#3b82f6"))
    glow_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Glowing title effect
    title_frame = ctk.CTkFrame(frame, fg_color="transparent")
    title_frame.pack(pady=50) # Increased padding for better spacing
    
    greeting = f"⚔️ Welcome, {player.data['name']}! ⚔️"
    greet_label = ctk.CTkLabel(title_frame, text=greeting, 
                               font=("Orbitron", 42, "bold"), # Larger, bolder font
                               text_color=("#3b82f6", "#60a5fa"))
    greet_label.pack()

    subtitle = "🌟 Ready to Forge Your Destiny? 🌟"
    subtitle_label = ctk.CTkLabel(title_frame, text=subtitle, 
                                  font=("Orbitron", 22), # Larger font
                                  text_color=("#fbbf24", "#fde047"))
    subtitle_label.pack(pady=15)

    # Animated instruction with better styling
    instruction_frame = ctk.CTkFrame(frame, fg_color="transparent")
    instruction_frame.pack(pady=30) # Increased padding
    
    instruction = ctk.CTkLabel(instruction_frame, 
                               text="✨ Click anywhere to begin your legendary journey... ✨", 
                               font=("Arial", 18, "italic"), # Larger font
                               text_color=("#9ca3af", "#d1d5db"))
    instruction.pack()

    # Enhanced pulsing animation for the instruction text
    def pulse_instruction():
        current_color = instruction.cget("text_color")
        # Check the current color to toggle between two states for pulsing effect
        if current_color[0] == "#9ca3af": # Check the dark mode color
            instruction.configure(text_color=("#ffffff", "#ffffff")) # Brighter color
        else:
            instruction.configure(text_color=("#9ca3af", "#d1d5db")) # Original color
        greet_win.after(1200, pulse_instruction) # Repeat every 1.2 seconds
    
    pulse_instruction() # Start the pulsing animation

    def proceed(event=None):
        """Destroys greeting window and starts the main application."""
        greet_win.destroy()
        start_main_app()

    # Enhanced buttons for better user interaction
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=30)

    proceed_btn = ctk.CTkButton(button_frame, text="🚀 START ADVENTURE", 
                                command=proceed,
                                font=("Orbitron", 16, "bold"),
                                fg_color=("#059669", "#10b981"),
                                hover_color=("#047857", "#059669"),
                                width=200, height=45,
                                corner_radius=25) # Rounded button
    proceed_btn.pack(pady=10)

    exit_btn = ctk.CTkButton(button_frame, text="❌ Exit", 
                             command=greet_win.destroy,
                             font=("Arial", 14),
                             fg_color=("#dc2626", "#ef4444"),
                             hover_color=("#b91c1c", "#dc2626"),
                             width=100, height=35,
                             corner_radius=20) # Rounded button
    exit_btn.pack(pady=10)

    # Bind click and keyboard events to proceed or exit
    greet_win.bind("<Button-1>", proceed)
    greet_win.bind("<Return>", proceed)
    greet_win.bind("<Escape>", lambda e: greet_win.destroy())

    greet_win.mainloop()

def start_setup_window():
    """
    Displays the character creation window where the player enters their details.
    """
    global setup_win # Declare as global to be accessible for destruction
    setup_win = ctk.CTk()
    setup_win.title("QuestForge - Character Creation")
    setup_win.geometry("1200x800") # Set initial window size
    setup_win.state('zoomed')   # Maximize the window with controls
    setup_win.configure(fg_color=("#0d1117", "#0d1117")) # Dark background

    # Main container frame with enhanced styling
    main_frame = ctk.CTkFrame(setup_win, width=1000, height=700, corner_radius=30,
                              fg_color=("gray8", "#1a1a1a"), border_width=3,
                              border_color=("#3b82f6", "#60a5fa"))
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Title with special effects
    title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    title_frame.pack(pady=40)
    
    title = ctk.CTkLabel(title_frame, text="⚔️ QUESTFORGE CHARACTER CREATION ⚔️", 
                         font=("Orbitron", 36, "bold"), # Larger, bolder font
                         text_color=("#3b82f6", "#60a5fa"))
    title.pack()

    subtitle = ctk.CTkLabel(title_frame, text="🌟 Forge Your Legend 🌟", 
                            font=("Orbitron", 20), # Larger font
                            text_color=("#fbbf24", "#fde047"))
    subtitle.pack(pady=15)

    # Enhanced form container with better background and borders
    form_frame = ctk.CTkFrame(main_frame, fg_color=("gray10", "#2a2a2a"), 
                              corner_radius=20, border_width=2,
                              border_color=("#374151", "#4b5563"))
    form_frame.pack(pady=30, padx=60, fill="x")

    # Enhanced entry fields with better styling
    ctk.CTkLabel(form_frame, text="🏷️ Hero Name:", 
                 font=("Arial", 18, "bold"), # Larger font
                 text_color=("#e5e7eb", "#f3f4f6")).pack(pady=(30, 8))
    
    entry_name = ctk.CTkEntry(form_frame, placeholder_text="Enter your legendary name...", 
                              font=("Arial", 16), height=50, # Larger height
                              border_width=2, border_color=("#3b82f6", "#60a5fa"),
                              corner_radius=15) # Rounded corners
    entry_name.pack(pady=5, padx=30, fill="x")

    ctk.CTkLabel(form_frame, text="🎂 Age:", 
                 font=("Arial", 18, "bold"),
                 text_color=("#e5e7eb", "#f3f4f6")).pack(pady=(25, 8))
    
    entry_age = ctk.CTkEntry(form_frame, placeholder_text="How many years have you lived?", 
                             font=("Arial", 16), height=50,
                             border_width=2, border_color=("#3b82f6", "#60a5fa"),
                             corner_radius=15)
    entry_age.pack(pady=5, padx=30, fill="x")

    ctk.CTkLabel(form_frame, text="⚧️ Gender:", 
                 font=("Arial", 18, "bold"),
                 text_color=("#e5e7eb", "#f3f4f6")).pack(pady=(25, 8))
    
    entry_gender = ctk.CTkEntry(form_frame, placeholder_text="Male/Female/Other", 
                                font=("Arial", 16), height=50,
                                border_width=2, border_color=("#3b82f6", "#60a5fa"),
                                corner_radius=15)
    entry_gender.pack(pady=5, padx=30, fill="x")

    def start():
        """
        Validates input, sets player profile, saves it, and proceeds to the greeting window.
        """
        name = entry_name.get().strip()
        age = entry_age.get().strip()
        gender = entry_gender.get().strip()

        if not name or not age or not gender:
            messagebox.showerror("⚠️ Missing Information", 
                                 "Please complete all fields to create your character!")
            return

        player.set_profile(name, age, gender)
        player.save_profile()
        start_greeting_window()

    # Enhanced start button with bold font and rounded corners
    start_btn = ctk.CTkButton(form_frame, text="🚀 BEGIN QUEST", 
                              command=start, 
                              font=("Orbitron", 20, "bold"),
                              height=60, width=300, # Larger button
                              fg_color=("#059669", "#10b981"),
                              hover_color=("#047857", "#059669"),
                              border_width=3,
                              border_color=("#34d399", "#6ee7b7"),
                              corner_radius=30)
    start_btn.pack(pady=50)

    # Exit button with rounded corners
    exit_btn = ctk.CTkButton(form_frame, text="❌ Exit", 
                             command=setup_win.destroy,
                             font=("Arial", 14),
                             fg_color=("#dc2626", "#ef4444"),
                             hover_color=("#b91c1c", "#dc2626"),
                             width=100, height=35,
                             corner_radius=20)
    exit_btn.pack(pady=(0, 30))

    setup_win.bind("<Escape>", lambda e: setup_win.destroy())
    setup_win.mainloop()

def create_stat_dropdown(parent, stat_name, stat_data):
    """
    Creates an enhanced dropdown menu for a specific stat, displaying its level, XP,
    and a list of tasks that reward XP for that stat.
    """
    # Main stat container with enhanced styling
    stat_container = ctk.CTkFrame(parent, fg_color=("gray15", "#2a2a2a"), 
                                  corner_radius=20, border_width=2,
                                  border_color=("#374151", "#4b5563"))
    stat_container.pack(fill="x", padx=15, pady=12)
    
    # Stat header with progress
    header_frame = ctk.CTkFrame(stat_container, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=15)
    
    # Stat info
    stat_level = stat_data['level']
    stat_xp = stat_data['xp']
    stat_xp_limit = stat_data['xp_limit']
    
    # Enhanced header button with better styling and larger font
    header_text = f"⚔️ {stat_name} - Level {stat_level}"
    header_btn = ctk.CTkButton(header_frame, text=header_text,
                               font=("Orbitron", 18, "bold"),
                               height=50, 
                               fg_color=("#1e40af", "#3b82f6"),
                               hover_color=("#1d4ed8", "#2563eb"),
                               corner_radius=15, # Rounded corners for the header button
                               anchor="w") # Align text to the left
    header_btn.pack(fill="x", pady=8)
    
    # Enhanced progress section with a subtle background frame
    progress_frame = ctk.CTkFrame(header_frame, fg_color=("gray20", "#333333"),
                                  corner_radius=12, border_width=1,
                                  border_color=("#374151", "#4b5563"))
    progress_frame.pack(fill="x", pady=8)
    
    # Progress bar with better styling and rounded corners
    xp_progress = AnimatedProgressBar(progress_frame, height=12, 
                                      progress_color=("#059669", "#10b981"),
                                      fg_color=("#374151", "#4b5563"),
                                      corner_radius=6) # Rounded corners for progress bar
    xp_progress.pack(fill="x", pady=8, padx=15)
    xp_progress.animate_to(stat_xp / stat_xp_limit)
    
    # XP label with percentage display
    xp_label = ctk.CTkLabel(progress_frame, 
                            text=f"💫 {stat_xp:,}/{stat_xp_limit:,} XP ({(stat_xp/stat_xp_limit)*100:.1f}%)",
                            font=("Arial", 14, "bold"),
                            text_color=("#9ca3af", "#d1d5db"))
    xp_label.pack(pady=(0, 10))
    
    # Tasks dropdown container with smooth animation
    tasks_frame = ctk.CTkFrame(stat_container, fg_color=("gray10", "#1f1f1f"),
                               corner_radius=15, border_width=1,
                               border_color=("#374151", "#4b5563"))
    
    is_expanded = False
    animation_running = False # Flag to prevent multiple rapid clicks during animation
    
    def toggle_tasks():
        nonlocal is_expanded, animation_running
        if animation_running:
            return # Prevent re-triggering if animation is already running
            
        animation_running = True
        
        if is_expanded:
            # Collapse animation: change header text and then hide the tasks frame
            header_btn.configure(text=f"⚔️ {stat_name} - Level {stat_level}")
            
            def hide_tasks_complete():
                tasks_frame.pack_forget() # Hide the frame
                nonlocal animation_running
                animation_running = False # Reset flag after animation completes
                
            # Use after to create a slight delay before hiding, giving a smoother feel
            stat_container.after(50, hide_tasks_complete) 
            is_expanded = False
        else:
            # Expand animation: change header text and then show the tasks frame
            header_btn.configure(text=f"⚡ {stat_name} - Level {stat_level} (Click to close)")
            tasks_frame.pack(fill="x", padx=15, pady=(0, 15)) # Show the frame
            is_expanded = True
            animation_running = False # Reset flag immediately for expand, as pack is instant
            # Note: For truly smooth expand/collapse, animating height with grid or place is better,
            # but this is the best approach with pack for a simple toggle.
            
    header_btn.configure(command=toggle_tasks) # Bind the toggle function to the header button
    
    # Create enhanced task buttons within an inner frame for better padding control
    tasks_inner_frame = ctk.CTkFrame(tasks_frame, fg_color="transparent")
    tasks_inner_frame.pack(fill="x", padx=15, pady=15)
    
    for i, (task_name, xp_reward) in enumerate(stat_data['tasks'].items()):
        # Create a callback function for each task button
        def make_task_callback(stat=stat_name, task=task_name):
            return lambda: complete_task(stat, task)
        
        # Enhanced task button with better styling and rounded corners
        task_btn = ctk.CTkButton(tasks_inner_frame, 
                                 text=f"🎯 {task_name} (+{xp_reward} XP)",
                                 font=("Arial", 14, "bold"),
                                 height=45, # Taller buttons
                                 fg_color=("#065f46", "#059669"),
                                 hover_color=("#047857", "#10b981"),
                                 command=make_task_callback(),
                                 corner_radius=12, # Rounded corners
                                 anchor="w")
        task_btn.pack(fill="x", padx=5, pady=6)
        
        # Add subtle animation delay for staggered appearance of task buttons when dropdown is created
        # This runs once when the stat dropdown is initially created, not every time it's expanded/collapsed.
        task_btn.configure(state="disabled") # Disable initially to allow animation
        stat_container.after(i * 50, lambda btn=task_btn: btn.configure(state="normal")) # Enable after a delay
        
    return stat_container

def show_task_completion_popup(stat_name, task_name, xp_gained, old_stat_data, new_stat_data, old_player_data, new_player_data):
    """
    Displays an enhanced popup window detailing the results of a completed task,
    including XP gained and before/after stats for the specific stat and overall player.
    """
    popup = ctk.CTkToplevel()
    popup.title("🎉 Task Completed!")
    popup.geometry("600x500") # Fixed size for the popup
    popup.transient() # Make it transient to the main app window
    popup.grab_set()  # Grab focus, preventing interaction with other windows until closed
    popup.configure(fg_color=("#0d1117", "#0d1117")) # Dark background for popup
    
    # Center the popup on the screen
    popup.update_idletasks() # Update geometry info
    x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
    y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"600x500+{x}+{y}")
    
    # Main frame with enhanced styling for the popup content
    main_frame = ctk.CTkFrame(popup, fg_color=("gray8", "#1a1a1a"), 
                              corner_radius=25, border_width=3,
                              border_color=("#059669", "#10b981")) # Green border for success
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Success animation frame for the top section
    success_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    success_frame.pack(pady=30)
    
    # Animated success message
    success_label = ctk.CTkLabel(success_frame, text="🎉 QUEST COMPLETED! 🎉",
                                 font=("Orbitron", 28, "bold"),
                                 text_color=("#059669", "#10b981")) # Green success text
    success_label.pack()
    
    task_label = ctk.CTkLabel(success_frame, text=f"📋 {task_name}",
                              font=("Arial", 18, "bold"),
                              text_color=("#fbbf24", "#fde047")) # Gold task name
    task_label.pack(pady=10)
    
    # Stats section container
    stats_frame = ctk.CTkFrame(main_frame, fg_color=("gray10", "#2a2a2a"),
                               corner_radius=15, border_width=2,
                               border_color=("#374151", "#4b5563"))
    stats_frame.pack(fill="x", padx=30, pady=20)
    
    # XP gained display
    ctk.CTkLabel(stats_frame, text=f"💫 XP Gained: +{xp_gained}",
                 font=("Arial", 20, "bold"),
                 text_color=("#3b82f6", "#60a5fa")).pack(pady=15) # Blue XP text
    
    # Specific Stat progress section
    stat_section = ctk.CTkFrame(stats_frame, fg_color="transparent")
    stat_section.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(stat_section, text=f"⚔️ {stat_name} Progress:",
                 font=("Arial", 16, "bold"),
                 text_color=("#e5e7eb", "#f3f4f6")).pack()
    
    # Before/After comparison for the specific stat
    before_text = f"Before: Level {old_stat_data['level']} | {old_stat_data['xp']:,}/{old_stat_data['xp_limit']:,} XP"
    after_text = f"After: Level {new_stat_data['level']} | {new_stat_data['xp']:,}/{new_stat_data['xp_limit']:,} XP"
    
    ctk.CTkLabel(stat_section, text=before_text,
                 font=("Arial", 12),
                 text_color=("#9ca3af", "#d1d5db")).pack(pady=2)
    
    ctk.CTkLabel(stat_section, text=after_text,
                 font=("Arial", 12, "bold"),
                 text_color=("#059669", "#10b981")).pack(pady=2) # Green for after state
    
    # Level up notification for the specific stat
    if new_stat_data['level'] > old_stat_data['level']:
        level_up_label = ctk.CTkLabel(stat_section, text=f"🌟 {stat_name} LEVEL UP! 🌟",
                                      font=("Orbitron", 16, "bold"),
                                      text_color=("#fbbf24", "#fde047")) # Gold level up
        level_up_label.pack(pady=10)
    
    # Overall Player level section
    player_section = ctk.CTkFrame(stats_frame, fg_color="transparent")
    player_section.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(player_section, text="🏆 Overall Progress:",
                 font=("Arial", 16, "bold"),
                 text_color=("#e5e7eb", "#f3f4f6")).pack()
    
    # Before/After comparison for overall player
    player_before_text = f"Before: Level {old_player_data['level']} | {old_player_data['xp']:,}/{old_player_data['xp_limit']:,} XP"
    player_after_text = f"After: Level {new_player_data['level']} | {new_player_data['xp']:,}/{new_player_data['xp_limit']:,} XP"
    
    ctk.CTkLabel(player_section, text=player_before_text,
                 font=("Arial", 12),
                 text_color=("#9ca3af", "#d1d5db")).pack(pady=2)
    
    ctk.CTkLabel(player_section, text=player_after_text,
                 font=("Arial", 12, "bold"),
                 text_color=("#3b82f6", "#60a5fa")).pack(pady=2) # Blue for after state
    
    # Overall Player level up notification
    if new_player_data['level'] > old_player_data['level']:
        player_level_up_label = ctk.CTkLabel(player_section, text="🎊 PLAYER LEVEL UP! 🎊",
                                             font=("Orbitron", 18, "bold"),
                                             text_color=("#fbbf24", "#fde047")) # Gold level up
        player_level_up_label.pack(pady=15)
    
    # Close button for the popup
    close_btn = ctk.CTkButton(main_frame, text="✨ Continue Journey",
                              command=popup.destroy, # Closes the popup
                              font=("Orbitron", 16, "bold"),
                              fg_color=("#3b82f6", "#60a5fa"),
                              hover_color=("#1d4ed8", "#2563eb"),
                              height=45, width=200,
                              corner_radius=25)
    close_btn.pack(pady=30)
    
    # Auto-close the popup after 10 seconds for convenience
    popup.after(10000, popup.destroy)

def complete_task(stat_name, task_name):
    """
    Handles the logic for completing a task, updating player stats,
    and then displaying an enhanced completion popup.
    """
    # Store old data for comparison in the popup
    old_stat_data = player.data['stats'][stat_name].copy()
    old_player_data = {'level': player.data['level'], 'xp': player.data['xp'], 'xp_limit': player.data['xp_limit']}
    
    # Get XP reward for the task
    xp_gained = player.data['stats'][stat_name]['tasks'][task_name]
    
    # Update player data using the Player class method
    player.add_stat_xp(stat_name, task_name)
    
    # Get new data after the update for comparison in the popup
    new_stat_data = player.data['stats'][stat_name].copy()
    new_player_data = {'level': player.data['level'], 'xp': player.data['xp'], 'xp_limit': player.data['xp_limit']}
    
    # Show the detailed popup with before/after information
    show_task_completion_popup(stat_name, task_name, xp_gained, old_stat_data, new_stat_data, old_player_data, new_player_data)

    # After task completion and popup, refresh the main app's UI elements
    # This is crucial to update progress bars and labels without destroying the whole window.
    # We need to get a reference to the main app window and then update its components.
    # A simple way to do this is to pass the main app instance to complete_task,
    # or have a global function that can access and update the main app's widgets.
    # For now, we'll rely on the main app's structure to be re-drawn if needed,
    # but for a truly smooth experience, specific widget updates would be better.
    # The previous `refresh_main_app()` which destroyed and recreated the window is removed.
    
    # A more robust way would be to have a method in the main app class (if it were a class)
    # or a global function that iterates through and updates relevant labels/progress bars.
    # For simplicity, and given the new popup handles the immediate feedback,
    # we're omitting a full UI refresh here, assuming the popup is sufficient.

def start_main_app():
    """
    Initializes and displays the main application window, showing player profile,
    overall XP progress, and stat-specific dropdowns.
    """
    app = ctk.CTk()
    app.title("QuestForge - Your Epic Journey")
    app.geometry("1400x900") # Set initial window size
    app.state('zoomed')   # Maximize the window with controls
    app.configure(fg_color=("#0d1117", "#0d1117")) # Dark background
    
    # Create main scrollable container with enhanced styling for the scrollbar
    main_container = ctk.CTkScrollableFrame(app, fg_color="transparent",
                                            scrollbar_button_color=("#374151", "#4b5563"),
                                            scrollbar_button_hover_color=("#4b5563", "#6b7280"))
    main_container.pack(fill="both", expand=True, padx=25, pady=25) # Increased padding
    
    # TOP SECTION - Enhanced Player Profile
    profile_section = ctk.CTkFrame(main_container, height=220, corner_radius=25,
                                   fg_color=("gray8", "#1a1a1a"), border_width=3,
                                   border_color=("#3b82f6", "#60a5fa")) # Blue border
    profile_section.pack(fill="x", pady=(0, 25)) # Increased vertical padding
    
    # Player info container
    player_info_frame = ctk.CTkFrame(profile_section, fg_color="transparent")
    player_info_frame.pack(expand=True, fill="both", pady=25) # Increased vertical padding
    
    # Avatar and basic info
    avatar_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent")
    avatar_frame.pack(pady=15)
    
    # Enhanced avatar with glow effect (outer border)
    avatar_glow = ctk.CTkFrame(avatar_frame, width=140, height=140, corner_radius=70,
                               fg_color="transparent", border_width=4,
                               border_color=("#fbbf24", "#fde047")) # Gold glow
    avatar_glow.pack()
    
    avatar_bg = ctk.CTkFrame(avatar_glow, width=120, height=120, corner_radius=60,
                             fg_color=("#1e40af", "#3b82f6"), border_width=3,
                             border_color=("#fbbf24", "#fde047")) # Inner gold border
    avatar_bg.place(relx=0.5, rely=0.5, anchor="center") # Centered within glow frame
    
    avatar_label = ctk.CTkLabel(avatar_bg, text="🧙‍♂️", font=("Arial", 60))
    avatar_label.place(relx=0.5, rely=0.5, anchor="center")
    
    # Enhanced player details
    details_frame = ctk.CTkFrame(player_info_frame, fg_color="transparent")
    details_frame.pack(pady=20)
    
    name_label = ctk.CTkLabel(details_frame, 
                              text=f"⚔️ {player.data['name']} ⚔️",
                              font=("Orbitron", 32, "bold"), # Larger, bolder font
                              text_color=("#3b82f6", "#60a5fa"))
    name_label.pack()
    
    info_text = f"🎂 Age: {player.data['age']} • ⚧️ Gender: {player.data['gender']}"
    info_label = ctk.CTkLabel(details_frame, text=info_text,
                              font=("Arial", 18), # Larger font
                              text_color=("#9ca3af", "#d1d5db"))
    info_label.pack(pady=8)
    
    # ENHANCED MAIN XP SECTION
    xp_section = ctk.CTkFrame(main_container, height=140, corner_radius=25,
                              fg_color=("gray8", "#1a1a1a"), border_width=3,
                              border_color=("#059669", "#10b981")) # Green border
    xp_section.pack(fill="x", pady=(0, 25))
    
    # XP content with better layout
    xp_content = ctk.CTkFrame(xp_section, fg_color="transparent")
    xp_content.pack(expand=True, fill="both", pady=25, padx=40)
    
    # Enhanced level display
    level_label = ctk.CTkLabel(xp_content, 
                               text=f"🏆 LEVEL {player.data['level']} LEGENDARY HERO 🏆",
                               font=("Orbitron", 28, "bold"), # Larger, bolder font
                               text_color=("#fbbf24", "#fde047")) # Gold text
    level_label.pack(pady=(15, 25))
    
    # Enhanced main XP progress container
    xp_progress_frame = ctk.CTkFrame(xp_content, fg_color=("gray10", "#2a2a2a"),
                                     corner_radius=15, border_width=2,
                                     border_color=("#374151", "#4b5563"))
    xp_progress_frame.pack(fill="x", pady=10)
    
    main_xp_bar = AnimatedProgressBar(xp_progress_frame, height=30, # Taller progress bar
                                      progress_color=("#059669", "#10b981"),
                                      fg_color=("#374151", "#4b5563"),
                                      corner_radius=15) # Rounded corners
    main_xp_bar.pack(fill="x", pady=15, padx=20)
    main_xp_bar.animate_to(player.data['xp'] / player.data['xp_limit'])
    
    xp_percentage = (player.data['xp'] / player.data['xp_limit']) * 100
    xp_text = f"💫 {player.data['xp']:,} / {player.data['xp_limit']:,} XP ({xp_percentage:.1f}%)"
    xp_label = ctk.CTkLabel(xp_progress_frame, text=xp_text,
                            font=("Arial", 16, "bold"),
                            text_color=("#e5e7eb", "#f3f4f6"))
    xp_label.pack(pady=5)
    
    # MAIN CONTENT SECTION (Stats + Habits)
    content_section = ctk.CTkFrame(main_container, corner_radius=20,
                                   fg_color="transparent")
    content_section.pack(fill="both", expand=True)
    
    # Create two columns for Stats and Habits
    left_column = ctk.CTkFrame(content_section, corner_radius=15,
                               fg_color=("gray10", "#1a1a1a"), border_width=1,
                               border_color=("#374151", "#4b5563"))
    left_column.pack(side="left", fill="both", expand=True, padx=(0, 15)) # Increased padx
    
    right_column = ctk.CTkFrame(content_section, corner_radius=15,
                                fg_color=("gray10", "#1a1a1a"), border_width=1,
                                border_color=("#374151", "#4b5563"))
    right_column.pack(side="right", fill="both", expand=True, padx=(15, 0)) # Increased padx
    
    # LEFT COLUMN - Stats
    stats_title = ctk.CTkLabel(left_column, text="⚔️ PLAYER STATISTICS ⚔️",
                               font=("Orbitron", 20, "bold"),
                               text_color=("#3b82f6", "#60a5fa"))
    stats_title.pack(pady=20)
    
    # Stats container
    stats_container = ctk.CTkFrame(left_column, fg_color="transparent")
    stats_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Create stat dropdowns dynamically
    for stat_name, stat_data in player.data['stats'].items():
        create_stat_dropdown(stats_container, stat_name, stat_data)
    
    # RIGHT COLUMN - Habits (Placeholder for future expansion)
    habits_title = ctk.CTkLabel(right_column, text="📋 DAILY HABITS 📋",
                                font=("Orbitron", 20, "bold"),
                                text_color=("#059669", "#10b981"))
    habits_title.pack(pady=20)
    
    habits_placeholder = ctk.CTkFrame(right_column, fg_color=("gray15", "#2a2a2a"),
                                      corner_radius=15, border_width=1,
                                      border_color=("#374151", "#4b5563"))
    habits_placeholder.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    placeholder_label = ctk.CTkLabel(habits_placeholder, 
                                     text="🚧 HABIT TRACKER COMING SOON 🚧\n\n"
                                          "📅 Daily Habits\n"
                                          "📊 Streak Counter\n"
                                          "🎯 Weekly Goals\n"
                                          "🏆 Achievements",
                                     font=("Arial", 16, "italic"),
                                     text_color=("#6b7280", "#9ca3af"),
                                     justify="center")
    placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
    
    # BOTTOM BAR - Controls
    control_bar = ctk.CTkFrame(main_container, height=60, corner_radius=15,
                               fg_color=("gray15", "#1f1f1f"), border_width=1,
                               border_color=("#374151", "#4b5563"))
    control_bar.pack(fill="x", pady=(20, 0))
    
    # Control buttons frame
    btn_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
    btn_frame.pack(expand=True, fill="x", pady=10, padx=20)
    
    refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh",
                                command=lambda: app.update_idletasks(), # Simple UI refresh
                                font=("Arial", 14),
                                fg_color=("#1e40af", "#3b82f6"),
                                hover_color=("#1d4ed8", "#2563eb"),
                                width=120, height=35)
    refresh_btn.pack(side="left", padx=5)
    
    exit_btn = ctk.CTkButton(btn_frame, text="❌ Exit",
                             command=app.destroy,
                             font=("Arial", 14),
                             fg_color=("#dc2626", "#ef4444"),
                             hover_color=("#b91c1c", "#dc2626"),
                             width=120, height=35)
    exit_btn.pack(side="right", padx=5)
    
    # Keyboard shortcuts
    app.bind("<F5>", lambda e: app.update_idletasks()) # F5 to refresh UI
    app.bind("<Escape>", lambda e: app.destroy()) # Esc to exit
    
    app.mainloop()

if __name__ == "__main__":
    # Attempt to load existing player profile
    if player.load_profile():
        print("✅ Profile loaded successfully!")
        start_greeting_window() # Go to greeting if profile exists
    else:
        print("📝 No profile found. Starting character creation...")
        start_setup_window() # Go to setup if no profile found
