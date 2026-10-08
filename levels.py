"""Ten deterministic courses; each has its own palette and terrain rhythm."""
import random
import pygame

NAMES = ['Sonnenwiese', 'Pilzpfad', 'Bernsteinküste', 'Windige Höhen',
         'Dämmerwald', 'Kristalltal', 'Frostpass', 'Sternenschlucht',
         'Glutberge', 'Himmelsfestung']
PALETTES = [
    ((94,179,223),(222,247,226),(75,148,113),(63,186,105),(126,84,64)),
    ((109,170,203),(239,224,206),(87,120,131),(142,179,83),(112,79,78)),
    ((247,173,118),(255,233,169),(167,130,126),(234,182,96),(141,96,75)),
    ((126,182,226),(236,249,252),(116,151,188),(115,201,171),(100,105,132)),
    ((79,92,153),(215,172,204),(70,91,122),(113,172,133),(96,69,100)),
    ((81,141,182),(192,237,239),(84,125,159),(116,218,213),(78,88,132)),
    ((135,174,211),(234,247,255),(111,142,174),(230,247,253),(123,155,178)),
    ((29,40,83),(108,93,149),(47,62,111),(133,133,208),(67,67,112)),
    ((104,61,101),(255,174,114),(124,73,94),(222,136,76),(100,66,77)),
    ((51,62,112),(190,148,202),(81,87,138),(196,177,240),(100,89,140)),
]


def make_level(index):
    rng = random.Random(701 + index)
    length = 4800 + index * 480
    ground = []
    x, previous_y = 0, 460
    while x < length:
        width = 700 if x == 0 else rng.randint(390 - index * 12, 600 - index * 14)
        y = 460 if x == 0 else max(405, min(480, previous_y + rng.choice([-25, 0, 25])))
        if x + width > length - 350:
            width = length - x
        ground.append(pygame.Rect(x, y, width, 540 - y))
        x += width + rng.randint(80 + index * 5, 110 + index * 6)
        previous_y = y
    checkpoints = [ground[len(ground)//3].x + 45, ground[2*len(ground)//3].x + 45]
    coins, enemies, spikes, bonus, moving, walls = [], [], [], [], [], []
    for i, p in enumerate(ground):
        if i and i < len(ground)-1:
            enemy_x = p.x + p.w * 0.65
            enemies.append({'rect': pygame.Rect(enemy_x, p.y-28, 32, 28),
                            'x': enemy_x, 'dir': -1, 'left': p.x+140,
                            'right': p.right-35, 'speed': 65 + index*9,
                            'hp': 2 if index >= 5 and i % 3 == 0 else 1,
                            'armored': index >= 5 and i % 3 == 0})
            if index >= 2 and i % 2 == 1:
                spikes.append(pygame.Rect(p.x + p.w//2 - 22, p.y-18, 44 + index*2, 18))
        # Elevated routes remain optional; all ground gaps have a direct sprint jump.
        if p.w > 330:
            b = pygame.Rect(p.x+130, p.y-95, 125 if index < 4 else 95, 20)
            bonus.append(b)
            if index >= 3 and i % 3 == 1:
                moving.append({'rect': pygame.Rect(p.x+260, p.y-175, 90, 18),
                               'base': p.x+260, 'phase': i, 'dx': 0})
            coins += [pygame.Rect(b.x+j, b.y-32, 16, 20) for j in range(15, b.w-10, 30)]
        if i < len(ground)-1:
            next_p = ground[i+1]
            gap_middle = (p.right + next_p.x)//2
            coins.append(pygame.Rect(gap_middle, min(p.y,next_p.y)-65,16,20))
        if i == 0 or (i % 3 == 0 and i < len(ground)-1):
            wall = pygame.Rect(p.x + (360 if i == 0 else 100), p.y-150, 40, 150)
            walls.append(wall)
            coins += [pygame.Rect(wall.x+12,wall.y-34,16,20)]
    return dict(length=length, ground=ground, bonus=bonus, moving=moving,
                coins=coins, enemies=enemies, spikes=spikes, checkpoints=checkpoints, walls=walls)
