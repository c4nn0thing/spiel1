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
        self.place(e['rect'].x,e['rect'].top-51,600)
        count=len(g.enemies)
        g.update(1/60,held=True)
        self.assertEqual(len(g.enemies),count-1)
        self.assertLess(g.vy,0)
        g.level=6; g.load_level()
        e=next(e for e in g.enemies if e['armored']); e['speed']=0
        self.place(e['rect'].x,e['rect'].top-51,600)
        g.update(1/60,held=True)
        self.assertEqual(g.lives,3)
        self.assertIn(e,g.enemies)
        g.invincible=0
        s=g.spikes[0]
        self.place(s.x,s.bottom-42)
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
                self.place(cp+1,p.y-42)
                g.update(1/60)
                self.assertEqual(g.checkpoint,cp)
            p=g.ground[-1]
            self.place(g.length-139,p.y-42)
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
            for left,right in zip(ground,ground[1:]):
                g.state='play'
                self.place(left.right-50,left.top-42)
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
        self.place(m['rect'].x+20,m['rect'].top-42)
        g.grounded=True; g.standing=m['rect']
        old=g.player.x
        g.update(1/60)
        self.assertEqual(g.player.x,old+m['dx'])
        self.assertTrue(g.grounded)


def run_tests():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Mechanics))
    if not result.wasSuccessful(): raise SystemExit(1)

if __name__=='__main__': run_tests()
