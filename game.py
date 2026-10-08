"""Wolkensprung: a self-contained platform game, with no external assets."""
import os
import sys

if "--smoke-test" in sys.argv:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

WIDTH, HEIGHT = 960, 540
WORLD = 3600
SKY = (135, 206, 235)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wolkensprung")
        self.font = pygame.font.Font(None, 30)
        self.big = pygame.font.Font(None, 66)
        self.clock = pygame.time.Clock()
        self.level = 0
        self.score = 0
        self.load_level()
        self.state = "title"

    def load_level(self):
        self.platforms = [pygame.Rect(x, 460, w, 100) for x, w in
                          [(0, 680), (800, 640), (1570, 660), (2370, 1230)]]
        self.platforms += [pygame.Rect(x, y, w, 22) for x, y, w in
                           [(280, 355, 180), (530, 280, 140), (930, 355, 180),
                            (1240, 295, 160), (1690, 360, 180), (1950, 280, 190),
                            (2470, 355, 180), (2730, 285, 190), (3050, 355, 180)]]
        self.coins = [pygame.Rect(p.x + i, p.y - 38, 18, 22)
                      for p in self.platforms[4:] for i in range(20, p.w - 10, 35)]
        self.enemies = [{"rect": pygame.Rect(x, 432, 32, 28), "x": float(x),
                         "dir": 1, "left": x - 70, "right": x + 100}
                        for x in (480, 1080, 1800, 2600, 3160)]
        self.checkpoint = 60
        self.lives = 3
        self.timer = 0
        self.invincible = 0
        self.camera = 0
        self.state = "play"
        self.spawn()

    def spawn(self):
        self.player = pygame.Rect(self.checkpoint, 390, 28, 42)
        self.x, self.y = float(self.player.x), float(self.player.y)
        self.vy = 0
        self.grounded = False
        self.coyote = 0
        self.jump_buffer = 0

    def hurt(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "over"
        else:
            self.spawn()
            self.invincible = 1.5

    def update(self, dt, move=0, jump=False, held=False, sprint=False):
        if self.state != "play":
            return
        self.timer += dt
        self.invincible = max(0, self.invincible - dt)
        self.coyote = 0.1 if self.grounded else max(0, self.coyote - dt)
        self.jump_buffer = 0.12 if jump else max(0, self.jump_buffer - dt)
        if self.jump_buffer and self.coyote:
            self.vy = -590
            self.grounded = False
            self.coyote = self.jump_buffer = 0
        if not held and self.vy < -240:
            self.vy = -240
        self.x += move * (340 if sprint else 235) * dt
        self.player.x = round(self.x)
        for platform in self.platforms:
            if self.player.colliderect(platform):
                if move > 0:
                    self.player.right = platform.left
                elif move < 0:
                    self.player.left = platform.right
                self.x = float(self.player.x)
        self.x = max(0, min(WORLD - self.player.w, self.x))
        self.player.x = round(self.x)
        old_bottom = self.player.bottom
        self.vy = min(950, self.vy + 1550 * dt)
        self.y += self.vy * dt
        self.player.y = round(self.y)
        self.grounded = False
        for platform in self.platforms:
            if self.player.colliderect(platform):
                if self.vy >= 0:
                    self.player.bottom = platform.top
                    self.grounded = True
                else:
                    self.player.top = platform.bottom
                self.y = float(self.player.y)
                self.vy = 0
        for coin in self.coins[:]:
            if self.player.colliderect(coin):
                self.coins.remove(coin)
                self.score += 10
        for enemy in self.enemies[:]:
            enemy["x"] += enemy["dir"] * (65 + self.level * 25) * dt
            if enemy["x"] > enemy["right"] or enemy["x"] < enemy["left"]:
                enemy["dir"] *= -1
            enemy["rect"].x = round(enemy["x"])
            if self.player.colliderect(enemy["rect"]):
                if self.vy > 0 and old_bottom <= enemy["rect"].top + 12:
                    self.enemies.remove(enemy)
                    self.vy = -400
                    self.score += 50
                elif not self.invincible:
                    self.hurt()
                    break
        if self.player.top > HEIGHT + 100:
            self.hurt()
        if self.player.x > 1660:
            self.checkpoint = 1640
        if self.player.x >= 3440 and self.state == "play":
            self.score += 100
            self.state = "win" if self.level == 2 else "clear"
        self.camera = max(0, min(WORLD - WIDTH, self.player.centerx - WIDTH // 3))

    def text(self, message, x, y, font=None, color=(27, 42, 63)):
        self.screen.blit((font or self.font).render(message, True, color), (x, y))

    def draw(self):
        self.screen.fill(SKY if self.level != 2 else (185, 173, 224))
        for i in range(10):
            x = i * 420 - int(self.camera * 0.25)
            pygame.draw.polygon(self.screen, (111, 175, 147),
                                [(x - 170, 460), (x + 90, 210), (x + 320, 460)])
            pygame.draw.ellipse(self.screen, (247, 250, 255), (x, 75 + i % 3 * 25, 110, 35))
        def rect(r):
            return r.move(-self.camera, 0)
        for p in self.platforms:
            pygame.draw.rect(self.screen, (142, 92, 61), rect(p), border_radius=3)
            pygame.draw.rect(self.screen, (69, 163, 86), rect(pygame.Rect(p.x, p.y, p.w, 9)))
        for coin in self.coins:
            pygame.draw.ellipse(self.screen, (255, 204, 42), rect(coin))
            pygame.draw.ellipse(self.screen, (255, 244, 150), rect(coin.inflate(-9, -5)))
        for enemy in self.enemies:
            r = rect(enemy["rect"])
            pygame.draw.rect(self.screen, (137, 63, 148), r, border_radius=10)
            for offset in (7, 21):
                pygame.draw.circle(self.screen, (255, 255, 255), (r.x + offset, r.y + 9), 5)
                pygame.draw.circle(self.screen, (30, 25, 45), (r.x + offset, r.y + 10), 2)
        for x, activated in [(1660, self.checkpoint != 60), (3460, True)]:
            pygame.draw.rect(self.screen, (245, 245, 230), (x - self.camera, 310, 5, 150))
            pygame.draw.polygon(self.screen, (255, 166, 48) if x == 1660 else (65, 184, 104),
                                [(x - self.camera + 5, 310), (x - self.camera + 65, 329),
                                 (x - self.camera + 5, 350)])
            if x == 1660 and activated:
                self.text("Checkpoint", x - self.camera - 40, 275)
        if not self.invincible or int(self.timer * 12) % 2 == 0:
            r = rect(self.player)
            pygame.draw.rect(self.screen, (36, 84, 153), r, border_radius=7)
            pygame.draw.rect(self.screen, (255, 199, 133), (r.x + 3, r.y + 5, 22, 18), border_radius=5)
            pygame.draw.rect(self.screen, (235, 108, 48), (r.x - 3, r.y, 34, 8), border_radius=3)
            pygame.draw.circle(self.screen, (30, 35, 50), (r.x + 19, r.y + 12), 2)
        pygame.draw.rect(self.screen, (245, 249, 239), (14, 12, 480, 42), border_radius=12)
        self.text(f"Level {self.level + 1}/3    Leben: {self.lives}    Punkte: {self.score}", 28, 23)
        self.text("A/D: laufen   Space: springen   Shift: rennen   P: Pause", 22, HEIGHT - 30)
        if self.state != "play":
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((12, 26, 48, 185))
            self.screen.blit(shade, (0, 0))
            titles = {"title": "Wolkensprung", "pause": "Pause", "over": "Noch ein Versuch?",
                      "clear": "Level geschafft!", "win": "Du hast gewonnen!"}
            title = self.big.render(titles[self.state], True, (255, 227, 115))
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 205)))
            hint = "P: weiter" if self.state == "pause" else "Enter: weiter    R: Neustart    Esc: beenden"
            self.text(hint, 190, 285, color=(255, 255, 255))
            self.text("Muenzen sammeln, auf Gegner springen, Flagge erreichen", 160, 330, color=(255, 255, 255))
        pygame.display.flip()

    def run(self):
        while True:
            dt = min(self.clock.tick(60) / 1000, 1 / 30)
            jump = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_r:
                        self.level = self.score = 0
                        self.load_level()
                    elif event.key == pygame.K_p and self.state in ("play", "pause"):
                        self.state = "pause" if self.state == "play" else "play"
                    elif event.key == pygame.K_RETURN:
                        if self.state == "title":
                            self.state = "play"
                        elif self.state == "clear":
                            self.level += 1
                            self.load_level()
                        elif self.state in ("over", "win"):
                            self.level = self.score = 0
                            self.load_level()
                    jump |= event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP)
            keys = pygame.key.get_pressed()
            move = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
            self.update(dt, move, jump, keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP],
                        keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            self.draw()


