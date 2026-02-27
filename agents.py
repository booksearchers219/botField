import random
from database import insert_agent


class Agent:
    def __init__(self, agent_id, name, post_probability):
        self.id = agent_id
        self.name = name
        self.post_probability = post_probability

    def decide_action(self, context):
        """
        context: list of recent posts (unused in v0.1)
        returns: "post" or "idle"
        """
        roll = random.random()

        if roll < self.post_probability:
            return "post"

        return "idle"


def create_default_agents(conn):
    """
    Creates three baseline agents:
    - Passive (10% post chance)
    - Balanced (50% post chance)
    - Noisy (80% post chance)
    """

    agents = []

    configs = [
        ("PassiveAgent", 0.10),
        ("BalancedAgent", 0.50),
        ("NoisyAgent", 0.80),
    ]

    for name, probability in configs:
        agent_id = insert_agent(conn, name)
        agents.append(Agent(agent_id, name, probability))

    return agents
