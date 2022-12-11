import sys
from entity import *
from food import *
from environment import *
from datetime import datetime
import json
import pygame
from collections import Counter
import cv2
import os
import numpy as np

env = None
step = 0

entities = 20
neurons = 512
axons = 256
mutation_rate = 10
initial_food = 400
food_per_step = 50

pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode(
    [SCREEN_WIDTH, SCREEN_HEIGHT], pygame.DOUBLEBUF)

pygame.display.set_caption('evolution')

font = pygame.font.SysFont("Consolas", 12)

running = True

clock = pygame.time.Clock()


def load_save(save_path):
    global step, neurons, axons
    with open(f'{save_path}', 'r') as savefile:
        save = json.load(savefile)
        step = save['step']
        neurons = save['neurons']
        axons = save['axons']
        env = Environment(size=save['env']['size'], entities=[], food=[],
                          ray_stop=save['env']['ray_stop'], ray_steps=save['env']['ray_steps'], mutation_rate=save['env']['mutation_rate'], food_per_step=100)#save['env']['food_per_step'])
        env.entities = list(map(lambda x: Entity(
            x['dna'], env, x['position'], x['lifetime'], x['generation'], x['hunger']), save['env']['entities']))
        env.food = list(
            map(lambda x: Food(x['position'], x['radius']), save['env']['food']))
    return env


def dump_save(save_path):
    save = {
        'step': step,
        'neurons': neurons,
        'axons': axons,
        'env': {
            'size': env.size,
            'ray_stop': env.ray_stop,
            'ray_steps': env.ray_steps,
            'entities': list(map(lambda x: {'dna': x.dna, 'position': x.position, 'lifetime': x.lifetime, 'generation': x.generation, 'hunger': x.hunger}, env.entities)),
            'food': list(map(lambda x: {'position': x.position, 'radius': x.radius}, env.food)),
            'mutation_rate': env.mutation_rate,
            'food_per_step': env.food_per_step,
        }
    }
    with open(save_path, 'w') as savefile:
        json.dump(save, savefile)


def create_env():
    env = Environment(size=pygame.display.get_surface().get_size(), entities=[],
                      food=[], ray_stop=0.1, ray_steps=10, mutation_rate=mutation_rate, food_per_step=food_per_step)
    for _ in range(entities):
        dna = generate_dna(neurons, axons)
        env.entities.append(
            Entity(dna, env, (random.random()*env.size[0], random.random()*env.size[1])))
    for _ in range(initial_food):
        env.food.append(
            Food((random.random()*env.size[0], random.random()*env.size[1])))
    return env


def draw_food(screen):
    for food in env.food:
        pygame.draw.circle(screen, (0, 255, 0), food.position, food.radius)


def draw_entities(screen):
    for entity in env.entities:
        pygame.draw.circle(screen, (255, 255, 255),
                           entity.position, math.log2(entity.lifetime if entity.lifetime != 0 else 4)+3)
        pygame.draw.circle(screen, entity.color,
                           entity.position, math.log2(entity.lifetime if entity.lifetime != 0 else 4)+2)
        pygame.draw.circle(screen, (255, 0, 0),
                           entity.position, (entity.hunger/100)*(math.log2(entity.lifetime if entity.lifetime != 0 else 4)+2))


def draw_information(screen, text_array):
    for i, text in enumerate(text_array):
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (0, i*12))


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        save_path = sys.argv[1]
        video_path = f"videos/{os.path.basename(sys.argv[1]).split('.')[0]}.mp4"
        env = load_save(save_path)
        os.rename(video_path, f"{video_path}.bak")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videowriter = cv2.VideoWriter(video_path, fourcc, 60, env.size)
        old_video = cv2.VideoCapture(f"{video_path}.bak")
        while (old_video.isOpened()):
            ret, frame = old_video.read()
            if ret == True:
                videowriter.write(frame)
            else:
                break
        old_video.release()
        os.remove(f"{video_path}.bak")
    else:
        save_path = f"saves/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        video_path = f"videos/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.mp4"
        env = create_env()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videowriter = cv2.VideoWriter(video_path, fourcc, 60, env.size)
    neurons_count = sum(map(lambda x: len(x.neurons), env.entities))
    axons_count = sum(
        map(lambda x: sum(map(lambda y: len(y.axons), x.neurons)), env.entities))
    generations = list(f" Gen {generation}: {number}" for generation, number in Counter(
        [d.generation for d in env.entities]).items())
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        env.size = pygame.display.get_surface().get_size()
        env.step()
        step += 1
        screen.fill((22, 22, 22))
        draw_food(screen)
        draw_entities(screen)
        draw_information(screen, [
            f"Savepath: {save_path}",
            f"Step: {step}",
            f"Entities: {len(env.entities)}",
            f"Food: {len(env.food)}",
            f"Neurons: {neurons_count}",
            f"Axons: {axons_count}",
            f"Generations:",
            *generations
        ])
        pygame.display.flip()
        if step % 10 == 0:
            neurons_count = sum(map(lambda x: len(x.neurons), env.entities))
            axons_count = sum(
                map(lambda x: sum(map(lambda y: len(y.axons), x.neurons)), env.entities))
            generations = list(f" Gen {generation}: {number}" for generation, number in Counter(
                [d.generation for d in env.entities]).items())
        videowriter.write(pygame.surfarray.pixels3d(screen).swapaxes(1, 0).copy())
        if step % 100 == 0:
            dump_save(save_path)
        clock.tick(60)
    dump_save(save_path)
    videowriter.release()
    pygame.quit()
