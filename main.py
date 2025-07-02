import tkinter as tk
from tkinter import messagebox
from player import Player  # reusing your Player class

# Create Player instance
player = Player()

def start_greeting_window():
    """Show greeting window after setup or if profile already exists."""
    try:
       setup_win.destroy()  # close setup window if it exists
    except NameError:
       pass  # skip if setup_win is not defined


    greet_win = tk.Tk()
    greet_win.title("QuestForge - Welcome!")
    greet_win.configure(bg="#0F0F0F")

    # Greeting text with dynamic name
    greeting = f"Welcome, {player.data['name']}! Ready to conquer?"
    greet_label = tk.Label(greet_win, text=greeting, fg="#00FFFF", bg="#0F0F0F", font=("Helvetica", 24))
    greet_label.pack(pady=50)

    # Instruction text
    instruction = tk.Label(greet_win, text="Click anywhere to enter your Quest...", fg="#AAAAAA", bg="#0F0F0F", font=("Helvetica", 16))
    instruction.pack(pady=20)

    def proceed_to_main(event=None):
        greet_win.destroy()
        start_main_app()

    # Bind mouse click or Enter key to proceed
    greet_win.bind("<Button-1>", proceed_to_main)
    greet_win.bind("<Return>", proceed_to_main)

    greet_win.mainloop()
    greet_win.geometry("1200x700")  # For Windows fullscreen maximize


def start_setup_window():
    """First-time setup window for new users."""
    global setup_win
    setup_win = tk.Tk()
    setup_win.title("QuestForge - Setup")
    setup_win.configure(bg="#0F0F0F")

    tk.Label(setup_win, text="Welcome to QuestForge!", fg="#00FFFF", bg="#0F0F0F", font=("Helvetica", 20)).pack(pady=20)
    tk.Label(setup_win, text="Enter your details to start your quest:", fg="#AAAAAA", bg="#0F0F0F", font=("Helvetica", 14)).pack(pady=10)

    tk.Label(setup_win, text="Name:", fg="#FFFFFF", bg="#0F0F0F", font=("Helvetica", 12)).pack(pady=5)
    entry_name = tk.Entry(setup_win, font=("Helvetica", 12))
    entry_name.pack()

    tk.Label(setup_win, text="Age:", fg="#FFFFFF", bg="#0F0F0F", font=("Helvetica", 12)).pack(pady=5)
    entry_age = tk.Entry(setup_win, font=("Helvetica", 12))
    entry_age.pack()

    tk.Label(setup_win, text="Gender:", fg="#FFFFFF", bg="#0F0F0F", font=("Helvetica", 12)).pack(pady=5)
    entry_gender = tk.Entry(setup_win, font=("Helvetica", 12))
    entry_gender.pack()

    def on_start():
        name = entry_name.get().strip()
        age = entry_age.get().strip()
        gender = entry_gender.get().strip()

        if not name or not age or not gender:
            messagebox.showerror("Incomplete Info", "Please fill out all fields!")
            return
        
        # Save profile
        player.set_profile(name, age, gender)
        player.save_profile()
        start_greeting_window()
        

    tk.Button(setup_win, text="Start Quest", command=on_start, font=("Helvetica", 14), bg="#00FFFF").pack(pady=30)

    setup_win.mainloop()


def start_main_app():
    """Main application window. (Next chunk will build content inside)"""
    main_win = tk.Tk()
    main_win.title("QuestForge - Main Window")
    main_win.configure(bg="#0F0F0F")

    # Placeholder text for now
    tk.Label(main_win, text="Main Quest Window - Coming Soon!", fg="#00FFFF", bg="#0F0F0F", font=("Helvetica", 22)).pack(pady=100)

    main_win.mainloop()
    main_win.geometry("1200x700")  # For Windows fullscreen maximize


if __name__ == "__main__":
    if player.load_profile():
        print("Profile found, skipping setup.")
        start_greeting_window()
    else:
        print("No profile found, starting setup.")
        start_setup_window()
