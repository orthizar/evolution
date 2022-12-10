import sys
from entity import *
from food import *
from environment import *
from datetime import datetime
import json
import pygame
from collections import Counter

env = None
step = 0

entities = 50
mutation_rate = 10
initial_food = 400
food_per_step = 30

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

pygame.display.set_caption('evolution')

font = pygame.font.SysFont("Consolas", 12)

running = True

clock = pygame.time.Clock()


def load_save(save_path):
    global step
    with open(f'{save_path}', 'r') as savefile:
        save = json.load(savefile)
        step = save['step']
        env = Environment(size=save['env']['size'], entities=[], food=[],
                          ray_stop=save['env']['ray_stop'], ray_steps=save['env']['ray_steps'], mutation_rate=save['env']['mutation_rate'], food_per_step=save['env']['food_per_step'])
        env.entities = list(map(lambda x: Entity(
            x['dna'], env, x['position'], x['lifetime'], x['generation'], x['hunger']), save['env']['entities']))
        env.food = list(
            map(lambda x: Food(x['position'], x['radius']), save['env']['food']))
    return env


def dump_save(save_path):
    save = {
        'step': step,
        'env': {
            'size': env.size,
            'ray_stop': env.ray_stop,
            'ray_steps': env.ray_steps,
            'entities': list(map(lambda x: {'dna': x.dna, 'position': x.position, 'lifetime': x.lifetime, 'generation': x.generation, 'hunger': x.hunger}, env.entities)),
            'food': list(map(lambda x: {'position': x.position, 'radius': x.radius}, env.food)),
            'mutation_rate': mutation_rate,
            'food_per_step': food_per_step,
        }
    }
    with open(save_path, 'w') as savefile:
        json.dump(save, savefile)


def create_env():
    env = Environment(size=(1000, 1000), entities=[],
                      food=[], ray_stop=0.1, ray_steps=10, mutation_rate=mutation_rate, food_per_step=food_per_step)
    for _ in range(entities):
        dna = generate_dna(64, 64)
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
        pygame.draw.circle(screen, entity.color,
                           entity.position, math.log2(entity.lifetime)+2)


def draw_information(screen, text_array):
    for i, text in enumerate(text_array):
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (0, i*12))


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        save_path = sys.argv[1]
        env = load_save(save_path)
    else:
        save_path = f"saves/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        env = create_env()
    neurons = sum(map(lambda x: len(x.neurons), env.entities))
    axons = sum(map(lambda x: sum(map(lambda y: len(y.axons), x.neurons)), env.entities))
    generations = list(f" Gen {generation}: {number}" for generation, number in Counter([d.generation for d in env.entities]).items())
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        env.step()
        step += 1
        screen.fill((255, 255, 255))
        draw_food(screen)
        draw_entities(screen)
        draw_information(screen, [
            f"Savepath: {save_path}",
            f"Step: {step}",
            f"Entities: {len(env.entities)}",
            f"Food: {len(env.food)}",
            f"Neurons: {neurons}",
            f"Axons: {axons}",
            f"Generations:",
            *generations
        ])
        pygame.display.flip()
        if step % 100 == 0:
            neurons = sum(map(lambda x: len(x.neurons), env.entities))
            axons = sum(map(lambda x: sum(map(lambda y: len(y.axons), x.neurons)), env.entities))
            generations = list(f" Gen {generation}: {number}" for generation, number in Counter([d.generation for d in env.entities]).items())
            dump_save(save_path)
        clock.tick(60)
    dump_save(save_path)
    pygame.quit()
