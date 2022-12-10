import math
import random
import threading

# the two strands of dna consist of dna which are composed of one of four nucleobases.
# the four types of nucleobases:
#  - c (cytosine)
#  - g (guanine)
#  - a (adenine)
#  - t (thymine)

# a neuron has a bias, an activation function as well as:
# axons:
#  - efferent nerve fibers (transmit information to a particular region).
#    afferent nerve fibers also have a weight.
#  - afferent nerve fibers (propagate the stimulation received from other regions).

# proofreading during synthesis.
# homologous recombination.
# non-homologous end joining.

# dna encoding
# the dna holds infomation about every neuron and other properties of the entity.

# 11000000 (TCCC) + '10'*16 + 8 bit uint (r) + 8 bit uint (g) + 8 bit uint (b): color of entity where color = (r,g,b)

# '10'*32 (AAAAAAAAAAAAAAAA): start sequence of neuron
# 10000000 (ACCC) + '10'*16 + 16 bit uint (x): bias of neuron where bias = x

# 10000100 (ACGC) + '10'*16 : start sequence of axon
# 10010100 (AGGT) + '10'*16  + 16 bit uint (x): weight of axon where weight = (x/(2**16))*2-1
# 10010110 (AGGA) + '10'*16  + 16 bit uint (index): sensory target of axon where index of sensor = index
# 10010111 (AGCC) + '10'*16  + 16 bit uint (index): interneuron target of axon where neuron index in dna = index, ignored when sensory target already defined


def sigmoid(x) -> float:
    return 1 / (1 + math.exp(-x))
    # return 0.5 * (1 + x / (1 + abs(x)))


def relu(x) -> float:
    return x if x > 0 else 0


def get_random_n_bit_uint(n: int) -> str:
    return '{0:0{n}b}'.format(random.getrandbits(n), n=n)


def uint_to_bits(x: int, n: int) -> str:
    return '{0:0{n}b}'.format(x, n=n)


def generate_dna(number_of_neurons, number_of_axons) -> str:
    nucleotide_chain = ''
    # color
    nucleotide_chain += '11000000'+'10'*16 + \
        get_random_n_bit_uint(8) + get_random_n_bit_uint(8) + \
        get_random_n_bit_uint(8)
    for _ in range(number_of_neurons):
        # print(x/number_of_neurons*100, '%')
        nucleotide_chain += '10'*32  # start sequence of neuron
        nucleotide_chain += '10000000'+'10'*16 + get_random_n_bit_uint(16)
        for _ in range(number_of_axons):
            if random.randint(0, 1):  # start sequence of axon
                nucleotide_chain += '10000100'+'10'*16
                nucleotide_chain += '10010100'+'10' * \
                    16 + get_random_n_bit_uint(16)
                if random.randint(0, 1):  # sensory target
                    nucleotide_chain += '10010110'+'10' * \
                        16 + get_random_n_bit_uint(16)
                else:  # interneuron target
                    nucleotide_chain += '10010111'+'10' * \
                        16 + get_random_n_bit_uint(16)
    return nucleotide_chain


def encode_dna(data) -> str:
    nucleotide_chain = ''
    nucleotide_chain += '11000000'+'10'*16 + \
        uint_to_bits(data['color'][0], 8) + uint_to_bits(data['color']
                                                         [1], 8) + uint_to_bits(data['color'][2], 8)
    for neuron in data['neurons']:
        nucleotide_chain += '10'*32
        nucleotide_chain += '10000000'+'10'*16 + \
            uint_to_bits(int(neuron['bias']*(2**16)), 16)
        for axon in neuron['axons']:
            nucleotide_chain += '10000100'+'10'*16
            nucleotide_chain += '10010100'+'10'*16 + \
                uint_to_bits(int(((axon['weight']+1)/2)*(2**16)), 16)
            if axon['target_type'] == 'sensory':
                nucleotide_chain += '10010110'+'10'*16
            elif axon['target_type'] == 'interneuron':
                nucleotide_chain += '10010111'+'10'*16
            nucleotide_chain += uint_to_bits(axon['target_index'], 16)
    return nucleotide_chain


