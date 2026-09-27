# Ghost Chase 👻🔦

*Ghost Chase* est un jeu multijoueur compétitif et asymétrique développé en Python avec **Pygame**. Un joueur incarne un Chasseur équipé d'une lampe torche dans un manoir hanté, tandis que l'autre incarne un Fantôme cherchant à survivre ou à l'emporter avant la fin du temps imparti !

---

## 🎮 Fonctionnalités du jeu

* **Gameplay Asymétrique :** 
  * **Le Chasseur** doit explorer le manoir, gérer la batterie de sa lampe torche, ramasser des recharges d'énergie et éclairer le fantôme pour réduire ses points de vie.
  * **Le Fantôme** se déplace discrètement dans l'obscurité, peut regagner de la vie s'il reste caché dans le noir, et l'emporte si le temps s'écoule ou si le chasseur est attrapé.
* **Cartes Aléatoires :** Le jeu propose 4 dispositions de manoir différentes générées aléatoirement à chaque partie avec des positions de départ sécurisées.
* **Système de POV (Point de Vue) :** Le fantôme se voit en permanence sur son écran, tandis que le chasseur doit s'aider de sa lampe torche et d'un détecteur pour le localiser.
* **Interface Stylisée :** Un menu d'accueil dynamique (`Lobby.py`) et des graphismes entièrement dessinés en code (pas besoin d'images externes).

---

## 🕹️ Commandes

| Rôle | Touches | Action |
| :--- | :--- | :--- |
| **Chasseur** | `Flèches directionnelles` | Se déplacer |
| **Chasseur** | `L` | Allumer / éteindre la lampe torche |
| **Fantôme** | `W`, `A`, `S`, `D` | Se déplacer |

---

## 🚀 Installation et Lancement

### 1. Prérequis
Assurez-vous d'avoir Python installé ainsi que la bibliothèque **Pygame** :
```bash
pip install pygame
```

### 2. Lancer en mode local (sur un même PC)
Assurez-vous d'avoir les fichiers suivants dans le même dossier :

- game.py
-entities.py
-Lobby.py

Lancez ensuite le menu du jeu :

'''Bash
python Lobby.py'''

### 3. Lancer en mode Réseau (Multijoueur sur deux PC)
Sur le premier ordinateur (le serveur) :

'''Bash
python server.py''' 

Sur les deux ordinateurs (le serveur et le client) :

'''Bash
python client.py'''

(Entrez l'adresse IP locale du serveur si vous jouez sur deux machines distinctes, ou laissez vide pour localhost).

👥 Auteurs
Projet initié pendant les années de lycée et repris pour être amélioré !