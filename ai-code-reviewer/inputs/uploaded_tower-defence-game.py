import pygame

import math

import random


pygame.init()


# Constants

WIDTH, HEIGHT = 1000, 600

FPS = 60

WHITE = (255, 255, 255)

BLACK = (0, 0, 0)

RED = (255, 0, 0)

GREEN = (0, 255, 0)

BLUE = (0, 100, 255)

YELLOW = (255, 255, 0)

GRAY = (150, 150, 150)

DARK_GREEN = (0, 150, 0)

PURPLE = (150, 0, 150)


# Game setup

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()


# Path for enemies

path = [
    (0, 300),
    (200, 300),
    (200, 100),
    (400, 100),
    (400, 400),
    (600, 400),
    (600, 200),
    (800, 200),
    (800, 400),
    (1000, 400),
]


class Enemy:

    def __init__(self, health, speed, reward):

        self.x, self.y = path[0]

        self.health = health

        self.max_health = health

        self.speed = speed

        self.path_index = 0

        self.reward = reward

        self.radius = 12

    def move(self):

        if self.path_index < len(path) - 1:

            target_x, target_y = path[self.path_index + 1]

            dx = target_x - self.x

            dy = target_y - self.y

            dist = math.sqrt(dx**2 + dy**2)

            if dist < self.speed:

                self.path_index += 1

            else:

                self.x += (dx / dist) * self.speed

                self.y += (dy / dist) * self.speed

            return False

        return True

    def draw(self):

        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

        # Health bar

        bar_width = 30

        bar_height = 4

        health_ratio = self.health / self.max_health

        pygame.draw.rect(screen, RED, (self.x - 15, self.y - 20, bar_width, bar_height))

        pygame.draw.rect(
            screen,
            GREEN,
            (self.x - 15, self.y - 20, bar_width * health_ratio, bar_height),
        )


class Tower:

    def __init__(self, x, y, tower_type):

        self.x = x

        self.y = y

        self.type = tower_type

        self.level = 1

        if tower_type == "basic":

            self.damage = 20

            self.range = 120

            self.fire_rate = 30

            self.cost = 100

            self.upgrade_cost = 80

            self.color = BLUE

        elif tower_type == "sniper":

            self.damage = 50

            self.range = 200

            self.fire_rate = 60

            self.cost = 200

            self.upgrade_cost = 150

            self.color = PURPLE

        elif tower_type == "rapid":

            self.damage = 10

            self.range = 100

            self.fire_rate = 10

            self.cost = 150

            self.upgrade_cost = 100

            self.color = YELLOW

        self.cooldown = 0

        self.target = None

    def upgrade(self):

        self.level += 1

        self.damage = int(self.damage * 1.5)

        self.range = int(self.range * 1.1)

        self.upgrade_cost = int(self.upgrade_cost * 1.5)

    def find_target(self, enemies):

        closest = None

        min_dist = self.range + 1

        for enemy in enemies:

            dist = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)

            if dist < self.range and dist < min_dist:

                closest = enemy

                min_dist = dist

        self.target = closest

    def shoot(self):

        if self.target and self.cooldown == 0:

            self.target.health -= self.damage

            self.cooldown = self.fire_rate

            return True

        return False

    def update(self):

        if self.cooldown > 0:

            self.cooldown -= 1

    def draw(self, selected=False):

        # Tower body

        pygame.draw.circle(screen, self.color, (self.x, self.y), 20)

        pygame.draw.circle(screen, BLACK, (self.x, self.y), 20, 2)

        # Level indicator

        font = pygame.font.Font(None, 20)

        level_text = font.render(str(self.level), True, WHITE)

        screen.blit(level_text, (self.x - 5, self.y - 8))

        # Range indicator if selected

        if selected:

            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

            pygame.draw.circle(s, (0, 100, 255, 50), (self.x, self.y), self.range)

            screen.blit(s, (0, 0))

        # Shooting line

        if self.target and self.cooldown > self.fire_rate - 5:

            pygame.draw.line(
                screen,
                self.color,
                (self.x, self.y),
                (int(self.target.x), int(self.target.y)),
                2,
            )


