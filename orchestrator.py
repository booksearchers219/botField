import random

from database import (
    insert_post,
    insert_event,
    get_recent_posts,
)


class Orchestrator:
    def __init__(self, agents, db):
        self.agents = agents
        self.db = db
        self.tick = 0

    def run(self, steps: int):
        for _ in range(steps):
            self.tick += 1
            self.process_tick()

    def process_tick(self):
        agent = self.pick_agent()

        # Log agent selection
        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="AGENT_SELECTED",
            metadata={
                "agent_name": agent.name
            }
        )

        context = self.get_context()

        action = agent.decide_action(context)

        # Log decision
        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="ACTION_DECIDED",
            metadata={
                "decision": action
            }
        )

        if action == "post":
            self.create_post(agent)
        else:
            self.log_idle(agent)

    def pick_agent(self):
        return random.choice(self.agents)

    def get_context(self):
        return get_recent_posts(self.db, limit=5)

    def create_post(self, agent):
        content = f"Tick {self.tick}: Post from {agent.name}"

        post_id = insert_post(
            self.db,
            author_id=agent.id,
            content=content
        )

        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="POST_CREATED",
            metadata={
                "post_id": post_id,
                "content_length": len(content)
            }
        )

    def log_idle(self, agent):
        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="AGENT_IDLE",
            metadata={
                "reason": "probability_check_failed"
            }
        )
