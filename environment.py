import math
from typing import Union
import random
from entity import *
from food import *
import threading


class Environment:
    def __init__(self, size=(1000, 1000), entities=[], food=[], ray_stop=0.01, ray_steps=100, mutation_rate=10, food_per_step=100) -> None:
        self.size = size
        self.entities = entities
        self.food = food
        self.ray_stop = ray_stop
        self.ray_steps = ray_steps
        self.mutation_rate = mutation_rate
        self.food_per_step = food_per_step

    def cast(self, start, angle, ray_range) -> Union[None, float]:
        ray_position = start
        last_distance = math.inf
        for _ in range(self.ray_steps):
            closest_food = min(self.food, key=lambda x: math.sqrt(
                (x.position[0]-ray_position[0])**2+(x.position[1]-ray_position[1])**2))
            min_distance = math.sqrt(
                (closest_food.position[0]-ray_position[0])**2+(closest_food.position[1]-ray_position[1])**2)
            if min_distance > last_distance or min_distance > ray_range:
                return math.inf
            else:
                last_distance = min_distance
                if min_distance-closest_food.radius < self.ray_stop:
                    return math.sqrt((start[0]-ray_position[0])**2+(start[1]-ray_position[1])**2)
                ray_position = (ray_position[0]+(math.cos(angle)*min_distance/2),
                                ray_position[1]+(math.sin(angle)*min_distance/2))
        return math.inf

    def update_entity(self, entity):
        if entity.hunger >= 100:
            self.entities.remove(entity)
            del entity
            return
        for sensor in entity.sensors:
            sensor.update()
        entity.update(self)
        # print(entity.color, entity.lifetime, entity.food, entity.hunger, entity.position)
        if entity.food >= 2:
            #print("Cloning entity")
            entity.food = 0
            dna = mutate_dna(entity.data, self.mutation_rate)
            self.entities.append(Entity(
                dna=dna, environment=self, position=entity.position, generation=entity.generation+1))

    def step(self):
        if len(self.food) < self.food_per_step:
            for _ in range(self.food_per_step):
                self.food.append(
                    Food((random.random()*self.size[0], random.random()*self.size[1])))
        if len(self.entities) < 1:
            dna = generate_dna(512, 128)
            self.entities.append(
                Entity(dna, self, (random.random()*self.size[0], random.random()*self.size[1])))
        threads = []
        for entity in self.entities:
            thread = threading.Thread(
                target=self.update_entity, args=(entity,))
            threads.append(thread)

        # Start each thread
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
