import pygame
import random
import heapq

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 900
CAR_WIDTH = 180
CAR_HEIGHT = 180
ENEMY_WIDTH = 180
ENEMY_HEIGHT = 180
LANE_WIDTH = SCREEN_WIDTH // 5
SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up display
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crash-athon")

# Load car image
car_img = pygame.image.load('car.png')
car_img = pygame.transform.scale(car_img, (CAR_WIDTH, CAR_HEIGHT))

# Load enemy image
enemy_img = pygame.image.load('enemy_car.png')
enemy_img = pygame.transform.scale(enemy_img, (ENEMY_WIDTH, ENEMY_HEIGHT))

# Game variables
car_x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
car_y = SCREEN_HEIGHT - CAR_HEIGHT - 10
score = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)

# Collision margin
collision_margin = 30
side_collision = 90

# Enemy count
NUM_ENEMIES = 3

def a_star(start_lane, target_lane):
    open_set = [(0, start_lane, [])]
    heapq.heapify(open_set)
    g_score = {i: float('inf') for i in range(5)}
    g_score[start_lane] = 0
    f_score = {i: float('inf') for i in range(5)}
    f_score[start_lane] = abs(start_lane - target_lane)
    
    while open_set:
        _, current, path = heapq.heappop(open_set)
        if current == target_lane:
            return path
        for next_lane in [current - 1, current + 1]:
            if 0 <= next_lane < 5:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[next_lane]:
                    g_score[next_lane] = tentative_g_score
                    f_score[next_lane] = tentative_g_score + abs(next_lane - target_lane)
                    heapq.heappush(open_set, (f_score[next_lane], next_lane, path + [next_lane]))
    return []

class EnemyCar:
    def __init__(self, other_enemies):
        self.x = random.choice([LANE_WIDTH * i + (LANE_WIDTH - ENEMY_WIDTH) // 2 for i in range(5)])
        self.y = -ENEMY_HEIGHT
        self.speed = SPEED
        self.path = []
        while any(abs(self.x - enemy.x) < ENEMY_WIDTH for enemy in other_enemies):
            self.x = random.choice([LANE_WIDTH * i + (LANE_WIDTH - ENEMY_WIDTH) // 2 for i in range(5)])

    def move_towards_player(self, player_x):
        player_lane = player_x // LANE_WIDTH
        current_lane = self.x // LANE_WIDTH
        if not self.path or current_lane != self.path[0]:
            self.path = a_star(current_lane, player_lane)
        if self.path:
            next_lane = self.path.pop(0)
            target_x = next_lane * LANE_WIDTH + (LANE_WIDTH - ENEMY_WIDTH) // 2
            if self.x < target_x:
                self.x += self.speed // 2
            elif self.x > target_x:
                self.x -= self.speed // 2
        self.y += self.speed

    def reset_position(self, other_enemies):
        self.x = random.choice([LANE_WIDTH * i + (LANE_WIDTH - ENEMY_WIDTH) // 2 for i in range(5)])
        self.y = -ENEMY_HEIGHT
        self.speed = SPEED
        self.path = []
        while any(abs(self.x - enemy.x) < ENEMY_WIDTH for enemy in other_enemies):
            self.x = random.choice([LANE_WIDTH * i + (LANE_WIDTH - ENEMY_WIDTH) // 2 for i in range(5)])

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def game_over_screen(win, score):
    win.fill(WHITE)
    draw_text('GAME OVER', font, BLACK, win, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
    draw_text(f'Score: {score}', font, BLACK, win, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text('Press any key to restart', font, BLACK, win, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def main():
    global car_x, car_y, score, SPEED

    # Reset game variables
    car_x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
    car_y = SCREEN_HEIGHT - CAR_HEIGHT - 10
    enemies = [EnemyCar([]) for _ in range(NUM_ENEMIES)]
    score = 0
    SPEED = 5

    run = True
    car_speed_x = 0
    car_speed_y = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and car_x > 0:
            car_speed_x = -SPEED
        elif keys[pygame.K_RIGHT] and car_x < SCREEN_WIDTH - CAR_WIDTH:
            car_speed_x = SPEED
        else:
            car_speed_x = 0
        
        if keys[pygame.K_UP] and car_y > 0:
            car_speed_y = -SPEED
        elif keys[pygame.K_DOWN] and car_y < SCREEN_HEIGHT - CAR_HEIGHT:
            car_speed_y = SPEED
        else:
            car_speed_y = 0

        car_x += car_speed_x
        car_y += car_speed_y

        win.fill(WHITE)

        # Draw lanes
        for i in range(1, 5):
            pygame.draw.line(win, BLACK, (LANE_WIDTH * i, 0), (LANE_WIDTH * i, SCREEN_HEIGHT), 5)

        # Draw car
        win.blit(car_img, (car_x, car_y))

        # Draw and move enemies
        for i, enemy in enumerate(enemies):
            other_enemies = [e for j, e in enumerate(enemies) if j != i]
            enemy.move_towards_player(car_x)
            win.blit(enemy_img, (enemy.x, enemy.y))
            if enemy.y > SCREEN_HEIGHT:
                enemy.reset_position(other_enemies)
                score += 1
                SPEED += 0.5  # Increase speed

            # Check collision
            if car_y < enemy.y + ENEMY_HEIGHT - collision_margin and car_y + CAR_HEIGHT > enemy.y + collision_margin:
                if car_x < enemy.x + ENEMY_WIDTH - collision_margin - side_collision and car_x + CAR_WIDTH > enemy.x + collision_margin + side_collision:
                    pygame.time.wait(2000)
                    game_over_screen(win, score)
                    clock.tick(500)
                    main()  # Restart the game

        # Display score
        draw_text(f'Score: {score}', font, BLACK, win, SCREEN_WIDTH // 2, 30)

        pygame.display.update()
        clock.tick(30)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
