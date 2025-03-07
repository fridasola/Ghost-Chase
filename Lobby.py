import tkinter as tk
from tkinter import messagebox, Label, Button, Frame
import pygame
import threading
import sys
import os
from game import Game

class GhostChaseLobby:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghost Chase Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Set background color
        self.root.configure(bg="#2d2d2d")
        
        # Title
        title_frame = Frame(root, bg="#2d2d2d")
        title_frame.pack(pady=20)
        
        title_label = Label(title_frame, text="GHOST CHASE", font=("Arial", 24, "bold"), 
                            fg="#ff9900", bg="#2d2d2d")
        title_label.pack()
        
        subtitle_label = Label(title_frame, text="Un jeu de chasse aux fantômes", 
                              font=("Arial", 12), fg="#cccccc", bg="#2d2d2d")
        subtitle_label.pack(pady=5)
        
        # Game modes
        modes_frame = Frame(root, bg="#2d2d2d")
        modes_frame.pack(pady=20)
        
        self.start_button = Button(modes_frame, text="JOUER", font=("Arial", 14, "bold"),
                                 bg="#ff9900", fg="#000000", width=15, height=2,
                                 command=self.start_game)
        self.start_button.pack(pady=10)
        
        # Instructions
        instructions_frame = Frame(root, bg="#2d2d2d")
        instructions_frame.pack(pady=10)
        
        instructions_title = Label(instructions_frame, text="Contrôles:", 
                                 font=("Arial", 12, "bold"), fg="#ffffff", bg="#2d2d2d")
        instructions_title.pack(anchor="w")
        
        instructions = [
            "- Chasseur: Flèches pour se déplacer, L pour la lampe",
            "- Fantôme: WASD pour se déplacer"
        ]
        
        for instruction in instructions:
            instr_label = Label(instructions_frame, text=instruction, 
                              font=("Arial", 10), fg="#cccccc", bg="#2d2d2d", justify="left")
            instr_label.pack(anchor="w", padx=20)
        
        # Footer
        footer_frame = Frame(root, bg="#2d2d2d")
        footer_frame.pack(side="bottom", fill="x", pady=10)
        
        quit_button = Button(footer_frame, text="Quitter", font=("Arial", 10),
                           bg="#444444", fg="#ffffff", width=10,
                           command=self.quit_game)
        quit_button.pack(side="right", padx=20)
        
    def start_game(self):
        # Disable the start button to prevent multiple clicks
        self.start_button.config(state="disabled")
        
        # Show a message about controls
        messagebox.showinfo("Ghost Chase", 
                           "Le jeu va démarrer!\n\n"
                           "Chasseur: Flèches pour se déplacer, L pour la lampe\n"
                           "Fantôme: WASD pour se déplacer\n\n"
                           "Appuyez sur OK pour commencer")
        
        # Start the game in a separate thread
        game_thread = threading.Thread(target=self.run_game)
        game_thread.daemon = True  # Thread will close when main program exits
        game_thread.start()
        
    def run_game(self):
        try:
            game = Game()
            game.run()
        except Exception as e:
            messagebox.showerror("Error", f"Une erreur est survenue: {str(e)}")
        finally:
            # Re-enable the start button when the game ends
            self.root.after(0, lambda: self.start_button.config(state="normal"))
    
    def quit_game(self):
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter?"):
            self.root.destroy()
            sys.exit()

def main():
    # Create and run the application
    root = tk.Tk()
    app = GhostChaseLobby(root)
    root.mainloop()

if __name__ == "__main__":
    main()