def decode_dna(dna) -> dict:
    data = {}
    neurons = []
    last_neuron = {}
    axons = []
    last_axon = {}
    index = 0
    while index < len(dna):
        # print(index, len(dna), dna[index:index+64])
        if dna[index:index+64] == '10'*32:
            # print(str(index/len(dna)*100), '%')
            index += 64
            if not last_neuron == {}:
                if not last_axon == {}:
                    axons.append(last_axon)
                    last_axon = {}
                last_neuron.update({'axons': axons})
                axons = []
                neurons.append(last_neuron)
                last_neuron = {}
        elif dna[index:index+8+32] == '10000000'+'10'*16:
            index += 8+32
            # print('bias')
            last_neuron.update(
                {'bias': (int(dna[index:index+16], 2)/(2**16))})
            index += 16
        elif dna[index:index+8+32] == '11000000'+'10'*16:
            index += 8+32
            # print('color')
            data.update({'color': (int(dna[index:index+8], 2), int(
                dna[index+8:index+16], 2), int(dna[index+16:index+24], 2))})
            index += 24
        elif dna[index:index+8+32] == '10000100'+'10'*16:
            index += 8+32
            # print('axon')
            if not last_axon == {}:
                axons.append(last_axon)
                last_axon = {}
        elif dna[index:index+8+32] == '10010100'+'10'*16:
            index += 8+32
            # print('weight')
            if int(dna[index:index+16], 2)-1 != 0:
                last_axon.update(
                    {'weight': (int(dna[index:index+16], 2)/(2**16))*2-1})
            else:
                last_axon.update({'weight': 0})
            index += 16
        elif dna[index:index+8+32] == '10010110'+'10'*16:
            index += 8+32
            # print('sensory')
            last_axon.update({'target_type': 'sensory'})
            last_axon.update(
                {'target_index': int(dna[index:index+16], 2)})
            index += 16
        elif dna[index:index+8+32] == '10010111'+'10'*16:
            index += 8+32
            # print('interneuron')
            last_axon.update({'target_type': 'interneuron'})
            last_axon.update(
                {'target_index': int(dna[index:index+16], 2)})
            index += 16
    if not last_neuron == {}:
        if not last_axon == {}:
            axons.append(last_axon)
            last_axon = {}
        last_neuron.update({'axons': axons})
        axons = []
        neurons.append(last_neuron)
        last_neuron = {}
    data.update({'neurons': neurons})
    return data


def mutate_dna(data, rate) -> str:
    # data = decode_dna(dna)
    nucleotide_chain = ''
    nucleotide_chain += '11000000'+'10'*16 + \
        uint_to_bits(data['color'][0], 8) + uint_to_bits(data['color']
                                                         [1], 8) + uint_to_bits(data['color'][2], 8)
    for neuron in data['neurons']:
        nucleotide_chain += '10'*32
        if random.randint(rate, 100) == 100:
            nucleotide_chain += '10000000'+'10'*16 + \
                get_random_n_bit_uint(16)
        else:
            nucleotide_chain += '10000000'+'10'*16 + \
                uint_to_bits(int(neuron['bias']*(2**16)), 16)
        for axon in neuron['axons']:
            nucleotide_chain += '10000100'+'10'*16
            if random.randint(rate, 100) == 100:
                nucleotide_chain += '10010100'+'10'*16 + \
                    get_random_n_bit_uint(16)
            else:
                nucleotide_chain += '10010100'+'10'*16 + \
                    uint_to_bits(int(((axon['weight']+1)/2)*(2**16)), 16)
            if random.randint(rate, 100) == 100:
                if random.randint(0, 1):  # sensory target
                    nucleotide_chain += '10010110'+'10' * \
                        16 + get_random_n_bit_uint(16)
                else:  # interneuron target
                    nucleotide_chain += '10010111'+'10' * \
                        16 + get_random_n_bit_uint(16)
            else:
                if axon['target_type'] == 'sensory':
                    nucleotide_chain += '10010110'+'10'*16
                elif axon['target_type'] == 'interneuron':
                    nucleotide_chain += '10010111'+'10'*16
                if random.randint(rate, 100) == 100:
                    nucleotide_chain += get_random_n_bit_uint(16)
                else:
                    nucleotide_chain += uint_to_bits(axon['target_index'], 16)
    return nucleotide_chain


