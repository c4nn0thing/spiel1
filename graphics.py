"""Pre-rendered original cartoon sprites. No image files or per-frame allocations."""
import math
import pygame


def pensioner(frame=0, facing=1, airborne=False):
    s=pygame.Surface((72,76),pygame.SRCALPHA)
    step=round(math.sin(frame*math.tau/8)*4) if not airborne else 3
    bob=round(math.sin(frame*math.tau/8)*1) if not airborne else 0
    pygame.draw.ellipse(s,(18,31,61,65),(10,66,52,8))
    for x,dy in ((23,step),(43,-step)):
        pygame.draw.rect(s,(68,58,73),(x,55+dy,11,10),border_radius=3)
        pygame.draw.rect(s,(115,77,52),(x-4,63+dy,17,6),border_radius=3)
        pygame.draw.line(s,(208,167,117),(x-2,65+dy),(x+10,65+dy),2)
    # Round cardigan, visible belly, shirt and suspenders.
    pygame.draw.ellipse(s,(48,70,76),(9,26+bob,54,36))
    pygame.draw.ellipse(s,(116,153,133),(11,25+bob,50,34))
    pygame.draw.ellipse(s,(231,217,174),(23,28+bob,31,30))
    pygame.draw.line(s,(90,69,52),(25,31+bob),(26,55+bob),3)
    pygame.draw.line(s,(90,69,52),(47,31+bob),(45,55+bob),3)
    pygame.draw.rect(s,(100,72,57),(19,54+bob,35,5),border_radius=2)
    pygame.draw.rect(s,(228,187,78),(34,54+bob,7,6),1,border_radius=1)
    for y in (37,45): pygame.draw.circle(s,(115,98,82),(36,y+bob),1)
    pygame.draw.ellipse(s,(247,196,154),(6,39+bob,12,15))
    pygame.draw.ellipse(s,(247,196,154),(54,37+bob,12,15))
    pygame.draw.rect(s,(120,156,137),(9,37+bob,8,6),border_radius=2)
    pygame.draw.rect(s,(120,156,137),(54,35+bob,8,6),border_radius=2)
    pygame.draw.ellipse(s,(247,200,162),(23,7+bob,31,29))
    # Bald crown, white side hair, eyebrows, round glasses, moustache.
    pygame.draw.ellipse(s,(225,222,216),(19,13+bob,9,16))
    pygame.draw.ellipse(s,(255,216,180),(28,7+bob,21,8))
    pygame.draw.arc(s,(202,171,146),(29,9+bob,18,10),0.2,2.7,1)
    pygame.draw.line(s,(246,244,232),(32,16+bob),(39,16+bob),2)
    pygame.draw.line(s,(246,244,232),(44,16+bob),(51,16+bob),2)
    for x in (35,47):
        pygame.draw.circle(s,(188,225,228),(x,21+bob),5)
        pygame.draw.circle(s,(57,60,69),(x,21+bob),5,1)
        pygame.draw.circle(s,(40,44,52),(x+1,21+bob),1)
    pygame.draw.line(s,(57,60,69),(40,21+bob),(42,21+bob),1)
    pygame.draw.ellipse(s,(231,164,131),(48,22+bob,9,7))
    pygame.draw.ellipse(s,(245,240,225),(35,28+bob,18,5))
    pygame.draw.line(s,(137,96,87),(40,33+bob),(47,33+bob),1)
    return (s if facing==1 else pygame.transform.flip(s,True,False)).convert_alpha()


def terrain(rect,grass,earth,ground=False,wall=False):
    s=pygame.Surface((rect.w+8,rect.h+23),pygame.SRCALPHA)
    r=pygame.Rect(4,18,rect.w,rect.h)
    pygame.draw.rect(s,(32,38,63),r.inflate(4,4),border_radius=5)
    pygame.draw.rect(s,earth,r,border_radius=4)
    pygame.draw.rect(s,grass,(r.x,r.y,r.w,9),border_radius=4)
    pygame.draw.line(s,tuple(min(255,c+35) for c in grass),(r.x+3,r.y+2),(r.right-3,r.y+2),2)
    if wall:
        for y in range(35,r.bottom,20):
            pygame.draw.line(s,(67,65,83),(5,y),(r.right-1,y),2)
            pygame.draw.line(s,(67,65,83),(20 if y%40 else 30,y),(20 if y%40 else 30,y+18),2)
    else:
        for x in range(r.x,r.right,26):
            pygame.draw.line(s,tuple(max(0,c-15) for c in earth),(x,r.y+19),(x+10,r.y+19),2)
            if ground:
                pygame.draw.line(s,tuple(max(0,c-20) for c in earth),(x+8,r.y+38),(x+18,r.y+38),2)
        if ground:
            for x in range(49,r.right-20,110):
                pygame.draw.line(s,grass,(x,r.y),(x+2,r.y-12),2)
                pygame.draw.circle(s,(255,202,146),(x+2,r.y-13),3)
    return s.convert_alpha()


