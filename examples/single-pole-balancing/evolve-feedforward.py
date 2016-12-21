"""
Single-pole balancing experiment using a feed-forward neural network.
"""

from __future__ import print_function

import os
import pickle

import cart_pole

import neat
import visualize

runs_per_net = 5
num_steps = 60000 # equivalent to 1 minute of simulation time


# Use the NN network phenotype and the discrete actuator force function.
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        fitnesses = []

        for runs in range(runs_per_net):
            sim = cart_pole.CartPole()

            # Run the given simulation for up to num_steps time steps.
            fitness = 0.0
            for s in range(num_steps):
                inputs = sim.get_scaled_state()
                action = net.activate(inputs)

                # Apply action to the simulated cart-pole
                force = cart_pole.discrete_actuator_force(action)
                sim.step(force)

                # Stop if the network fails to keep the cart within the position or angle limits.
                # The per-run fitness is the number of time steps the network can balance the pole
                # without exceeding these limits.
                if abs(sim.x) >= sim.position_limit or abs(sim.theta) >= sim.angle_limit_radians:
                    break

                fitness += 1.0

            fitnesses.append(fitness)

        # The genome's fitness is its worst performance across all runs.
        genome.fitness = min(fitnesses)


# Load the config file, which is assumed to live in
# the same directory as this script.
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultStagnation, config_path)

pop = neat.Population(config)
stats = neat.StatisticsReporter()
pop.add_reporter(stats)
pop.add_reporter(neat.StdOutReporter())
winner = pop.run(eval_genomes, 2000)

# Save the winner.
with open('winner-feedforward', 'wb') as f:
    pickle.dump(winner, f)

print(winner)

visualize.plot_stats(stats, ylog=True, view=True)
visualize.plot_species(stats, view=True)

node_names = {-1: 'x', -2: 'dx', -3: 'theta', -4: 'dtheta', 0: 'control'}
visualize.draw_net(config, winner, True, node_names=node_names)

visualize.draw_net(config, winner, view=True, node_names=node_names, filename="winner-feedforward.gv")
visualize.draw_net(config, winner, view=True, node_names=node_names, filename="winner-feedforward-enabled.gv", show_disabled=False)
visualize.draw_net(config, winner, view=True, node_names=node_names, filename="winner-feedforward-enabled-pruned.gv", show_disabled=False, prune_unused=True)


