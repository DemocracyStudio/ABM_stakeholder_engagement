# visualisation window
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement
import math

#Model imports
from main import SEmodel
import main as m

# red
negative_color = "#FF0000"
# grey
neutral_color = "#808080"
# positive
positive_color = "#0400ff"


def network_portrayal(G):
    # the model ensures that there is always 1 agent per node

    def node_color(agent):
        if agent.opinion > 0.5:
            return positive_color
        if agent.opinion < -0.5:
            return negative_color
        return neutral_color

    def edge_color(agent1, agent2):
        if (agent1.opinion > 0.5 and agent2.opinion > 0.5):
            return positive_color
        if (agent1.opinion < -0.5 and agent2.opinion < -0.5):
            return negative_color
        return neutral_color

    def edge_width(agent1, agent2):
        if (agent1.opinion > 0.5 and agent2.opinion > 0.5):
            return 3
        if (agent1.opinion > 0.5 and agent2.opinion > 0.5):
            return 3
        return 2

    def get_edges(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": "id: {}<br>opinion: {}".format(
                agents[0].unique_id, agents[0].opinion
            )
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_edges(source, target)),
            "width": edge_width(*get_edges(source, target))
        }
        for (source, target) in G.edges
    ]

    return portrayal


# instantiate network module
network = NetworkModule(network_portrayal, 500, 500, library="d3")

# map data to chart in the ChartModule
chart = ChartModule(
    [
        {"Label": "Neutral", 'Color': neutral_color},
        {"Label": "Negative", 'Color': negative_color},
        {"Label": "Positive", 'Color': positive_color}
    ]
)


class MyTextElement(TextElement):
    def render(self, model):
        ratio = model.positive_negative_ratio()
        ratio_text = "&infin;" if ratio is math.inf else "{0:.2f}".format(ratio)
        positive_text = str(m.num_positive(model))
        negative_text = str(m.num_negative(model))

        return "Positive/Negative Ratio: {}<br>Positive Opinion: {}<br>Negative Opinion: {}".format(
            ratio_text, positive_text, negative_text
        )


# model parameters settable from interface
model_parameters = {
    "num_nodes": UserSettableParameter(
        "slider",
        "Number of nodes",
        100,
        10,
        1000,
        10,
        description="Number of nodes to include in the model"
    ),
    "avg_node_degree": UserSettableParameter(
        "slider",
        "Average node degree",
        2,
        1,
        5,
        0.1,
        description="Average number of links from each node"
    ),
    "initial_opinion": UserSettableParameter(
        "slider",
        "Initial opinion of undetermined nodes",
        0,
        -1,
        1,
        0.1,
        description="Opinion of the undetermined population."
    ),
    "public_sector_opinion": UserSettableParameter(
        "slider",
        "Public sector opinion",
        0,
        -1,
        1,
        1,
        description="Opinion of public sector stakeholder."
    ),
    "corpo_opinion": UserSettableParameter(
        "slider",
        "Corporate companies opinion",
        0,
        -1,
        1,
        1,
        description="Opinion of corporate companies stakeholder."
    ),
    "startup_opinion": UserSettableParameter(
        "slider",
        "Startup business opinion",
        0,
        -1,
        1,
        1,
        description="Opinion of startup business stakeholder."
    ),
    "academic_opinion": UserSettableParameter(
        "slider",
        "Academic sector opinion",
        0,
        -1,
        1,
        1,
        description="Opinion of academic sector stakeholder."
    ),
    "civil_opinion": UserSettableParameter(
        "slider",
        "Civil society opinion",
        0,
        -1,
        1,
        1,
        description="Opinion of civil society stakeholder."
    ),
    "media_opinion": UserSettableParameter(
        "slider",
        "Media industry opinion",
        0,
        -1,
        1,
        1,
        description="Opinion of media industry stakeholder."
    )
}

# create server
server = ModularServer(
    SEmodel, [network, MyTextElement(), chart], "Stakeholder Engagement Model", model_parameters
)
server.port = 8518  # default port