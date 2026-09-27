# client.py
import pygame
import socket
import threading
import pickle
from entities import Chasseur, Fantome

WIDTH, HEIGHT = 800, 600
FPS = 60

class NetworkGame:
    def __init__(self, server_ip='localhost'):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ghost Chase - Multijoueur")
        self.clock = pygame.time.Clock()
        self.running = True

        self.player_id = None
        self.role = None
        self.players = {}
        self.walls = []
        self.font = pygame.font.Font(None, 24)

        # Connexion au serveur
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((server_ip, 12337))
            print("Connecté au serveur avec succès !")
        except Exception as e:
            print(f"Impossible de se connecter au serveur : {e}")
            self.running = False

        self.listen_thread = threading.Thread(target=self.receive_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def receive_loop(self):
        while self.running:
            try:
                packet = self.client.recv(4096)
                if not packet:
                    break
                message = pickle.loads(packet)
                
                if message['type'] == 'init':
                    self.player_id = message['player_id']
                    self.role = message['role']
                    self.players = message['players']
                    self.walls = message['walls']
                    print(f"Je suis le joueur {self.player_id} ({self.role})")
                elif message['type'] == 'game_state':
                    self.players = message['players']
                    if 'walls' in message and message['walls']:
                        self.walls = message['walls']
            except Exception as e:
                print(f"Erreur de réception : {e}")
                break

    def send_update(self, dx, dy):
        if self.player_id in self.players:
            p = self.players[self.player_id]
            try:
                data = pickle.dumps({
                    'type': 'update_position',
                    'dx': dx,
                    'dy': dy,
                    'speed': p.speed,
                    'lampe_on': getattr(p, 'lampe_on', False),
                    'batterie_lampe': getattr(p, 'batterie_lampe', 100),
                    'points_de_vie': p.points_de_vie,
                    'alive': p.alive
                })
                self.client.send(data)
            except:
                pass

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l and self.role == 'chasseur':
                        if self.player_id in self.players:
                            self.players[self.player_id].lampe_on = not self.players[self.player_id].lampe_on

            # Gestion des mouvements locaux
            dx, dy = 0, 0
            keys = pygame.key.get_pressed()

            if self.player_id and self.player_id in self.players:
                p = self.players[self.player_id]
                if p.alive:
                    if self.role == 'chasseur':
                        if keys[pygame.K_UP]: dy = -1
                        if keys[pygame.K_DOWN]: dy = 1
                        if keys[pygame.K_LEFT]: dx = -1
                        if keys[pygame.K_RIGHT]: dx = 1
                    elif self.role == 'fantome':
                        if keys[pygame.K_w]: dy = -1
                        if keys[pygame.K_s]: dy = 1
                        if keys[pygame.K_a]: dx = -1
                        if keys[pygame.K_d]: dx = 1

                    if dx != 0 and dy != 0:
                        dx *= 0.7071
                        dy *= 0.7071

                    if dx != 0 or dy != 0:
                        self.send_update(dx, dy)

            # --- AFFICHAGE ---
            self.screen.fill((15, 15, 22))

            # Dessiner les murs
            for wall in self.walls:
                pygame.draw.rect(self.screen, (50, 50, 65), 
                                (wall['x'], wall['y'], wall['width'], wall['height']))
                pygame.draw.rect(self.screen, (75, 75, 95), 
                                (wall['x'], wall['y'], wall['width'], wall['height']), 2)

            # Dessiner les joueurs selon leur rôle et leur visibilité POV
            for pid, p in self.players.items():
                if p.type == 'chasseur':
                    hx, hy = p.x, p.y
                    pygame.draw.circle(self.screen, (40, 50, 70), (int(hx + 10), int(hy + 10)), 10)
                    pygame.draw.circle(self.screen, (220, 120, 30), (int(hx + 10), int(hy + 10)), 7)
                    if getattr(p, 'lampe_on', False):
                        # Dessin simplifié du cône de lumière pour le réseau
                        pass
                    # UI batterie pour le chasseur
                    pygame.draw.rect(self.screen, (200, 200, 200), (680, 10, 100, 20), 2)
                    fill_w = int(getattr(p, 'batterie_lampe', 100) / 100 * 96)
                    pygame.draw.rect(self.screen, (0, 255, 0), (682, 12, fill_w, 16))

                elif p.type == 'fantome':
                    fx, fy = p.x, p.y
                    # Règle POV : Le fantôme se voit toujours lui-même. 
                    # Si on est le fantôme (pid == self.player_id), on s'affiche toujours. 
                    # Si on est le chasseur, on ne le voit que s'il est visible / éclairé.
                    is_ghost_self = (pid == self.player_id)
                    is_visible_by_hunter = getattr(p, 'visible', False)

                    if is_ghost_self or is_visible_by_hunter or self.role == 'fantome':
                        pygame.draw.circle(self.screen, (170, 200, 255), (int(fx + 10), int(fy + 8)), 9)
                        hp_text = self.font.render(f"Vie: {int(p.points_de_vie)}", True, (255, 120, 120))
                        self.screen.blit(hp_text, (fx - 8, fy - 22))

            if len(self.players) < 2:
                wait_text = self.font.render("En attente du second joueur dans le manoir...", True, (255, 255, 255))
                self.screen.blit(wait_text, (WIDTH // 2 - 180, HEIGHT // 2))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        self.client.close()

if __name__ == "__main__":
    ip = input("Entrez l'adresse IP du serveur (laissez vide pour localhost) : ").strip()
    if not ip:
        ip = 'localhost'
    game = NetworkGame(ip)
    game.run()