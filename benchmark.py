"""Repeatable headless render benchmark; numbers are not Windows FPS guarantees."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import argparse
import json
import statistics
import time
import pygame
from game import Game


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--frames',type=int,default=600)
    args=parser.parse_args()
    if args.frames<100: parser.error('--frames must be at least 100')
    game=Game(); game.level=9; game.load_level(); game.state='play'
    samples=[]
    try:
        for frame in range(args.frames+60):
            game.camera=(frame*47)%(game.length-960)
            game.timer=frame/60
            start=time.perf_counter()
            game.draw()
            if frame>=60: samples.append((time.perf_counter()-start)*1000)
        print(json.dumps(dict(frames=len(samples),mean_ms=round(statistics.mean(samples),3),
                              median_ms=round(statistics.median(samples),3),
                              p95_ms=round(sorted(samples)[int(len(samples)*.95)],3))))
    finally:
        pygame.quit()

if __name__=='__main__': main()
