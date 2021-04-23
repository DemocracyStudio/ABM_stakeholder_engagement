import pandas as pd
import numpy as np
import random
import math
from enum import Enum

import networkx as nx

# modelling
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid

# data collection
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner


# notebook visualisation
import matplotlib.pyplot as plt

# clustering automation feature
import multilevel_mesa as mlm

import agent


# datacollector functions
def num_negative(model):
    # return number of negative opinions
    num_negative = [a for a in model.schedule.agents if a.opinion < -0.5]
    return len(num_negative)


def num_neutral(model):
    # return number of neutral opinions
    num_neutral = [a for a in model.schedule.agents if a.opinion < 0.5 and a.opinion > -0.5]
    return len(num_neutral)


def num_positive(model):
    # return number of positive opinions
    num_positive = [a for a in model.schedule.agents if a.opinion > 0.5]
    return len(num_positive)


def total_engagement(model):
    # engagement level in the population
    agent_engagement = [a.engagement for a in model.schedule.agents]
    return sum(agent_engagement)


def total_trustability(model):
    # trustability level in the population
    agent_trustability = [a.trustability for a in model.schedule.agents]
    return sum(agent_trustability)


def total_recovery(model):
    # recovery level in the population
    agent_recovery = [a.recovery for a in model.schedule.agents]
    return sum(agent_recovery)


def total_experience(model):
    # experience level in the population
    agent_experience = [a.experience for a in model.schedule.agents]
    return sum(agent_experience)


def public_opinion(model):
    # orientation of the population
    agent_opinion = [a.opinion for a in model.schedule.agents]
    return sum(agent_opinion) / num_nodes


class SEmodel(Model):
    # manual model has parameters set by user interface
    def __init__(
            self,
            num_nodes=100,
            avg_node_degree=3,
            # taipei : 1.92
            # telaviv : 2.16
            # tallinn : 2.20,
            engagement=0.49,
            trustability=0.21,
            influenceability=0.53,
            recovery=0.63,
            experience=1,
            initial_opinion=0,
            opinion=0,
            public_sector_opinion=1,
            corpo_opinion=1,
            startup_opinion=1,
            academic_opinion=-1,
            civil_opinion=-1,
            media_opinion=-1
    ):
        # set network layout
        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        # set space and time of the model
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        # set model parameters
        self.engagement = engagement
        self.trustability = trustability
        self.influenceability = influenceability
        self.recovery = recovery
        self.experience = experience
        self.initial_opinion = initial_opinion
        self.opinion = initial_opinion
        self.public_sector_opinion = public_sector_opinion
        self.corpo_opinion = corpo_opinion
        self.startup_opinion = startup_opinion
        self.academic_opinion = academic_opinion
        self.civil_opinion = civil_opinion
        self.media_opinion = media_opinion
        # set data collection
        self.datacollector = DataCollector(
            {
                "Negative": num_negative,
                "Neutral": num_neutral,
                "Positive": num_positive,
                "Total Engagement": total_engagement,
                "Total Trustability": total_trustability,
                "Total Recovery": total_recovery,
                "Total Experience": total_experience,
            }
        )

        # create agents with average parameters taken on #city tweets
        for i, node in enumerate(self.G.nodes()):
            a = agent.Agent(i,
                      self,
                      self.engagement,
                      self.trustability,
                      self.influenceability,
                      self.recovery,
                      self.experience,
                      self.initial_opinion,  # fixed by interface
                      self.opinion
                      )
            self.schedule.add(a)
            # add the undetermined agents to the network
            self.grid.place_agent(a, node)

        # create 1 representative of each stakeholder category
        public_sector = self.random.sample(self.G.nodes(), 1)
        for a in self.grid.get_cell_list_contents(public_sector):
            a.engagement = 0.57
            a.trustability = 0.53
            a.influenceability = 0.59
            a.recovery = 0.70
            a.experience = 1
            a.initial_opinion = public_sector_opinion  # fixed by interface
            a.opinion = a.initial_opinion

        corporate = self.random.sample(self.G.nodes(), 1)
        for a in self.grid.get_cell_list_contents(corporate):
            a.engagement = 0.75
            a.trustability = 0.49
            a.influenceability = 0.68
            a.recovery = 0.73
            a.experience = 1
            a.initial_opinion = corpo_opinion  # fixed by interface
            a.opinion = a.initial_opinion

        startup = self.random.sample(self.G.nodes(), 1)
        for a in self.grid.get_cell_list_contents(startup):
            a.engagement = 0.69
            a.trustability = 0.29
            a.influenceability = 0.68
            a.recovery = 0.97
            a.experience = 1
            a.initial_opinion = startup_opinion  # fixed by interface
            a.opinion = a.initial_opinion

        academic = self.random.sample(self.G.nodes(), 1)
        for a in self.grid.get_cell_list_contents(academic):
            a.engagement = 0.49
            a.trustability = 0.20
            a.influenceability = 0.65
            a.recovery = 0.75
            a.experience = 1
            a.initial_opinion = academic_opinion  # fixed by interface
            a.opinion = a.initial_opinion

        civil = self.random.sample(self.G.nodes(), 1)
        for a in self.grid.get_cell_list_contents(civil):
            a.engagement = 0.43
            a.trustability = 0.21
            a.influenceability = 0.69
            a.recovery = 0.72
            a.experience = 1
            a.initial_opinion = civil_opinion  # fixed by interface
            a.opinion = a.initial_opinion

        media = self.random.sample(self.G.nodes(), 1)
        for a in self.grid.get_cell_list_contents(media):
            a.engagement = 0.50
            a.trustability = 0.23
            a.influenceability = 0.65
            a.recovery = 0.71
            a.experience = 1
            a.initial_opinion = media_opinion  # fixed by interface
            a.opinion = a.initial_opinion

        self.running = True
        self.datacollector.collect(self)
        print('Finished initialising model, network has %s nodes' % self.G.nodes)
        nx.draw_networkx(self.G)
        #plt.show()

    def positive_negative_ratio(self):
        try:
            return num_positive(self) / num_negative(self)
        except ZeroDivisionError:
            return 0.00

    def step(self):
        # advance the model by one step and collect data
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()