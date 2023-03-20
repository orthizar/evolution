import sys
from entity import *
from food import *
from environment import *
from datetime import datetime
import json
import pygame
from pygame.locals import *
from collections import Counter
#import cv2
import os
import numpy as np
import copy
from visualize import *
from operator import attrgetter

env = None
step = 0

entities = 5
mutation_rate = 10
initial_food = 100
food_per_step = 20

number_of_neurons = 16
number_of_axons = 16


num_axs = 6

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode(
    [SCREEN_WIDTH, SCREEN_HEIGHT], pygame.DOUBLEBUF)

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
                          ray_stop=save['env']['ray_stop'], ray_steps=save['env']['ray_steps'], mutation_rate=save['env']['mutation_rate'], food_per_step=100)#save['env']['food_per_step'])
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
            'mutation_rate': env.mutation_rate,
            'food_per_step': env.food_per_step,
        }
    }
    with open(save_path, 'w') as savefile:
        json.dump(save, savefile)


def create_env():
    env = Environment(size=pygame.display.get_surface().get_size(), entities=[],
                      food=[], ray_stop=0.1, ray_steps=10, mutation_rate=mutation_rate, food_per_step=food_per_step, number_of_neurons=number_of_neurons, number_of_axons=number_of_axons)
    for _ in range(entities):
        dna = generate_dna(number_of_neurons, number_of_axons)
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


def draw_information(screen, text_array):
    for i, text in enumerate(text_array):
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (0, i*12))

def visualize_network(num_axs):
    for idx in range(min(num_axs, len(env.entities))):
        axons_visualize = []
        axon_activations = []
        node_activations = []
        entity = env.entities[idx]
        for neuron in entity.neurons:
            node_activations.append(neuron.output)
            for axon in neuron.axons:
                if axon['target_type'] == 'interneuron':
                    axons_visualize.append((entity.neurons.index(neuron), axon['target_index']%len(entity.neurons)))
                    axon_activations.append(entity.neurons[axon['target_index'] %
                                    len(entity.neurons)].output * axon['weight'])

        graph = create_graph(axons_visualize)
        render_graph(idx, graph, axon_activations, node_activations, f"G: {entity.generation}, L: {entity.lifetime}")
    if min(num_axs, len(env.entities)) < num_axs:
        clear_axs(range(len(env.entities),num_axs))
if __name__ == '__main__':
    if len(sys.argv) >= 2:
        save_path = sys.argv[1]
        video_path = f"videos/{os.path.basename(sys.argv[1]).split('.')[0]}.mp4"
        env = load_save(save_path)
    else:
        save_path = f"saves/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        video_path = f"videos/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.mp4"
        env = create_env()
    neurons = sum(map(lambda x: len(x.neurons), env.entities))
    axons = sum(
        map(lambda x: sum(map(lambda y: len(y.axons), x.neurons)), env.entities))
    generations = list(f" Gen {generation}: {number}" for generation, number in Counter(
        [d.generation for d in env.entities]).items())
    #os.rename(video_path, f"{video_path}.bak")
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #videowriter = cv2.VideoWriter(video_path, fourcc, 24, env.size)
    #old_video = cv2.VideoCapture(f"{video_path}.bak")
    #while (old_video.isOpened()):
        #ret, frame = old_video.read()
        #if ret == True:
            #videowriter.write(frame)
        #else:
            #break
    #old_video.release()
    #os.remove(f"{video_path}.bak")
    init_graph(num_axs, SCREEN_WIDTH//3, SCREEN_HEIGHT//3)

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
            f"Neurons: {neurons}",
            f"Axons: {axons}",
            f"Generations:",
            *generations
        ])
        if step % 1 == 0:
            visualize_network(num_axs)
            buffer, size = render_canvas()
            surf = pygame.image.frombuffer(buffer, size, "RGBA")
            screen.blit(surf, (((SCREEN_WIDTH//3)*2,(SCREEN_HEIGHT//3)*2)))
        pygame.display.flip()

        if step % 10 == 0:
            neurons = sum(map(lambda x: len(x.neurons), env.entities))
            axons = sum(
                map(lambda x: sum(map(lambda y: len(y.axons), x.neurons)), env.entities))
            generations = list(f" Gen {generation}: {number}" for generation, number in Counter(
                [d.generation for d in env.entities]).items())
        


            
        #videowriter.write(pygame.surfarray.pixels3d(screen).swapaxes(1, 0).copy())
        if step % 100 == 0:
            dump_save(save_path)
        clock.tick(60)
    dump_save(save_path)
    #videowriter.release()
    pygame.quit()
