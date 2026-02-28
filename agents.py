import random
from database import insert_agent


class Agent:
    def __init__(self, agent_id, name, post_probability, voice):
        self.id = agent_id
        self.name = name
        self.post_probability = post_probability
        self.voice = voice

    def decide_action(self, context):
        import random

        r = random.random()

        # 50% of post probability becomes replies if context exists
        if r < self.post_probability:
            if context:
                return random.choice(["post", "reply"])
            return "post"

        return "idle"

    def generate_post(self, tick):
        templates = {
            "noisy": [
                "I can't believe it's already tick {tick}. Things are moving fast.",
                "Another thought at tick {tick}: momentum matters.",
                "Tick {tick} and still pushing forward.",
            ],
            "balanced": [
                "Tick {tick}. Observing before acting.",
                "Steady progress at tick {tick}.",
                "Tick {tick}. Balance is everything.",
            ],
            "passive": [
                "Tick {tick}. Just watching.",
                "Quiet thoughts at tick {tick}.",
                "Still here at tick {tick}.",
            ]
        }

        options = templates[self.voice]
        return random.choice(options).format(tick=tick)

def create_default_agents(conn):
    agents = []

    configs = [
        ("PassiveAgent", 0.10, "passive"),
        ("BalancedAgent", 0.50, "balanced"),
        ("NoisyAgent", 0.80, "noisy"),
    ]

    for name, probability, voice in configs:
        agent_id = insert_agent(conn, name)
        agents.append(Agent(agent_id, name, probability, voice))

    return agents
