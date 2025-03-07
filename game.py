# game.py
import pygame
import math
import random
import os
from entities import Chasseur, Fantome, BatteryRecharge

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Ghost Chase")
        self.clock = pygame.time.Clock()

        # Initialize game state
        self.chasseur = Chasseur(100, 100)
        self.fantome = Fantome(400, 400)
        self.players = {1: self.chasseur, 2: self.fantome}

        self.game_over = False
        self.winner = None
        self.generate_walls()
        self.battery_recharge = None
        self.last_spawn_time = pygame.time.get_ticks()
        self.recharge_interval = 15000
        self.derniere_utilisation_lampe = 0

        # Load images with error handling
        self.load_images()
        
        # Font for UI elements
        self.font = pygame.font.Font(None, 24)

    def load_images(self):
        # Default to colored rectangles if images not found
        self.ghost_image = pygame.Surface((20, 20))
        self.ghost_image.fill((200, 200, 255))
        self.hunter_image = pygame.Surface((20, 20))
        self.hunter_image.fill((255, 200, 100))
        self.background_image = pygame.Surface((800, 600))
        self.background_image.fill((50, 50, 50))
        
        # Try to load images if they exist
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            img_paths = {
                "ghost": ["fantome.png", "assets/fantome.png"],
                "hunter": ["chasseur.png", "assets/chasseur.png"],
                "background": ["sol.jpg", "assets/sol.jpg", "background.jpg", "assets/background.jpg"]
            }
            
            for entity, paths in img_paths.items():
                for path in paths:
                    try:
                        full_path = os.path.join(current_dir, path)
                        if os.path.exists(full_path):
                            if entity == "ghost":
                                self.ghost_image = pygame.image.load(full_path)
                            elif entity == "hunter":
                                self.hunter_image = pygame.image.load(full_path)
                            elif entity == "background":
                                self.background_image = pygame.image.load(full_path)
                            break
                    except pygame.error:
                        continue
        except Exception as e:
            print(f"Error loading images: {e}")

    def generate_walls(self):
        self.walls = [
            {'x': 300, 'y': 100, 'width': 200, 'height': 20},
            {'x': 100, 'y': 300, 'width': 20, 'height': 200},
            {'x': 400, 'y': 400, 'width': 200, 'height': 20},
            {'x': 200, 'y': 200, 'width': 20, 'height': 150},
            {'x': 500, 'y': 200, 'width': 20, 'height': 150},
            {'x': 250, 'y': 100, 'width': 20, 'height': 100},
            {'x': 450, 'y': 100, 'width': 20, 'height': 100},
            # Border walls
            {'x': 0, 'y': 0, 'width': 800, 'height': 20},
            {'x': 0, 'y': 0, 'width': 20, 'height': 600},
            {'x': 780, 'y': 0, 'width': 20, 'height': 600},
            {'x': 0, 'y': 580, 'width': 800, 'height': 20}
        ]

    def update(self):
        current_time = pygame.time.get_ticks()

        # Update hunter's flashlight
        if self.chasseur.lampe_on:
            if not self.chasseur.use_light():
                self.chasseur.lampe_on = False
        
        # Spawn battery recharge if needed
        if not self.battery_recharge and current_time - self.last_spawn_time > self.recharge_interval:
            self.last_spawn_time = current_time
            valid_pos = False
            while not valid_pos:
                x = random.randint(50, 750)
                y = random.randint(50, 550)
                if not self.collides_with_walls(x, y):
                    valid_pos = True
            self.battery_recharge = BatteryRecharge(x, y)
            
        # Remove battery recharge if expired
        if self.battery_recharge and current_time - self.battery_recharge.spawn_time > self.battery_recharge.duration:
            self.battery_recharge = None

        # Check if game is over
        if not self.fantome.alive:
            self.game_over = True
            self.winner = "Chasseur"
        elif not self.chasseur.alive:
            self.game_over = True
            self.winner = "Fantôme"

    def move_player(self, player, dx, dy):
        new_x = player.x + dx * player.speed
        new_y = player.y + dy * player.speed
        if not self.collides_with_walls(new_x, new_y):
            player.x = new_x
            player.y = new_y
        self.check_collision(player)

    def collides_with_walls(self, x, y):
        player_size = 20  # Approximate player size
        for wall in self.walls:
            if (x < wall['x'] + wall['width'] and
                x + player_size > wall['x'] and
                y < wall['y'] + wall['height'] and
                y + player_size > wall['y']):
                return True
        return False

    def draw_light_cone(self, screen, player):
        light_color = (255, 255, 150, 100)  # Added transparency
        light_radius = 200
        light_angle = 60  # Wider angle for better playability
        
        # Get player direction
        dx, dy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        
        # Calculate angle based on direction
        if dx == 0 and dy == 0:
            angle = 0  # Default direction
        elif dx == 0:
            angle = 90 if dy > 0 else 270
        elif dy == 0:
            angle = 0 if dx > 0 else 180
        else:
            angle = math.degrees(math.atan2(dy, dx))
            
        # Convert to radians
        angle_rad = math.radians(angle)
        half_angle_rad = math.radians(light_angle / 2)
        
        # Create a semi-transparent surface for the light
        light_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        
        # Draw the light cone
        start_pos = (player.x + 10, player.y + 10)
        points = [start_pos]
        
        # Add points along the arc
        for i in range(21):  # More points for smoother cone
            angle_i = angle_rad - half_angle_rad + i * (2 * half_angle_rad / 20)
            end_pos = (player.x + 10 + light_radius * math.cos(angle_i),
                        player.y + 10 + light_radius * math.sin(angle_i))
            points.append(end_pos)
            
        # Draw the light cone on the transparent surface
        pygame.draw.polygon(light_surface, light_color, points)
        screen.blit(light_surface, (0, 0))
        
        # Check if ghost is in light
        ghost_center_x = self.fantome.x + 10
        ghost_center_y = self.fantome.y + 10
        
        # Check if ghost is in range
        distance = math.sqrt((player.x + 10 - ghost_center_x)**2 + (player.y + 10 - ghost_center_y)**2)
        if distance > light_radius:
            return False
            
        # Check if ghost is in the cone angle
        ghost_angle = math.atan2(ghost_center_y - (player.y + 10), ghost_center_x - (player.x + 10))
        angle_diff = abs((ghost_angle - angle_rad + math.pi) % (2 * math.pi) - math.pi)
        
        if angle_diff <= half_angle_rad:
            self.fantome.visible = True
            return True
        return False

    def draw_battery(self, screen, player):
        battery_width = 100
        battery_height = 20
        battery_x = screen.get_width() - battery_width - 10
        battery_y = 10
        border_color = (200, 200, 200)
        
        # Choose color based on battery level
        if player.batterie_lampe > 70:
            battery_color = (0, 255, 0)  # Green
        elif player.batterie_lampe > 30:
            battery_color = (255, 255, 0)  # Yellow
        else:
            battery_color = (255, 0, 0)  # Red
            
        # Draw battery outline
        pygame.draw.rect(screen, border_color, (battery_x, battery_y, battery_width, battery_height), 2)
        
        # Draw battery fill
        fill_width = int(player.batterie_lampe / 100 * (battery_width - 4))
        pygame.draw.rect(screen, battery_color, (battery_x + 2, battery_y + 2, fill_width, battery_height - 4))
        
        # Draw battery text
        battery_text = self.font.render(f"{int(player.batterie_lampe)}%", True, (255, 255, 255))
        screen.blit(battery_text, (battery_x + battery_width/2 - 20, battery_y + 2))

    def draw_ghost_detector(self, screen, player, ghost):
        max_distance = 400
        detector_width = 150
        detector_height = 20
        detector_x = 10
        detector_y = 10
        border_color = (200, 200, 200)
        
        # Calculate distance between hunter and ghost
        distance = math.sqrt((player.x - ghost.x) ** 2 + (player.y - ghost.y) ** 2)
        distance = min(distance, max_distance)
        
        # Choose color based on proximity
        if distance < 100:
            detector_color = (255, 0, 0)  # Red - very close
        elif distance < 200:
            detector_color = (255, 165, 0)  # Orange - medium distance
        else:
            detector_color = (0, 255, 0)  # Green - far away
            
        # Calculate fill width inversely proportional to distance
        fill_width = int((1 - distance / max_distance) * (detector_width - 4))
        
        # Draw detector outline
        pygame.draw.rect(screen, border_color, (detector_x, detector_y, detector_width, detector_height), 2)
        
        # Draw detector fill
        pygame.draw.rect(screen, detector_color, (detector_x + 2, detector_y + 2, fill_width, detector_height - 4))
        
        # Draw detector text
        detector_text = self.font.render("Ghost Detector", True, (255, 255, 255))
        screen.blit(detector_text, (detector_x, detector_y + detector_height + 2))

    def check_collision(self, player):
        # Check hunter-ghost collision
        if player.type == 'chasseur':
            # Check if flashlight hits ghost
            if player.lampe_on:
                ghost_in_light = self.draw_light_cone(self.screen, player)
                if ghost_in_light:
                    self.fantome.take_damage(0.05)  # Reduced damage rate for better gameplay
                    
            # Check if ghost caught hunter
            distance = math.sqrt((player.x - self.fantome.x) ** 2 + (player.y - self.fantome.y) ** 2)
            if distance < 20:  # Adjusted collision distance
                self.chasseur.alive = False
                
        # Check if hunter collects battery
        if player.type == 'chasseur' and self.battery_recharge:
            distance = math.sqrt((player.x - self.battery_recharge.x) ** 2 + 
                                 (player.y - self.battery_recharge.y) ** 2)
            if distance < 30:
                player.batterie_lampe = min(100, player.batterie_lampe + 50)
                self.battery_recharge = None

    def draw(self):
        # Draw background
        self.screen.blit(self.background_image, (0, 0))
        
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, (180, 180, 180), 
                            (wall['x'], wall['y'], wall['width'], wall['height']))
            
        # Draw battery recharge
        if self.battery_recharge:
            pygame.draw.circle(self.screen, (0, 255, 255), 
                              (self.battery_recharge.x, self.battery_recharge.y), 10)
            
        # Draw Hunter and light cone if active
        if self.chasseur.alive:
            self.screen.blit(self.hunter_image, (self.chasseur.x, self.chasseur.y))
            if self.chasseur.lampe_on:
                self.draw_light_cone(self.screen, self.chasseur)
                
        # Draw UI elements for Hunter
        self.draw_battery(self.screen, self.chasseur)
        self.draw_ghost_detector(self.screen, self.chasseur, self.fantome)
            
        # Draw Ghost only if visible (in light) or for the ghost player
        if self.fantome.alive:
            if self.fantome.visible:
                self.screen.blit(self.ghost_image, (self.fantome.x, self.fantome.y))
                # Display ghost health
                health_text = self.font.render(f"Vie: {int(self.fantome.points_de_vie)}", True, (255, 255, 255))
                self.screen.blit(health_text, (self.fantome.x, self.fantome.y - 20))
                
            # Ghost is always visible to itself (for ghost player)
            # In a networked game, you'd only show this to the ghost player
            pygame.draw.rect(self.screen, (100, 100, 255, 128), 
                            (self.fantome.x, self.fantome.y, 20, 20), 1)
                
        # Draw game over screen if game is over
        if self.game_over:
            self.draw_game_over()
            
        # Update display
        pygame.display.flip()
        
    def draw_game_over(self):
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over message
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, 
                        (400 - game_over_text.get_width() // 2, 250 - game_over_text.get_height() // 2))
        
        # Draw winner
        winner_font = pygame.font.Font(None, 48)
        winner_text = winner_font.render(f"{self.winner} wins!", True, (255, 255, 255))
        self.screen.blit(winner_text, 
                        (400 - winner_text.get_width() // 2, 330 - winner_text.get_height() // 2))
        
        # Draw restart prompt
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render("Press R to restart or Q to quit", True, (200, 200, 200))
        self.screen.blit(restart_text, 
                        (400 - restart_text.get_width() // 2, 400 - restart_text.get_height() // 2))

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    pygame.quit()
                    return
                    
                elif event.type == pygame.KEYDOWN:
                    # Toggle flashlight
                    if event.key == pygame.K_l and pygame.time.get_ticks() - self.derniere_utilisation_lampe > 500:
                        self.chasseur.lampe_on = not self.chasseur.lampe_on
                        self.derniere_utilisation_lampe = pygame.time.get_ticks()
            
            # Player movement
            keys = pygame.key.get_pressed()
            
            # Hunter controls
            hunter_dx, hunter_dy = 0, 0
            if keys[pygame.K_UP]: hunter_dy = -1
            if keys[pygame.K_DOWN]: hunter_dy = 1
            if keys[pygame.K_LEFT]: hunter_dx = -1
            if keys[pygame.K_RIGHT]: hunter_dx = 1
            
            # Apply diagonal movement with normalized speed
            if hunter_dx != 0 and hunter_dy != 0:
                hunter_dx *= 0.7071  # 1/sqrt(2)
                hunter_dy *= 0.7071
                
            self.move_player(self.chasseur, hunter_dx, hunter_dy)
            
            # Ghost controls
            ghost_dx, ghost_dy = 0, 0
            if keys[pygame.K_w]: ghost_dy = -1
            if keys[pygame.K_s]: ghost_dy = 1
            if keys[pygame.K_a]: ghost_dx = -1
            if keys[pygame.K_d]: ghost_dx = 1
            
            # Apply diagonal movement with normalized speed
            if ghost_dx != 0 and ghost_dy != 0:
                ghost_dx *= 0.7071
                ghost_dy *= 0.7071
                
            self.move_player(self.fantome, ghost_dx, ghost_dy)
            
            # Update game state
            self.update()
            
            # Draw frame
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Game over loop for restart option
        restart = False
        while not restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
                        self.__init__()
                        self.run()
                        return
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        return
            
            # Draw game over screen
            self.draw()
            self.clock.tick(30)

if __name__ == "__main__":
    game = Game()
    game.run()