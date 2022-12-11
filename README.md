# evolution
## Introduction
This code is a simulation of evolution that uses artificial neural networks to control the behavior of the entities in the simulation. The simulation takes place in an environment with food, which the entities need to eat in order to survive and reproduce. The entities in the simulation have neural networks that control their behavior, and their neural networks are mutated over time in order to help them adapt to their environment. The code uses Pygame to display the simulation and to handle user input, and it uses JSON to save and load the state of the simulation and it exports video via OpenCV.

The code generates a string representing the properties of a neuron, such as its bias, the weights of its axons, and the targets of its axons. This "DNA" string is composed of nucleobases, which are the building blocks of DNA in real life. The nucleobases in the code are represented by the letters 'c', 'g', 'a', and 't'.

In the code, entities have sensors that allow them to "see" the food in a given range. The output of the sensors is used by the neural network of the entity to make decisions, such as moving towards food. The sensors use a "ray casting" algorithm to simulate the behavior of light rays. The ray starts from the position of the entity and is being casted in a particular direction, specified by an angle. The ray continues until it reaches the edge of its range or until it hits a piece of food. The output of the sensor is the distance from the sensor to the closest piece of food and is being used by neurons with interneuron connection to the sensor.

Overall, the code is a simplified and abstracted representation of a biological neuron and the genetic material that encodes its properties. It is not a direct representation of real DNA or neurons, but rather a computational model inspired by them.

## Installation
### Clone
Clone this repository:
```
https://github.com/orthizar/evolution.git
```
Or via SSH:
```
git@github.com:orthizar/evolution.git
```
Or via Github CLI:
```
gh repo clone orthizar/evolution
```
### Install dependencies
```
pip3 install numpy pygame opencv
```

## Usage
To start the simulation run:
```
python main.py
```

To continue a simulation run:
```
python main.py ./saves/YYYY-mm-dd-HH-MM-SS
```

## Feedback
Please provide any feedback under https://github.com/orthizar/evolution/issues or via mail to [silvankohler@protonmail.com](mailto:silvankohler@protonmail.com).