class Game:

    def __init__(self):

        self.money = 400

        self.lives = 20

        self.wave = 1

        self.enemies = []

        self.towers = []

        self.selected_tower = None

        self.placing_tower = None

        self.wave_started = False

        self.enemies_to_spawn = 0

        self.spawn_timer = 0

        self.wave_complete = True

    def spawn_wave(self):

        self.wave_started = True

        self.wave_complete = False

        self.enemies_to_spawn = 5 + self.wave * 3

        self.spawn_timer = 0

    def spawn_enemy(self):

        # Enemies get stronger each wave

        health = 50 + self.wave * 20

        speed = 1 + self.wave * 0.1

        reward = 10 + self.wave * 2

        self.enemies.append(Enemy(health, speed, reward))

    def update(self):

        # Spawn enemies

        if self.wave_started and self.enemies_to_spawn > 0:

            self.spawn_timer += 1

            if self.spawn_timer >= 60:

                self.spawn_enemy()

                self.enemies_to_spawn -= 1

                self.spawn_timer = 0

        # Move enemies

        for enemy in self.enemies[:]:

            reached_end = enemy.move()

            if reached_end:

                self.lives -= 1

                self.enemies.remove(enemy)

            elif enemy.health <= 0:

                self.money += enemy.reward

                self.enemies.remove(enemy)

        # Update towers

        for tower in self.towers:

            tower.find_target(self.enemies)

            tower.shoot()

            tower.update()

        # Check wave complete

        if self.wave_started and self.enemies_to_spawn == 0 and len(self.enemies) == 0:

            self.wave_started = False

            self.wave_complete = True

    def draw(self):

        screen.fill((34, 139, 34))

        # Draw path

        pygame.draw.lines(screen, GRAY, False, path, 40)

        # Draw towers

        for tower in self.towers:

            selected = tower == self.selected_tower

            tower.draw(selected)

        # Draw enemies

        for enemy in self.enemies:

            enemy.draw()

        # Draw placing tower preview

        if self.placing_tower:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            if mouse_y < HEIGHT - 100:

                pygame.draw.circle(
                    screen, self.placing_tower.color + (100,), (mouse_x, mouse_y), 20
                )

                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

                pygame.draw.circle(
                    s, (0, 100, 255, 30), (mouse_x, mouse_y), self.placing_tower.range
                )

                screen.blit(s, (0, 0))

        # Draw UI

        self.draw_ui()

    def draw_ui(self):

        # Bottom panel

        pygame.draw.rect(screen, (100, 100, 100), (0, HEIGHT - 100, WIDTH, 100))

        font = pygame.font.Font(None, 32)

        # Stats

        money_text = font.render(f"Money: ${self.money}", True, YELLOW)

        lives_text = font.render(f"Lives: {self.lives}", True, RED)

        wave_text = font.render(f"Wave: {self.wave}", True, WHITE)

        screen.blit(money_text, (20, HEIGHT - 80))

        screen.blit(lives_text, (20, HEIGHT - 50))

        screen.blit(wave_text, (200, HEIGHT - 65))

        # Tower buttons

        btn_font = pygame.font.Font(None, 24)

        towers_info = [
            ("Basic", 100, BLUE, 400),
            ("Rapid", 150, YELLOW, 550),
            ("Sniper", 200, PURPLE, 700),
        ]

        for name, cost, color, x in towers_info:

            pygame.draw.rect(screen, color, (x, HEIGHT - 80, 120, 60))

            pygame.draw.rect(screen, BLACK, (x, HEIGHT - 80, 120, 60), 2)

            name_text = btn_font.render(name, True, WHITE)

            cost_text = btn_font.render(f"${cost}", True, WHITE)

            screen.blit(name_text, (x + 10, HEIGHT - 70))

            screen.blit(cost_text, (x + 10, HEIGHT - 45))

        # Wave button

        if self.wave_complete:

            pygame.draw.rect(screen, GREEN, (850, HEIGHT - 80, 120, 60))

            pygame.draw.rect(screen, BLACK, (850, HEIGHT - 80, 120, 60), 2)

            wave_btn_text = btn_font.render("Start Wave", True, WHITE)

            screen.blit(wave_btn_text, (860, HEIGHT - 55))

        # Selected tower info

        if self.selected_tower:

            info_font = pygame.font.Font(None, 24)

            info_x = WIDTH - 200

            info_y = 20

            pygame.draw.rect(screen, (50, 50, 50), (info_x - 10, info_y - 10, 190, 120))

            pygame.draw.rect(screen, WHITE, (info_x - 10, info_y - 10, 190, 120), 2)

            texts = [
                f"Level: {self.selected_tower.level}",
                f"Damage: {self.selected_tower.damage}",
                f"Range: {self.selected_tower.range}",
                f"Upgrade: ${self.selected_tower.upgrade_cost}",
            ]

            for i, text in enumerate(texts):

                rendered = info_font.render(text, True, WHITE)

                screen.blit(rendered, (info_x, info_y + i * 25))

            # Upgrade button

            pygame.draw.rect(screen, DARK_GREEN, (info_x - 5, info_y + 90, 80, 25))

            pygame.draw.rect(screen, WHITE, (info_x - 5, info_y + 90, 80, 25), 2)

            upgrade_text = info_font.render("Upgrade", True, WHITE)

            screen.blit(upgrade_text, (info_x, info_y + 92))

            # Sell button

            pygame.draw.rect(screen, RED, (info_x + 85, info_y + 90, 50, 25))

            pygame.draw.rect(screen, WHITE, (info_x + 85, info_y + 90, 50, 25), 2)

            sell_text = info_font.render("Sell", True, WHITE)

            screen.blit(sell_text, (info_x + 93, info_y + 92))

    def handle_click(self, pos):

        x, y = pos

        # Check tower buttons

        if y > HEIGHT - 100:

            if 400 <= x <= 520 and self.money >= 100:

                self.placing_tower = Tower(0, 0, "basic")

            elif 550 <= x <= 670 and self.money >= 150:

                self.placing_tower = Tower(0, 0, "rapid")

            elif 700 <= x <= 820 and self.money >= 200:

                self.placing_tower = Tower(0, 0, "sniper")

            elif 850 <= x <= 970 and self.wave_complete:

                self.wave += 1

                self.spawn_wave()

        elif self.selected_tower:

            # Check upgrade/sell buttons

            info_x = WIDTH - 200

            info_y = 20

            if info_x - 5 <= x <= info_x + 75 and info_y + 90 <= y <= info_y + 115:

                # Upgrade

                if self.money >= self.selected_tower.upgrade_cost:

                    self.money -= self.selected_tower.upgrade_cost

                    self.selected_tower.upgrade()

            elif info_x + 85 <= x <= info_x + 135 and info_y + 90 <= y <= info_y + 115:

                # Sell

                self.money += self.selected_tower.cost // 2

                self.towers.remove(self.selected_tower)

                self.selected_tower = None

        else:

            # Select tower

            self.selected_tower = None

            for tower in self.towers:

                dist = math.sqrt((tower.x - x) ** 2 + (tower.y - y) ** 2)

                if dist < 20:

                    self.selected_tower = tower

                    break

    def place_tower(self, pos):

        x, y = pos

        if y < HEIGHT - 100 and self.money >= self.placing_tower.cost:

            # Check if too close to path or other towers

            valid = True

            for px, py in path:

                if math.sqrt((x - px) ** 2 + (y - py) ** 2) < 50:

                    valid = False

                    break

            for tower in self.towers:

                if math.sqrt((x - tower.x) ** 2 + (y - tower.y) ** 2) < 45:

                    valid = False

                    break

            if valid:

                self.placing_tower.x = x

                self.placing_tower.y = y

                self.towers.append(self.placing_tower)

                self.money -= self.placing_tower.cost

                self.placing_tower = None


def main():

    game = Game()

    running = True

    while running:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if game.placing_tower:

                    game.place_tower(event.pos)

                else:

                    game.handle_click(event.pos)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    game.placing_tower = None

                    game.selected_tower = None

        if game.lives <= 0:

            font = pygame.font.Font(None, 72)

            text = font.render("GAME OVER!", True, RED)

            screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))

            pygame.display.flip()

            pygame.time.wait(3000)

            running = False

            continue

        game.update()

        game.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":

    main()
