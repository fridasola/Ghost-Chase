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
        self.root.title("Ghost Chase - Manoir Hanté")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Fond sombre style manoir
        self.root.configure(bg="#1a1a24")
        
        # --- TITRE ---
        title_frame = Frame(root, bg="#1a1a24")
        title_frame.pack(pady=30)
        
        title_label = Label(title_frame, text="GHOST CHASE", font=("Arial", 28, "bold"), 
                            fg="#ff8800", bg="#1a1a24")
        title_label.pack()
        
        subtitle_label = Label(title_frame, text="Traquez le fantôme... ou échappez à la lumière.", 
                              font=("Arial", 11, "italic"), fg="#8888aa", bg="#1a1a24")
        subtitle_label.pack(pady=5)
        
        # --- BOUTON DE LANCEMENT ---
        modes_frame = Frame(root, bg="#1a1a24")
        modes_frame.pack(pady=15)
        
        self.start_button = Button(modes_frame, text="ENTRER DANS LE MANOIR", font=("Arial", 13, "bold"),
                                 bg="#ff7700", fg="#ffffff", activebackground="#ff9933", activeforeground="#ffffff",
                                 relief="flat", bd=0, padx=20, pady=10,
                                 command=self.start_game)
        self.start_button.pack()
        
        # --- CADRE DES CONTRÔLES ---
        instructions_frame = Frame(root, bg="#222230", padx=20, pady=15)
        instructions_frame.pack(pady=15, fill="x", padx=50)
        
        instructions_title = Label(instructions_frame, text="Commandes des rôles :", 
                                 font=("Arial", 11, "bold"), fg="#ffaa44", bg="#222230")
        instructions_title.pack(anchor="w", pady=(0, 5))
        
        instructions = [
            "🔦 Chasseur : Flèches directionnelles pour bouger, [L] pour la lampe",
            "👻 Fantôme : Touches W-A-S-D pour se déplacer"
        ]
        
        for instruction in instructions:
            instr_label = Label(instructions_frame, text=instruction, 
                              font=("Arial", 10), fg="#cccccc", bg="#222230", justify="left")
            instr_label.pack(anchor="w", pady=2)
        
        # --- FOOTER ---
        footer_frame = Frame(root, bg="#1a1a24")
        footer_frame.pack(side="bottom", fill="x", pady=20)
        
        quit_button = Button(footer_frame, text="Quitter", font=("Arial", 10),
                           bg="#333344", fg="#aaaaaa", activebackground="#444455", activeforeground="#ffffff",
                           relief="flat", bd=0, padx=15, pady=5,
                           command=self.quit_game)
        quit_button.pack()
        
    def start_game(self):
        # Désactiver le bouton pour éviter les doubles clics
        self.start_button.config(state="disabled", bg="#555555")
        
        # Lancer le jeu dans un thread séparé pour ne pas figer l'interface Tkinter
        game_thread = threading.Thread(target=self.run_game)
        game_thread.daemon = True
        game_thread.start()

    
    def run_game(self):
        try:
            game = Game()
            game.run()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue dans le jeu : {str(e)}")
        finally:
            # Réactiver le bouton une fois la partie fermée
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.start_button.config(state="normal", bg="#ff7700"))
    
    def quit_game(self):
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment fuir le manoir ?"):
            self.root.destroy()
            sys.exit()

def main():
    root = tk.Tk()
    app = GhostChaseLobby(root)
    root.mainloop()

if __name__ == "__main__":
    main()