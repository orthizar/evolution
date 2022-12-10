import math
import random

# the two strands of dna consist of nucleotides which are composed of one of four nucleobases.
# the four types of nucleobases:
#  - c (cytosine)
#  - g (guanine)
#  - a (adenine)
#  - t (thymine)

# a neuron has a bias, an activation function as well as:
# axons:
#  - efferent nerve fibers (transmit information to a particular region).
#    efferent nerve fibers also have a weight.
#  - afferent nerve fibers (propagate the stimulation received from other regions).

# proofreading during synthesis.
# homologous recombination.
# non-homologous end joining.

# dna encoding
# the dna holds infomation about every neuron of the entity.
# '10'*16 (AAAAAAAAAAAAAAAA): start sequence of neuron
# 10000000 (ACCC) + 16 bit uint (x): weight of neuron where weight = 1/x

# 10000100 (ACGC): start sequence of efferent axon
# 10010100 (AGGC) + 16 bit uint (index): motory target of axon where index of motor = index, ignored when not efferent axon
# 10000110 (ACGA): start sequence of afferent axon
# 10010110 (AGGA) + 16 bit uint (index): sensory target of axon where index of sensor = index, ignored when not afferent axon
# 10010000 (AGCC) + 16 bit uint (index): interneuron target of axon where neuron index in dna = index, ignored when not axon or when sensory target already defined


def get_random_16_bit_uint():
  return '{0:016b}'.format(random.getrandbits(16))

def generate_dna():
  nucleotide_chain = ''
  for x in range(random.randint(16, 16)):
    nucleotide_chain += '10'*32 # start sequence of neuron
    nucleotide_chain += '10000000'+'10'*16 + get_random_16_bit_uint()
    for x in range(random.randint(16, 16)):
      if random.randint(0, 1): # efferent axon
        nucleotide_chain += '10000100'+'10'*16
        nucleotide_chain += '10010100'+'10'*16 + get_random_16_bit_uint()
      else: # afferent axon
        nucleotide_chain += '10000110'+'10'*16
        if random.randint(0, 1): # sensory target
          nucleotide_chain += '10010110'+'10'*16 + get_random_16_bit_uint()
        else: # interneuron target
          nucleotide_chain += '10010000'+'10'*16 + get_random_16_bit_uint()
  return (nucleotide_chain,)*2

class Entity:
  def __init__(self, dna):
    self.dna = dna
  def __str__(self):
    return self.dna[0]

def decode_neurons(nucleotides):
  neurons = []
  last_neuron = {}
  axons = []
  last_axon = {}
  index = 0
  while index < len(nucleotides):
    #print(index, len(nucleotides), nucleotides[index:index+8+32])
    print(str(index/len(nucleotides)*100) + '%')
    if index <= len(nucleotides)-64 and nucleotides[index:index+64] == '10'*32:
      index += 64
      if not last_neuron == {}:
        if not last_axon == {}:
          axons.append(last_axon)
          last_axon = {}
        last_neuron.update({'axons': axons})
        axons = []
        neurons.append(last_neuron)
        last_neuron = {}
    elif index <= len(nucleotides)-8-32:
      if nucleotides[index:index+8+32] == '10000000'+'10'*16:
        index += 8+32
        #print('weight')
        last_neuron.update({'weight': 1/int(nucleotides[index:index+16],2)})
        index += 16
      elif nucleotides[index:index+8+32] == '10000100'+'10'*16:
        index += 8+32
        if not last_axon == {}:
          axons.append(last_axon)
          last_axon = {}
        #print('efferent')
        last_axon.update({'type': 'efferent'})
      elif nucleotides[index:index+8+32] == '10000110'+'10'*16:
        index += 8+32
        if not last_axon == {}:
          axons.append(last_axon)
          last_axon = {}
        #print('afferent')
        last_axon.update({'type': 'afferent'})
      elif nucleotides[index:index+8+32] == '10010100'+'10'*16 and last_axon.get('type') == 'efferent':
        index += 8+32
        #print('motory')
        last_axon.update({'target_type': 'motory'})
        last_axon.update({'target_index': int(nucleotides[index:index+16],2)})
        index += 16
      elif nucleotides[index:index+8+32] == '10010110'+'10'*16 and last_axon.get('type') == 'afferent':
        index += 8+32
        #print('sensory')
        last_axon.update({'target_type': 'sensory'})
        last_axon.update({'target_index': int(nucleotides[index:index+16],2)})
        index += 16
      elif nucleotides[index:index+8+32] == '10010000'+'10'*16 and last_axon.get('type') == 'afferent':
        index += 8+32
        #print('interneuron')
        last_axon.update({'target_type': 'interneuron'})
        last_axon.update({'target_index': int(nucleotides[index:index+16],2)})
        index += 16
  if not last_neuron == {}:
    if not last_axon == {}:
          axons.append(last_axon)
          last_axon = {}
    last_neuron.update({'axons': axons})
    axons = []
    neurons.append(last_neuron)
    last_neuron = {}
  return neurons
          
    
dna = generate_dna()
print(dna[0])
nucleobases = ('C', 'G', 'A', 'T')
print('dna sequencing started')
neurons = decode_neurons(dna[0])
print('dna sequencing finished')
for neuron_index, neuron in enumerate(neurons):
  print(neuron_index, 'weight:', neuron['weight'])
  for axon_index, axon in enumerate(neuron['axons']):
    print(neuron_index, 'axon', axon_index, ':', 'target_type:', axon['target_type'],'target_index:', axon['target_index']%len(neurons))

#print(''.join(nucleobases[int(dna[0][x*2:x*2+2],2)] for x in range(len(dna[0])//2)))
##print(dna[0])
##print('-------')
##for neuron_index, neuron in enumerate(dna[0].split('10'*16)):
##  #print(neuron_index, neuron)
##  print(neuron_index, ''.join(nucleobases[int(neuron[x*2:x*2+2],2)] for x in range(len(neuron)//2)))
##  for axon_index, axon in enumerate(neuron.split('')
