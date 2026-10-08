"""Wolkensprung: original, asset-free platform game for Windows and Linux."""
import math
import os
import sys
if '--smoke-test' in sys.argv or '--screenshot' in sys.argv:
    os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from levels import NAMES, PALETTES, make_level
import graphics

ITEMS = ("Hausschuh", "Konservendose", "Gehstock")

WIDTH, HEIGHT = 960, 540

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Wolkensprung • Zehn Welten')
        self.font = pygame.font.Font(None, 27)
        self.small = pygame.font.Font(None, 21)
        self.big = pygame.font.Font(None, 64)
        self.clock = pygame.time.Clock()
        self.player_frames = {(f, d, air): graphics.pensioner(f,d,air)
                              for f in range(8) for d in (-1,1) for air in (False,True)}
        self.enemy_sprites = {(a,d): graphics.enemy(a,d) for a in (False,True) for d in (-1,1)}
        self.item_sprites = [graphics.item(i) for i in range(3)]
        self.coin_sprite = graphics.coin()
        self.text_cache = {}
        self.panel = pygame.Surface((WIDTH,65),pygame.SRCALPHA).convert_alpha()
        self.panel.fill((20,29,54,215))
        self.shade = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA).convert_alpha()
        self.shade.fill((14,20,43,205))
        self.level = self.score = 0
        self.load_level()
        self.state = 'title'

    def load_level(self):
        data = make_level(self.level)
        for key,value in data.items():
            setattr(self,key,value)
        self.solids = self.ground + self.walls
        self.platforms = self.solids + self.bonus + [m['rect'] for m in self.moving]
        self.checkpoint = 60
        self.level_score = self.score
        self.lives = 4
        self.timer = self.invincible = self.camera = 0
        self.particles = []
        self.projectiles = []
        self.weapon = 0
        self.shoot_cooldown = 0
        self.facing = 1
        self.walking = False
        self.standing = None
        self.state = 'play'
        self.spawn()
        self.background = self.make_background().convert()
        self.backdrop_layers=graphics.backdrop_layers(self.level,PALETTES[self.level][2])
        grass,earth=PALETTES[self.level][3:]
        self.terrain_sprites = {id(p): graphics.terrain(p,grass,earth,
                               ground=any(p is g for g in self.ground),
                               wall=any(p is w for w in self.walls)) for p in self.platforms}
        self.text_cache.clear()

    def make_background(self):
        surface = pygame.Surface((WIDTH,HEIGHT))
        top,bottom,*_ = PALETTES[self.level]
        for y in range(HEIGHT):
            t=y/HEIGHT
            pygame.draw.line(surface,tuple(int(a+(b-a)*t) for a,b in zip(top,bottom)),(0,y),(WIDTH,y))
        return surface

    def spawn(self):
        p = next(p for p in self.ground if p.x <= self.checkpoint < p.right)
        self.player = pygame.Rect(self.checkpoint,p.y-48,38,48)
        self.x,self.y = map(float,self.player.topleft)
        self.vy = 0
        self.grounded = True
        self.coyote = self.jump_buffer = 0
        self.standing = p
        self.wall_side = 0
        self.wall_grace = 0
        self.wall_kick = 0
        self.kick_time = 0

    def burst(self,x,y,color):
        for i in range(9):
            angle=i*math.tau/9
            self.particles.append([x,y,math.cos(angle)*90,-60+math.sin(angle)*90,0.45,color])

    def hurt(self):
        self.lives-=1
        self.burst(self.player.centerx,self.player.centery,(255,130,90))
        if self.lives<=0:
            self.state='over'
        else:
            self.spawn()
            self.invincible=1.5

    def wall_contact(self):
        for wall in self.solids:
            if self.player.bottom<=wall.top+2 or self.player.top>=wall.bottom:
                continue
            if abs(self.player.right-wall.left)<=3:
                return 1
            if abs(self.player.left-wall.right)<=3:
                return -1
        return 0

    def fire(self):
        if self.state!='play' or self.shoot_cooldown or len(self.projectiles)>=24:
            return
        kind=self.weapon
        self.shoot_cooldown=(0.22,0.6,0.7)[kind]
        self.projectiles.append(dict(kind=kind,x=float(self.player.centerx),
            y=float(self.player.centery+3),vx=self.facing*(650,420,510)[kind],
            vy=-210 if kind==1 else 0,age=0,hits=set()))

    def hit_enemy(self,enemy,damage):
        enemy['hp']-=damage
        self.burst(*enemy['rect'].center,(255,208,119))
        if enemy['hp']<=0 and enemy in self.enemies:
            self.enemies.remove(enemy)
            self.score+=75 if enemy['armored'] else 50

    def explode(self,shot):
        self.burst(shot['x'],shot['y'],(244,179,76))
        for enemy in self.enemies[:]:
            if pygame.Vector2(enemy['rect'].center).distance_to((shot['x'],shot['y']))<70:
                self.hit_enemy(enemy,2)

    def update_projectiles(self,dt):
        # Small collision steps prevent fast slippers passing through thin enemies.
        steps=max(1,math.ceil(dt*120))
        step=dt/steps
        for shot in self.projectiles[:]:
            removed=False
            for _ in range(steps):
                shot['age']+=step
                kind=shot['kind']
                if kind==1: shot['vy']+=680*step
                elif kind==2 and shot['age']>=0.5:
                    delta=pygame.Vector2(self.player.center)-pygame.Vector2(shot['x'],shot['y'])
                    if delta.length()<22:
                        removed=True; break
                    delta.scale_to_length(560)
                    shot['vx'],shot['vy']=delta
                shot['x']+=shot['vx']*step
                shot['y']+=shot['vy']*step
                r=pygame.Rect(round(shot['x'])-9,round(shot['y'])-9,18,18)
                if shot['age']>2 or shot['y']>HEIGHT+100 or not -50<shot['x']<self.length+50:
                    removed=True; break
                if kind!=2 and any(r.colliderect(p) for p in self.solids):
                    if kind==1: self.explode(shot)
                    removed=True; break
                for enemy in self.enemies[:]:
                    if id(enemy) in shot['hits'] or not r.colliderect(enemy['rect']):
                        continue
                    shot['hits'].add(id(enemy))
                    if kind==1: self.explode(shot)
                    else: self.hit_enemy(enemy,1)
                    if kind!=2: removed=True
                    break
                if removed: break
            if removed: self.projectiles.remove(shot)

    def update(self,dt,move=0,jump=False,held=False,sprint=False,shoot=False):
        if self.state!='play': return
        self.timer+=dt
        self.invincible=max(0,self.invincible-dt)
        self.shoot_cooldown=max(0,self.shoot_cooldown-dt)
        if shoot: self.fire()
        for particle in self.particles[:]:
            particle[0]+=particle[2]*dt; particle[1]+=particle[3]*dt
            particle[3]+=250*dt; particle[4]-=dt
            if particle[4]<=0: self.particles.remove(particle)
        for m in self.moving:
            previous=m['rect'].x
            m['rect'].x=round(m['base']+math.sin(self.timer*1.5+m['phase'])*48)
            m['dx']=m['rect'].x-previous
            if self.standing is m['rect']:
                self.x+=m['dx']
        self.coyote=0.1 if self.grounded else max(0,self.coyote-dt)
        self.jump_buffer=0.12 if jump else max(0,self.jump_buffer-dt)
        contact=self.wall_contact()
        if contact:
            self.wall_side=contact
            self.wall_grace=0.12
        else:
            self.wall_grace=max(0,self.wall_grace-dt)
        if self.jump_buffer and not self.grounded and self.wall_grace:
            self.vy=-590
            self.wall_kick=-self.wall_side*340
            self.facing=-self.wall_side
            self.kick_time=0.18
            self.wall_grace=self.coyote=self.jump_buffer=0
            self.standing=None
            self.burst(self.player.centerx,self.player.centery,(183,223,228))
        elif self.jump_buffer and self.coyote:
            self.vy=-590
            self.grounded=False
            self.standing=None
            self.coyote=self.jump_buffer=0
        if not held and self.vy < -240: self.vy=-240
        self.walking=bool(move)
        if move: self.facing=move
        # A brief outward kick makes wall jumps usable even while holding into the wall.
        vx=self.wall_kick if self.kick_time>0 else move*(340 if sprint else 235)
        if self.kick_time>0: self.facing=1 if vx>0 else -1
        self.kick_time=max(0,self.kick_time-dt)
        self.x+=vx*dt
        self.player.x=round(self.x)
        # Floating ledges are one-way, so jumps never snag on their undersides.
        for p in self.solids:
            if self.player.colliderect(p):
                if vx>0: self.player.right=p.left
                elif vx<0: self.player.left=p.right
                self.x=float(self.player.x)
        self.x=max(0,min(self.length-self.player.w,self.x))
        self.player.x=round(self.x)
        old_bottom=self.player.bottom
        self.vy=min(950,self.vy+1550*dt)
        if contact and move==contact and self.vy>160 and not self.kick_time:
            self.vy=160
        self.y+=self.vy*dt
        self.player.y=round(self.y)
        self.grounded=False
        self.standing=None
        for p in self.platforms:
            if (self.vy>=0 and old_bottom<=p.top+2 and self.player.bottom>=p.top
                    and self.player.right>p.left and self.player.left<p.right):
                self.player.bottom=p.top
                self.y=float(self.player.y)
                self.vy=0
                self.grounded=True
                self.standing=p
        for p in self.solids:
            if self.vy<0 and self.player.colliderect(p):
                self.player.top=p.bottom
                self.y=float(self.player.y)
                self.vy=0
        for coin in self.coins[:]:
            if self.player.colliderect(coin):
                self.coins.remove(coin); self.score+=10
                self.burst(*coin.center,(255,221,100))
        for e in self.enemies[:]:
            e['x']+=e['dir']*e['speed']*dt
            if e['x']>e['right'] or e['x']<e['left']:
                e['x']=max(e['left'],min(e['right'],e['x']))
                e['dir']*=-1
            e['rect'].x=round(e['x'])
            if self.player.colliderect(e['rect']):
                if self.vy>0 and old_bottom<=e['rect'].top+12 and not e['armored']:
                    self.enemies.remove(e); self.vy=-400; self.score+=50
                    self.burst(*e['rect'].center,(199,137,235))
                elif not self.invincible:
                    self.hurt(); break
        self.update_projectiles(dt)
        if not self.invincible and any(self.player.colliderect(s) for s in self.spikes):
            self.hurt()
        if self.player.top>HEIGHT+100: self.hurt()
        for cp in self.checkpoints:
            if self.player.x>=cp and cp>self.checkpoint:
                self.checkpoint=cp
                self.burst(cp,self.player.y,(113,245,201))
        if self.player.x>=self.length-140 and self.state=='play':
            self.score+=100+self.level*25
            self.state='win' if self.level==9 else 'clear'
        self.camera=max(0,min(self.length-WIDTH,self.player.centerx-WIDTH//3))

    def text(self,message,x,y,font=None,color=(240,246,255)):
        key=(message,font or self.font,color)
        if key not in self.text_cache:
            if len(self.text_cache)>128: self.text_cache.clear()
            self.text_cache[key]=(font or self.font).render(message,True,color)
        self.screen.blit(self.text_cache[key],(x,y))

    def draw_background(self):
        self.screen.blit(self.background,(0,0))
        if self.level<7:
            pygame.draw.circle(self.screen,(255,235,171),(785-int(self.camera*.03),92),38)
        for image,factor,y in self.backdrop_layers:
            x=-int(self.camera*factor)%image.get_width()-image.get_width()
            while x<WIDTH:
                self.screen.blit(image,(x,y))
                x+=image.get_width()

    def draw_player(self):
        frame=int(self.timer*12)%8 if self.walking and self.grounded else 0
        sprite=self.player_frames[frame,self.facing,not self.grounded]
        self.screen.blit(sprite,(self.player.x-self.camera-17,self.player.y-19))

    def draw(self):
        self.draw_background()
        for p in self.platforms:
            if p.right<self.camera-8 or p.left>self.camera+WIDTH+8: continue
            self.screen.blit(self.terrain_sprites[id(p)],(p.x-self.camera-4,p.y-18))
        for s in self.spikes:
            x=s.x-self.camera
            for offset in range(0,s.w,16):
                pygame.draw.polygon(self.screen,(53,58,83),[(x+offset,s.bottom),(x+offset+8,s.top-3),(x+offset+16,s.bottom)])
                pygame.draw.polygon(self.screen,(228,229,243),[(x+offset+3,s.bottom-2),(x+offset+8,s.top),(x+offset+11,s.bottom-2)])
        for m in self.moving:
            r=m['rect'].move(-self.camera,0)
            pygame.draw.circle(self.screen,(158,230,239),r.center,5)
        for c in self.coins:
            if c.right<self.camera-4 or c.left>self.camera+WIDTH: continue
            self.screen.blit(self.coin_sprite,(c.x-self.camera-2,c.y-2+round(math.sin(self.timer*4+c.x)*3)))
        for e in self.enemies:
            r=e['rect']
            if r.right<self.camera-8 or r.left>self.camera+WIDTH: continue
            self.screen.blit(self.enemy_sprites[e['armored'],e['dir']],(r.x-self.camera-5,r.y-9))
        for shot in self.projectiles:
            self.screen.blit(self.item_sprites[shot['kind']],(shot['x']-self.camera-14,shot['y']-14))
        for cp in self.checkpoints+[self.length-110]:
            p=next(p for p in self.ground if p.x<=cp<p.right)
            x=cp-self.camera
            pygame.draw.rect(self.screen,(240,232,216),(x,p.y-138,5,138),border_radius=2)
            color=(105,230,170) if cp<=self.checkpoint or cp==self.length-110 else (245,163,86)
            wave=math.sin(self.timer*4)*5
            pygame.draw.polygon(self.screen,color,[(x+5,p.y-135),(x+61,p.y-118+wave),(x+5,p.y-97)])
            pygame.draw.circle(self.screen,(255,231,151),(int(x+2),p.y-141),5)
        if not self.invincible or int(self.timer*12)%2==0: self.draw_player()
        for x,y,_,_,life,color in self.particles:
            pygame.draw.circle(self.screen,color,(round(x-self.camera),round(y)),max(1,round(life*8)))
        self.screen.blit(self.panel,(0,0))
        self.text(f'{self.level+1:02d} / 10  {NAMES[self.level]}',20,13)
        self.text(f'Punkte {self.score:05d}',WIDTH-175,14)
        for i in range(4):
            color=(249,115,113) if i<self.lives else (77,82,109)
            x=430+i*24
            pygame.draw.circle(self.screen,color,(x,22),6); pygame.draw.circle(self.screen,color,(x+8,22),6)
            pygame.draw.polygon(self.screen,color,[(x-6,24),(x+14,24),(x+4,36)])
        pygame.draw.rect(self.screen,(69,81,112),(20,46,WIDTH-40,4),border_radius=2)
        pygame.draw.rect(self.screen,(112,230,197),(20,46,max(1,int((WIDTH-40)*self.player.x/self.length)),4),border_radius=2)
        self.text(f'A/D: Laufen  SPACE: (Wand-)Sprung  SHIFT: Sprint  J: Schuss  1/2/3 oder Q: {ITEMS[self.weapon]}',20,HEIGHT-23,self.small)
        if self.state!='play':
            self.screen.blit(self.shade,(0,0))
            pygame.draw.rect(self.screen,(36,45,75),(155,143,650,262),border_radius=22)
            pygame.draw.rect(self.screen,(98,148,172),(155,143,650,262),2,border_radius=22)
            titles={'title':'WOLKENSPRUNG','pause':'Pause','over':'Versuch es noch einmal!','clear':'Etappe geschafft!','win':'Alle zehn Welten geschafft!'}
            rendered=self.big.render(titles[self.state],True,(255,224,144))
            if rendered.get_width()>610: rendered=pygame.transform.smoothscale(rendered,(600,45))
            self.screen.blit(rendered,rendered.get_rect(center=(480,210)))
            self.text(f'{self.level+1:02d}  {NAMES[self.level]}  •  {self.length//100} Abschnitte',245,260)
            hints={'pause':'P: Weiterspielen','over':'Enter: Level erneut versuchen', 'clear':'Enter: Nächstes Level','win':'Enter: Neue Reise','title':'Enter: Reise starten'}
            self.text(hints[self.state],280,307)
            self.text('R: Neue Reise    Esc: Beenden',320,349,self.small)
            if self.state=='title': self.text('An Wänden SPACE erneut drücken. Mit J Gegenstände werfen!',200,385,self.small)
        pygame.display.flip()

    def run(self):
        accumulator=0
        pending_jump=False
        while True:
            accumulator+=min(self.clock.tick(60)/1000,0.25)
            jump=False
            for event in pygame.event.get():
                if event.type==pygame.QUIT: return
                if event.type!=pygame.KEYDOWN: continue
                if event.key==pygame.K_ESCAPE: return
                if event.key==pygame.K_r:
                    self.level=self.score=0; self.load_level()
                elif event.key==pygame.K_p and self.state in ('play','pause'):
                    self.state='pause' if self.state=='play' else 'play'
                elif event.key==pygame.K_RETURN:
                    if self.state=='title': self.state='play'
                    elif self.state=='clear': self.level+=1; self.load_level()
                    elif self.state=='over': self.score=self.level_score; self.load_level()
                    elif self.state=='win': self.level=self.score=0; self.load_level()
                if event.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                    self.weapon=event.key-pygame.K_1
                elif event.key==pygame.K_q: self.weapon=(self.weapon+1)%3
                jump |= event.key in (pygame.K_SPACE,pygame.K_w,pygame.K_UP)
            k=pygame.key.get_pressed()
            pending_jump |= jump
            while accumulator>=1/60:
                self.update(1/60,int(k[pygame.K_d] or k[pygame.K_RIGHT])-int(k[pygame.K_a] or k[pygame.K_LEFT]),pending_jump,k[pygame.K_SPACE] or k[pygame.K_w] or k[pygame.K_UP],k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT],k[pygame.K_j] or k[pygame.K_x])
                pending_jump=False
                accumulator-=1/60
            self.draw()

if __name__=='__main__':
    game=Game()
    try:
        if '--smoke-test' in sys.argv:
            from test_game import run_tests
            run_tests()
        elif '--screenshot' in sys.argv:
            game.state='play'
            game.draw()
            pygame.image.save(game.screen,sys.argv[sys.argv.index('--screenshot')+1])
        else: game.run()
    finally: pygame.quit()