def enemy(armored,direction):
    s=pygame.Surface((42,43),pygame.SRCALPHA)
    pygame.draw.ellipse(s,(39,35,67),(2,33,38,8))
    pygame.draw.rect(s,(115,66,144),(5,9,32,28),border_radius=10)
    pygame.draw.rect(s,(185,115,205),(8,11,26,9),border_radius=5)
    for x in (13,28):
        pygame.draw.circle(s,(255,242,229),(x,22),5)
        pygame.draw.circle(s,(39,34,66),(x+direction,23),2)
    if armored:
        for x in (5,16,27):
            pygame.draw.polygon(s,(229,223,237),[(x,13),(x+5,0),(x+10,13)])
    return s.convert_alpha()


def item(kind):
    s=pygame.Surface((28,28),pygame.SRCALPHA)
    if kind==0:
        pygame.draw.ellipse(s,(74,44,34),(2,11,25,13))
        pygame.draw.ellipse(s,(181,105,75),(3,10,23,11))
        pygame.draw.ellipse(s,(237,193,145),(13,11,11,6))
        pygame.draw.line(s,(251,217,171),(4,20),(24,20),2)
    elif kind==1:
        pygame.draw.rect(s,(111,121,131),(6,5,17,20),border_radius=3)
        pygame.draw.rect(s,(220,227,215),(8,5,13,3),border_radius=1)
        pygame.draw.rect(s,(233,176,85),(6,12,17,7))
        pygame.draw.circle(s,(99,141,81),(14,15),3)
    else:
        pygame.draw.arc(s,(203,153,85),(4,2,17,15),0,math.pi,5)
        pygame.draw.line(s,(169,110,62),(6,9),(6,25),5)
        pygame.draw.line(s,(238,191,115),(5,10),(5,24),1)
    return s.convert_alpha()


def coin():
    s=pygame.Surface((20,24),pygame.SRCALPHA)
    pygame.draw.ellipse(s,(164,108,34),(0,0,20,24))
    pygame.draw.ellipse(s,(255,207,68),(2,2,16,20))
    pygame.draw.ellipse(s,(255,241,165),(5,5,10,14),2)
    return s.convert_alpha()


def backdrop_layers(level,ridge):
    layers=[]
    if level>=7:
        s=pygame.Surface((960,250)).convert(); s.fill((255,0,255))
        for i in range(55):
            pygame.draw.circle(s,(243,222,244),((i*173)%960,35+(i*47)%220),1 if i%3 else 2)
        s.set_colorkey((255,0,255),pygame.RLEACCEL)
        layers.append((s,.08,0))
    for layer in (0,1):
        # Three peak shapes repeat seamlessly; transparent sky uses RLE colorkey.
        s=pygame.Surface((810,330)).convert(); s.fill((255,0,255))
        color=tuple(max(0,c-layer*17) for c in ridge)
        for i in range(-2,5):
            x=i*270
            pygame.draw.polygon(s,color,[(x-90,330),(x+125,layer*95+(i%3)*22),(x+370,330)])
        s.set_colorkey((255,0,255),pygame.RLEACCEL)
        layers.append((s,.13+layer*.14,210))
    if level<7:
        s=pygame.Surface((1506,190)).convert(); s.fill((255,0,255))
        for i in range(6):
            x=i*251; y=66+(i%3)*37
            for dx,dy,r in ((0,9,19),(27,0,27),(56,9,20)):
                pygame.draw.circle(s,(238,248,253),(x+dx,y+dy),r)
        s.set_colorkey((255,0,255),pygame.RLEACCEL)
        layers.append((s,.19,0))
    return layers
