# server.py
import socket
import threading
import pickle
import time
import random
from entities import Chasseur, Fantome

HOST = '0.0.0.0' 
PORT = 12337

clients = []
players = {}
next_player_id = 1
game_started = False
fantome_id = None
start_time = None

# Définition des 4 maps identiques au jeu solo
borders = [
    {'x': 0, 'y': 0, 'width': 800, 'height': 20},
    {'x': 0, 'y': 0, 'width': 20, 'height': 600},
    {'x': 780, 'y': 0, 'width': 20, 'height': 600},
    {'x': 0, 'y': 580, 'width': 800, 'height': 20}
]

map_1 = borders + [
    {'x': 300, 'y': 100, 'width': 200, 'height': 20},
    {'x': 100, 'y': 300, 'width': 20, 'height': 200},
    {'x': 400, 'y': 400, 'width': 200, 'height': 20},
    {'x': 200, 'y': 200, 'width': 20, 'height': 150},
    {'x': 500, 'y': 200, 'width': 20, 'height': 150},
]
map_2 = borders + [
    {'x': 200, 'y': 0, 'width': 20, 'height': 400},
    {'x': 500, 'y': 200, 'width': 20, 'height': 400},
    {'x': 350, 'y': 150, 'width': 150, 'height': 20},
    {'x': 100, 'y': 480, 'width': 200, 'height': 20},
]
map_3 = borders + [
    {'x': 150, 'y': 150, 'width': 500, 'height': 20},
    {'x': 150, 'y': 300, 'width': 500, 'height': 20},
    {'x': 150, 'y': 450, 'width': 500, 'height': 20},
]
map_4 = borders + [
    {'x': 200, 'y': 150, 'width': 60, 'height': 60},
    {'x': 540, 'y': 150, 'width': 60, 'height': 60},
    {'x': 200, 'y': 390, 'width': 60, 'height': 60},
    {'x': 540, 'y': 390, 'width': 60, 'height': 60},
    {'x': 370, 'y': 270, 'width': 60, 'height': 60},
]

walls = random.choice([map_1, map_2, map_3, map_4])

def collides_with_walls(x, y):
    player_size = 20
    for wall in walls:
        if (x < wall['x'] + wall['width'] and
            x + player_size > wall['x'] and
            y < wall['y'] + wall['height'] and
            y + player_size > wall['y']):
            return True
    return False

def get_random_valid_position():
    while True:
        x = random.randint(50, 730)
        y = random.randint(50, 530)
        if not collides_with_walls(x, y):
            return x, y

def broadcast(message):
    data = pickle.dumps(message)
    for client in clients:
        try:
            client.send(data)
        except:
            pass

def handle_client(client_socket, player_id):
    global game_started
    while True:
        try:
            packet = client_socket.recv(2048)
            if not packet:
                break
            message = pickle.loads(packet)
            
            if message['type'] == 'update_position':
                dx = message['dx']
                dy = message['dy']
                speed = message['speed']
                
                p = players[player_id]
                new_x = p.x + dx * speed
                new_y = p.y + dy * speed
                if not collides_with_walls(new_x, new_y):
                    p.x = new_x
                    p.y = new_y
                
                if 'lampe_on' in message:
                    p.lampe_on = message['lampe_on']
                if 'batterie_lampe' in message:
                    p.batterie_lampe = message['batterie_lampe']
                if 'points_de_vie' in message:
                    p.points_de_vie = message['points_de_vie']
                if not p.alive:
                    p.alive = message['alive']

                broadcast({
                    'type': 'game_state',
                    'players': players,
                    'walls': walls
                })

        except Exception as e:
            print(f"Erreur client {player_id}: {e}")
            break

    clients.remove(client_socket)
    client_socket.close()
    if player_id in players:
        del players[player_id]
    broadcast({'type': 'game_state', 'players': players, 'walls': walls})

def main():
    global next_player_id, fantome_id, game_started, start_time
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"Serveur démarré sur le port {PORT} avec une map aléatoire...")

    hx, hy = get_random_valid_position()
    fx, fy = get_random_valid_position()
    while abs(hx - fx) < 100 and abs(hy - fy) < 100:
        fx, fy = get_random_valid_position()

    while True:
        client_socket, addr = server.accept()
        print(f"Connexion établie avec {addr}")
        clients.append(client_socket)

        player_id = next_player_id
        next_player_id += 1

        # Joueur 1 = Fantôme, Joueur 2 = Chasseur
        if fantome_id is None:
            players[player_id] = Fantome(fx, fy)
            fantome_id = player_id
            role = 'fantome'
        else:
            players[player_id] = Chasseur(hx, hy)
            role = 'chasseur'
            game_started = True
            start_time = time.time()

        client_socket.send(pickle.dumps({
            'type': 'init',
            'player_id': player_id,
            'role': role,
            'players': players,
            'walls': walls
        }))

        broadcast({
            'type': 'game_state',
            'players': players,
            'walls': walls
        })

        thread = threading.Thread(target=handle_client, args=(client_socket, player_id))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()