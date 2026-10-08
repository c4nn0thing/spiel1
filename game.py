"""Wolkensprung: original, asset-free platform game for Windows and Linux."""
import math
import os
import sys
if '--smoke-test' in sys.argv or '--screenshot' in sys.argv:
    os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from levels import NAMES, PALETTES, make_level

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
        self.level = self.score = 0
        self.load_level()
        self.state = 'title'

    def load_level(self):
        data = make_level(self.level)
        for key,value in data.items():
            setattr(self,key,value)
        self.platforms = self.ground + self.bonus + [m['rect'] for m in self.moving]
        self.checkpoint = 60
        self.level_score = self.score
        self.lives = 4
        self.timer = self.invincible = self.camera = 0
        self.particles = []
        self.facing = 1
        self.walking = False
        self.standing = None
        self.state = 'play'
        self.spawn()
        self.background = self.make_background()

    def make_background(self):
        surface = pygame.Surface((WIDTH,HEIGHT))
        top,bottom,*_ = PALETTES[self.level]
        for y in range(HEIGHT):
            t=y/HEIGHT
            pygame.draw.line(surface,tuple(int(a+(b-a)*t) for a,b in zip(top,bottom)),(0,y),(WIDTH,y))
        return surface

    def spawn(self):
        p = next(p for p in self.ground if p.x <= self.checkpoint < p.right)
        self.player = pygame.Rect(self.checkpoint,p.y-42,28,42)
        self.x,self.y = map(float,self.player.topleft)
        self.vy = 0
        self.grounded = True
        self.coyote = self.jump_buffer = 0
        self.standing = p

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

    def update(self,dt,move=0,jump=False,held=False,sprint=False):
        if self.state!='play': return
        self.timer+=dt
        self.invincible=max(0,self.invincible-dt)
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
        if self.jump_buffer and self.coyote:
            self.vy=-590
            self.grounded=False
            self.standing=None
            self.coyote=self.jump_buffer=0
        if not held and self.vy < -240: self.vy=-240
        self.walking=bool(move)
        if move: self.facing=move
        self.x+=move*(340 if sprint else 235)*dt
        self.player.x=round(self.x)
        # Floating ledges are one-way, so jumps never snag on their undersides.
        for p in self.ground:
            if self.player.colliderect(p):
                if move>0: self.player.right=p.left
                elif move<0: self.player.left=p.right
                self.x=float(self.player.x)
        self.x=max(0,min(self.length-self.player.w,self.x))
        self.player.x=round(self.x)
        old_bottom=self.player.bottom
        self.vy=min(950,self.vy+1550*dt)
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
        self.screen.blit((font or self.font).render(message,True,color),(x,y))

    def draw_background(self):
        self.screen.blit(self.background,(0,0))
        ridge=PALETTES[self.level][2]
        if self.level>=7:
            for i in range(55):
                x=(i*173-int(self.camera*.08))%WIDTH
                y=35+(i*47)%220
                pygame.draw.circle(self.screen,(243,222,244),(x,y),1 if i%3 else 2)
        else:
            pygame.draw.circle(self.screen,(255,235,171),(785-int(self.camera*.03),92),38)
        for layer in (0,1):
            factor=.13+layer*.14
            for i in range(-1,7):
                x=i*270-int(self.camera*factor)%270
                color=tuple(max(0,c-layer*17) for c in ridge)
                pygame.draw.polygon(self.screen,color,[(x-90,HEIGHT),(x+125,210+layer*95+(i%3)*22),(x+370,HEIGHT)])
        if self.level<7:
            for i in range(6):
                x=(i*251-int(self.camera*.19))%(WIDTH+220)-110
                y=66+(i%3)*37
                for dx,dy,r in [(0,9,19),(27,0,27),(56,9,20)]:
                    pygame.draw.circle(self.screen,(238,248,253),(x+dx,y+dy),r)

    def draw_player(self):
        r=self.player.move(-self.camera,0)
        sprite=pygame.Surface((52,58),pygame.SRCALPHA)
        bob=round(math.sin(self.timer*17)*2) if self.walking and self.grounded else 0
        step=round(math.sin(self.timer*17)*4) if self.walking and self.grounded else (2 if not self.grounded else 0)
        pygame.draw.ellipse(sprite,(18,31,61,75),(8,49,36,7))
        # Scarf, boots, tunic, gloves, face, hair and aviator goggles.
        pygame.draw.polygon(sprite,(255,148,70),[(12,24),(1,19+bob),(3,29+bob),(15,29)])
        for x,dy in [(15,step),(29,-step)]:
            pygame.draw.rect(sprite,(36,39,69),(x,40+dy,11,9),border_radius=3)
            pygame.draw.rect(sprite,(224,176,114),(x-1,46+dy,13,5),border_radius=2)
        pygame.draw.rect(sprite,(36,73,119),(13,26+bob,26,19),border_radius=6)
        pygame.draw.rect(sprite,(57,167,178),(15,25+bob,22,16),border_radius=5)
        pygame.draw.rect(sprite,(255,193,121),(9,31+bob,7,9),border_radius=3)
        pygame.draw.rect(sprite,(255,193,121),(36,30+bob,7,9),border_radius=3)
        pygame.draw.rect(sprite,(255,194,139),(15,10+bob,23,20),border_radius=7)
        pygame.draw.rect(sprite,(77,49,63),(14,7+bob,25,10),border_radius=5)
        pygame.draw.rect(sprite,(239,119,63),(12,3+bob,29,10),border_radius=5)
        pygame.draw.rect(sprite,(255,181,85),(17,3+bob,17,3),border_radius=2)
        pygame.draw.rect(sprite,(39,51,74),(21,12+bob,19,8),border_radius=3)
        pygame.draw.rect(sprite,(159,229,234),(24,13+bob,6,5),border_radius=2)
        pygame.draw.rect(sprite,(159,229,234),(33,13+bob,5,5),border_radius=2)
        pygame.draw.rect(sprite,(210,123,100),(31,24+bob,5,2))
        pygame.draw.rect(sprite,(255,150,69),(14,27+bob,24,4),border_radius=2)
        if self.facing<0: sprite=pygame.transform.flip(sprite,True,False)
        self.screen.blit(sprite,(r.x-12,r.y-9))

    def draw(self):
        self.draw_background()
        _,_,_,grass,earth=PALETTES[self.level]
        for p in self.platforms:
            r=p.move(-self.camera,0)
            if r.right<0 or r.left>WIDTH: continue
            floating=p not in self.ground
            pygame.draw.rect(self.screen,(32,38,63),r.inflate(4,4),border_radius=5)
            pygame.draw.rect(self.screen,earth,r,border_radius=4)
            pygame.draw.rect(self.screen,grass,(r.x,r.y,r.w,9),border_radius=4)
            pygame.draw.line(self.screen,tuple(min(255,c+35) for c in grass),(r.x+3,r.y+2),(r.right-3,r.y+2),2)
            for x in range(max(r.x, -30),min(r.right,WIDTH)+1,26):
                pygame.draw.line(self.screen,tuple(max(0,c-15) for c in earth),(x,r.y+19),(x+10,r.y+19),2)
                if not floating:
                    pygame.draw.line(self.screen,tuple(max(0,c-20) for c in earth),(x+8,r.y+38),(x+18,r.y+38),2)
            if p in self.ground:
                for offset in range(45,p.w-20,110):
                    x=r.x+offset
                    pygame.draw.line(self.screen,grass,(x,p.y),(x+2,p.y-12),2)
                    pygame.draw.circle(self.screen,(255,202,146),(x+2,p.y-13),3)
        for s in self.spikes:
            x=s.x-self.camera
            for offset in range(0,s.w,16):
                pygame.draw.polygon(self.screen,(53,58,83),[(x+offset,s.bottom),(x+offset+8,s.top-3),(x+offset+16,s.bottom)])
                pygame.draw.polygon(self.screen,(228,229,243),[(x+offset+3,s.bottom-2),(x+offset+8,s.top),(x+offset+11,s.bottom-2)])
        for m in self.moving:
            r=m['rect'].move(-self.camera,0)
            pygame.draw.circle(self.screen,(158,230,239),r.center,5)
        for c in self.coins:
            r=c.move(-self.camera,round(math.sin(self.timer*4+c.x)*3))
            pygame.draw.ellipse(self.screen,(164,108,34),r.inflate(3,3))
            pygame.draw.ellipse(self.screen,(255,207,68),r)
            pygame.draw.ellipse(self.screen,(255,241,165),r.inflate(-7,-5),2)
        for e in self.enemies:
            r=e['rect'].move(-self.camera,0)
            pygame.draw.ellipse(self.screen,(39,35,67),(r.x-3,r.bottom-4,38,8))
            pygame.draw.rect(self.screen,(115,66,144),r,border_radius=10)
            pygame.draw.rect(self.screen,(185,115,205),(r.x+3,r.y+2,26,9),border_radius=5)
            for dx in (8,23):
                pygame.draw.circle(self.screen,(255,242,229),(r.x+dx,r.y+13),5)
                pygame.draw.circle(self.screen,(39,34,66),(r.x+dx+e['dir'],r.y+14),2)
            if e['armored']:
                for dx in (0,11,22):
                    pygame.draw.polygon(self.screen,(229,223,237),[(r.x+dx,r.y+4),(r.x+dx+5,r.y-9),(r.x+dx+10,r.y+4)])
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
        panel=pygame.Surface((WIDTH,65),pygame.SRCALPHA); panel.fill((20,29,54,215)); self.screen.blit(panel,(0,0))
        self.text(f'{self.level+1:02d} / 10  {NAMES[self.level]}',20,13)
        self.text(f'Punkte {self.score:05d}',WIDTH-175,14)
        for i in range(4):
            color=(249,115,113) if i<self.lives else (77,82,109)
            x=430+i*24
            pygame.draw.circle(self.screen,color,(x,22),6); pygame.draw.circle(self.screen,color,(x+8,22),6)
            pygame.draw.polygon(self.screen,color,[(x-6,24),(x+14,24),(x+4,36)])
        pygame.draw.rect(self.screen,(69,81,112),(20,46,WIDTH-40,4),border_radius=2)
        pygame.draw.rect(self.screen,(112,230,197),(20,46,max(1,int((WIDTH-40)*self.player.x/self.length)),4),border_radius=2)
        self.text('A/D  Laufen    SPACE  Springen    SHIFT  Sprint    P  Pause',20,HEIGHT-23,self.small)
        if self.state!='play':
            shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); shade.fill((14,20,43,205)); self.screen.blit(shade,(0,0))
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
            if self.state=='title': self.text('Ab Welt 6: Gegner mit Stacheln immer überspringen!',230,385,self.small)
        pygame.display.flip()

    def run(self):
        while True:
            dt=min(self.clock.tick(60)/1000,1/30)
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
                jump |= event.key in (pygame.K_SPACE,pygame.K_w,pygame.K_UP)
            k=pygame.key.get_pressed()
            self.update(dt,int(k[pygame.K_d] or k[pygame.K_RIGHT])-int(k[pygame.K_a] or k[pygame.K_LEFT]),jump,k[pygame.K_SPACE] or k[pygame.K_w] or k[pygame.K_UP],k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT])
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