class Neuron:
    def __init__(self, bias, axons) -> None:
        self.bias = bias
        self.output = 0
        self.axons = axons
        self.position = (0, 0)

    def activate(self, x) -> float:
        return sigmoid(x)

    def update(self, neurons, sensors) -> None:
        output = 0
        for axon in self.axons:
            if axon['target_type'] == 'sensory':
                output += sensors[axon['target_index'] %
                                  len(sensors)].output * axon['weight']
            elif axon['target_type'] == 'interneuron':
                # print('output', neurons[axon['target_index'] % len(neurons)].output)
                output += neurons[axon['target_index'] %
                                  len(neurons)].output * axon['weight']
        output += self.bias
        self.output = self.activate(output)


class Sensor:
    def __init__(self, angle, range, entity) -> None:
        self.angle = angle
        self.range = range
        self.entity = entity
        self._output = 0

    def update(self):
        self._output = relu(
            1-(self.entity.environment.cast(self.entity.position, self.angle, self.range)/(self.range)))

    @property
    def output(self):
        return self._output


class Entity:
    def __init__(self, dna, environment,  position=(0, 0), lifetime=0, generation=0, hunger=0) -> None:
        self.dna = dna
        self.color = (0, 0, 0)
        self.neurons = []
        self.sensors = []
        self.init_neurons()
        self.init_sensors()
        self.position = position
        self.lifetime = lifetime
        self.generation = generation
        self.hunger = hunger
        self.food = 0
        self.environment = environment

    def init_neurons(self) -> None:
        self.data = decode_dna(self.dna)
        self.color = self.data.get('color', (0, 0, 0))
        # print(data)
        neurons = self.data.get('neurons', [])
        for neuron in neurons:
            n = Neuron(neuron.get('bias', 1), neuron.get('axons', []))
            self.neurons.append(n)
            # n.output = random.randint(-1, 1)

    def init_sensors(self) -> None:
        for _ in range(10):
            self.sensors.append(
                Sensor(random.random()*2*math.pi, random.random()*100, self))

    def update(self, environment) -> None:
        self.lifetime += 1
        self.hunger += 1
        for neuron in self.neurons:
            neuron.update(self.neurons, self.sensors)
            # print(neuron.output)
        speed = self.neurons[0].output*5
        direction = self.neurons[1].output*2*math.pi
        self.position = ((self.position[0] + speed*math.sin(direction)) % environment.size[0],
                         (self.position[1] + speed*math.cos(direction)) % environment.size[1])
        closest_food = min(environment.food, key=lambda x: math.sqrt(
            (x.position[0]-self.position[0])**2+(x.position[1]-self.position[1])**2))
        if math.sqrt((closest_food.position[0]-self.position[0])**2+(closest_food.position[1]-self.position[1])**2) <= 5:
            self.hunger = 0
            self.food += 1
            environment.food.remove(closest_food)
            del closest_food


def convert_to_bits(num) -> str:
    bits = int(max(8, math.log(num, 2)+1))
    return ''.join(['1' if num & (1 << (bits-1-n)) else '0' for n in range(bits)])


if __name__ == '__main__':
    dna = generate_dna(64, 64)
    # print(dna[:8+32+24])
    # print(len(dna))
    # nucleobases = ('C', 'G', 'A', 'T')
    # print(''.join(nucleobases[int(dna[x*2:x*2+2],2)] for x in range(len(dna)//2)))
    #test_entity = Entity(dna)
    # for x in range(10):
    # test_entity.update()
    # print(test_entity.position)
    # for neuron in test_entity.neurons:
    #     print(neuron.output)

    print('dna sequencing started')
    data = decode_dna(dna)
    print('dna sequencing finished')
    print(dna)
    print(encode_dna(data))
    print(dna == encode_dna(data))
    # print(data['color'])
    # print(convert_to_bits(data['color'][0]))
    # print(convert_to_bits(data['color'][1]))
    # print(convert_to_bits(data['color'][2]))
    # for neuron_index, neuron in enumerate(neurons):
    #   print(neuron_index, 'bias:', neuron['bias'])
    #   for axon_index, axon in enumerate(neuron['axons']):
    #     print(neuron_index, 'axon', axon_index, ':', 'type', axon['type'], 'target_type:', axon['target_type'],'target_index:', axon['target_index']%len(neurons))

    # print(dna[0])
    # print('-------')
    # for neuron_index, neuron in enumerate(dna[0].split('10'*16)):
    # print(neuron_index, neuron)
    ##  print(neuron_index, ''.join(nucleobases[int(neuron[x*2:x*2+2],2)] for x in range(len(neuron)//2)))
    # for axon_index, axon in enumerate(neuron.split('')
