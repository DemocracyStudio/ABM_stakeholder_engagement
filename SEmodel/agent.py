from mesa import Agent

class Agent(Agent):
    # a member of the general population
    def __init__(
            self,
            unique_id,
            model,
            engagement,  # network activity
            trustability,  # influence limitation
            influenceability,  # sensitivity to neighbors opinion
            recovery,  # capacity to recover its initial opinion
            experience,  # gain experience at each recovery
            initial_opinion,  # defined manually through interface
            # independent variable
            opinion  # y-axis to test
    ):
        super().__init__(unique_id, model)
        self.engagement = engagement
        self.trustability = trustability
        self.influenceability = influenceability
        self.recovery = recovery
        self.experience = experience
        self.initial_opinion = initial_opinion
        self.opinion = initial_opinion

    def step(self):
        # determine what agents do at each step:
        self.check_neighbors()
        self.try_to_influence()
        self.recover()
        self.rescale_values()

    def check_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        self.neutral_neighbors = [agent for agent in
                                  self.model.grid.get_cell_list_contents(neighbors_nodes)
                                  if agent.opinion > -0.5 and agent.opinion < 0.5]
        self.positive_neighbors = [agent for agent in
                                   self.model.grid.get_cell_list_contents(neighbors_nodes)
                                   if agent.opinion > 0.5]
        self.negative_neighbors = [agent for agent in
                                   self.model.grid.get_cell_list_contents(neighbors_nodes)
                                   if agent.opinion < - 0.5]

    def try_to_influence(self):
        # if opinion positive or negative, try to influence neighbors
        # if neighbor neutral, influences
        # if neighbor agree, influences
        # if neighbor disagree, battle.
        # the strongest influences, the weakest loses trustability
        # if tie, nothing happens.
        # when influences, wins engagement depending on others' influenceability
        if self.opinion <= -0.5:  # negative
            for a in self.neutral_neighbors:
                a.opinion -= 0.1 * self.trustability * self.engagement
                self.engagement += 0.05 - (0.05 * a.influenceability)
            for a in self.negative_neighbors:
                a.opinion -= 0.1 * self.trustability * self.engagement
                self.engagement += 0.01 - (0.01 * a.influenceability)
            for a in self.positive_neighbors:
                if abs(self.opinion) - abs(a.opinion) > 0:  # negative is stronger
                    a.opinion -= 0.1 * self.trustability * self.engagement
                    self.engagement += 0.1 - (0.1 * a.influenceability)
                if abs(self.opinion) - abs(a.opinion) < 0:  # positive is stronger
                    self.opinion += 0.1 * a.trustability * self.engagement
                    self.trustability -= 0.1
        if self.opinion >= 0.5:  # positive
            for a in self.neutral_neighbors:
                a.opinion += 0.1 * self.trustability * self.engagement
                self.engagement += 0.05 - (0.05 * a.influenceability)
            for a in self.positive_neighbors:
                a.opinion += 0.1 * self.trustability * self.engagement
                self.engagement += 0.01 - (0.01 * a.influenceability)
            for a in self.negative_neighbors:
                if abs(self.opinion) - abs(a.opinion) > 0:  # positive is stronger
                    a.opinion += 0.1 * self.trustability * self.engagement
                    self.engagement += 0.1 - (0.1 * a.influenceability)
                if abs(self.opinion) - abs(a.opinion) < 0:  # negative is stronger
                    self.opinion -= 0.1 * a.trustability * self.engagement
                    self.trustability -= 0.1

    def recover(self):
        # if opinion != initial opinion, recover depending on experience
        # when recover, gain experience depending on influenceability
        # the more influenceable, the less experience win
        if self.opinion != self.initial_opinion:
            self.opinion = self.opinion * self.recovery * self.experience
            self.experience += 0.1 - (0.1 * self.influenceability)

    def rescale_values(self):
        if self.opinion < -1:
            self.opinion = -1
        if self.opinion > 1:
            self.opinion = 1