def smoke_test(game):
    game.state = "play"
    for _ in range(60):
        game.update(1 / 60)
    assert game.grounded and game.player.bottom == 460, "Ground collision failed"
    game.state = "pause"
    before = game.player.copy()
    game.update(1 / 60, move=1)
    assert game.player == before, "Pause failed"
    game.state = "play"
    start_y = game.player.y
    game.update(1 / 60, jump=True, held=True)
    assert game.player.y < start_y and game.vy < 0, "Jump failed"
    game.spawn()
    game.coins = [game.player.copy()]
    game.update(1 / 60)
    assert not game.coins and game.score == 10, "Coin collection failed"
    game.y = 700
    game.update(1 / 60)
    assert game.lives == 2 and game.player.x == 60, "Respawn failed"
    game.x = 1680
    game.update(1 / 60)
    assert game.checkpoint == 1640, "Checkpoint failed"
    game.invincible = 0
    game.enemies[0]["x"] = 480.0
    game.x, game.y = 480, 417
    game.player.topleft = (480, 417)
    game.vy = 0
    game.update(1 / 60)
    assert game.lives == 1, "Enemy damage failed"
    game.invincible = 0
    game.enemies[0]["x"] = 480.0
    game.x, game.y = 480, 381
    game.player.topleft = (480, 381)
    game.vy = 600
    count = len(game.enemies)
    game.update(1 / 60, held=True)
    assert len(game.enemies) == count - 1 and game.vy < 0, "Enemy stomp failed"
    game.x = 3450
    game.update(1 / 60)
    assert game.state == "clear", "Level completion failed"
    game.level = 2
    game.load_level()
    game.x = 3450
    game.update(1 / 60)
    assert game.state == "win", "Victory failed"
    for state in ("title", "play", "pause", "over", "clear", "win"):
        game.state = state
        game.draw()
    print("PASS: ground collision, pause, jump, coins, respawn, checkpoint, enemy damage, enemy stomp, level completion, victory, rendering")


if __name__ == "__main__":
    game = Game()
    try:
        if "--smoke-test" in sys.argv:
            smoke_test(game)
        else:
            game.run()
    finally:
        pygame.quit()
