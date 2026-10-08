"""Headless gameplay regression tests; no Windows desktop required."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
import pygame
from game import Game

class Mechanics(unittest.TestCase):
    def setUp(self):
        self.g=Game()
        self.g.state='play'

    def place(self,x,y,vy=0):
        g=self.g
        g.x,g.y=float(x),float(y)
        g.player.topleft=(x,y)
        g.vy=vy
        g.grounded=False
        g.standing=None

    def test_jump_pause_coin_and_respawn(self):
        g=self.g
        g.update(1/60,jump=True,held=True)
        self.assertLess(g.vy,0)
        g.state='pause'; before=g.player.copy()
        g.update(1/60,move=1)
        self.assertEqual(g.player,before)
        g.state='play'; g.coins=[g.player.copy()]
        g.update(1/60,held=True)
        self.assertEqual(g.score,10)
        g.checkpoint=g.checkpoints[0]
        self.place(300,700)
        g.update(1/60)
        self.assertEqual(g.lives,3)
        self.assertEqual(g.player.x,g.checkpoint)
        self.assertTrue(g.grounded)

    def test_enemy_stomp_armor_and_spikes(self):
        g=self.g
        e=g.enemies[0]; e['speed']=0
        self.place(e['rect'].x,e['rect'].top-g.player.h-9,600)
        count=len(g.enemies)
        g.update(1/60,held=True)
        self.assertEqual(len(g.enemies),count-1)
        self.assertLess(g.vy,0)
        g.level=6; g.load_level()
        e=next(e for e in g.enemies if e['armored']); e['speed']=0
        self.place(e['rect'].x,e['rect'].top-g.player.h-9,600)
        g.update(1/60,held=True)
        self.assertEqual(g.lives,3)
        self.assertIn(e,g.enemies)
        g.invincible=0
        s=g.spikes[0]
        self.place(s.x,s.bottom-g.player.h)
        g.update(1/60)
        self.assertEqual(g.lives,2)

    def test_all_levels_render_checkpoint_and_finish(self):
        g=self.g
        layouts=set()
        previous=0
        for level in range(10):
            g.level=level; g.load_level()
            self.assertGreater(g.length,previous); previous=g.length
            self.assertEqual(g.ground[-1].right,g.length)
            layouts.add(tuple(tuple(p) for p in g.ground))
            g.enemies=[]; g.spikes=[]
            for cp in g.checkpoints:
                p=next(p for p in g.ground if p.x<=cp<p.right)
                self.place(cp+1,p.y-g.player.h)
                g.update(1/60)
                self.assertEqual(g.checkpoint,cp)
            p=g.ground[-1]
            self.place(g.length-139,p.y-g.player.h)
            g.update(1/60)
            self.assertEqual(g.state,'win' if level==9 else 'clear')
            for state in ('play','title','pause','over','clear','win'):
                g.state=state; g.draw()
        self.assertEqual(len(layouts),10)

    def test_every_ground_gap_is_physically_jumpable(self):
        g=self.g
        jumps=0
        for level in range(10):
            g.level=level; g.load_level()
            ground=list(g.ground)
            g.enemies=[]; g.spikes=[]; g.coins=[]; g.moving=[]
            # Validate the mandatory ground route, without optional ledges or hazards.
            g.platforms=ground
            g.solids=ground
            for left,right in zip(ground,ground[1:]):
                g.state='play'
                self.place(left.right-50,left.top-g.player.h)
                g.grounded=True
                g.standing=left
                landed=False
                for frame in range(90):
                    g.update(1/60,move=1,jump=frame==0,held=True,sprint=True)
                    if g.grounded and g.standing is right:
                        landed=True; break
                    if g.player.top>600: break
                self.assertTrue(landed,f'Level {level+1}, gap {left.right} -> {right.x}')
                jumps+=1
        print(f'Validated {jumps} mandatory sprint jumps across all 10 levels.')

    def test_moving_platform_carries_player(self):
        g=self.g; g.level=3; g.load_level()
        m=g.moving[0]
        self.place(m['rect'].x+20,m['rect'].top-g.player.h)
        g.grounded=True; g.standing=m['rect']
        old=g.player.x
        g.update(1/60)
        self.assertEqual(g.player.x,old+m['dx'])
        self.assertTrue(g.grounded)

    def test_walljump_both_sides_slide_and_no_air_jump(self):
        g=self.g
        wall=g.walls[0]
        g.enemies=[]; g.spikes=[]
        for side in (1,-1):
            x=wall.left-g.player.w if side==1 else wall.right
            self.place(x,wall.y+40,300)
            g.kick_time=g.wall_grace=0
            g.update(1/60,move=side,held=True)
            self.assertLessEqual(g.vy,160)
            before=g.player.x
            g.update(1/60,move=side,jump=True,held=True)
            self.assertLess(g.vy,0)
            self.assertLess((g.player.x-before)*side,0)
        self.place(40,150,100)
        g.wall_grace=g.coyote=g.kick_time=0
        g.update(1/60,jump=True,held=True)
        self.assertGreater(g.vy,0)

    def test_first_wall_can_be_climbed(self):
        g=self.g
        g.enemies=[]; g.spikes=[]
        wall=g.walls[0]
        self.place(wall.x-100,g.ground[0].y-g.player.h)
        g.grounded=True
        climbed=False
        for frame in range(180):
            g.update(1/60,move=1,jump=frame==0 or bool(g.wall_contact()),held=True,sprint=True)
            if g.player.left>=wall.right:
                climbed=True; break
        self.assertTrue(climbed,'First tower must be traversable with wall jumps')

    def test_all_weapons_damage_and_cane_returns(self):
        g=self.g
        g.enemies=[]
        for kind in range(3):
            g.projectiles=[]; g.shoot_cooldown=0; g.weapon=kind
            distance=240 if kind==1 else 85
            target=dict(rect=pygame.Rect(g.player.centerx+distance,g.player.y+10,38,38),
                        hp=2 if kind==1 else 1,armored=kind==1)
            g.enemies=[target]
            g.fire()
            self.assertEqual(len(g.projectiles),1)
            for _ in range(100): g.update_projectiles(1/120)
            self.assertNotIn(target,g.enemies,f'Weapon {kind} should hit the enemy')
            if kind==2:
                for _ in range(200): g.update_projectiles(1/120)
                self.assertFalse(g.projectiles,'Cane must return or expire')

    def test_shots_cooldown_pause_and_terrain_collision(self):
        g=self.g
        g.fire(); g.fire()
        self.assertEqual(len(g.projectiles),1)
        g.state='pause'; before=g.projectiles[0].copy()
        g.update(1/60,shoot=True)
        self.assertEqual(g.projectiles[0],before)
        g.state='play'; g.projectiles=[]; g.shoot_cooldown=0
        wall=g.walls[0]
        self.place(wall.left-g.player.w-30,wall.y+20)
        g.fire()
        for _ in range(40): g.update_projectiles(1/120)
        self.assertFalse(g.projectiles,'Slipper must stop at a wall')

    def test_armored_enemy_needs_two_slippers(self):
        g=self.g; g.weapon=0
        target=dict(rect=pygame.Rect(g.player.centerx+85,g.player.y+10,38,38),hp=2,armored=True)
        g.enemies=[target]
        for expected in (1,0):
            g.shoot_cooldown=0; g.fire()
            for _ in range(30): g.update_projectiles(1/120)
            self.assertEqual(target['hp'],expected)
        self.assertNotIn(target,g.enemies)

    def test_can_splash_and_projectile_limit(self):
        g=self.g
        g.enemies=[dict(rect=pygame.Rect(x,400,32,28),hp=2,armored=True)
                   for x in (150,190,350)]
        g.explode(dict(x=180,y=414))
        self.assertEqual(len(g.enemies),1)
        self.assertEqual(g.enemies[0]['rect'].x,350)
        g.enemies=[]
        for _ in range(40):
            g.shoot_cooldown=0; g.fire()
        self.assertEqual(len(g.projectiles),24)
        for _ in range(150): g.update_projectiles(1/60)
        self.assertFalse(g.projectiles)

    def test_keyboard_selects_weapons(self):
        g=self.g
        for key,expected in ((pygame.K_2,1),(pygame.K_3,2),(pygame.K_q,0)):
            pygame.event.clear()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=key))
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            g.run()
            self.assertEqual(g.weapon,expected)


def run_tests():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Mechanics))
    if not result.wasSuccessful(): raise SystemExit(1)

if __name__=='__main__': run_tests()
