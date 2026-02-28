import random
from database import insert_post, insert_event, get_recent_posts
from content_engine import RuleBasedContentEngine


class Orchestrator:
    def __init__(self, agents, db, verbose=False):
        self.agents = agents
        self.db = db
        self.tick = 0
        self.verbose = verbose
        self.content_engine = RuleBasedContentEngine()

    def run(self, steps: int):
        for _ in range(steps):
            self.tick += 1
            self.process_tick()

    def process_tick(self):
        agent = self.pick_agent()

        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="AGENT_SELECTED",
            metadata={"agent_name": agent.name}
        )

        context = self.get_context()
        action = agent.decide_action(context)

        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="ACTION_DECIDED",
            metadata={"decision": action}
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
        content = self.content_engine.generate_post(
        agent=agent,
        tick=self.tick,
        context=self.get_context()
        )

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

        if self.verbose:
            print(f"\n[Tick {self.tick}] NEW POST")
            print(f"  Author: {agent.name}")
            print(f"  Post ID: {post_id}")
            print(f"  Content: {content}")

            # Optional: print feed after each new post
            self.print_feed()

    def log_idle(self, agent):
        insert_event(
            self.db,
            tick=self.tick,
            agent_id=agent.id,
            action_type="AGENT_IDLE",
            metadata={"reason": "probability_check_failed"}
        )

        if self.verbose:
            print(f"[Tick {self.tick}] {agent.name} -> idle")

    def print_feed(self):
        cursor = self.db.cursor()
        rows = cursor.execute(
            """
            SELECT posts.id, agents.name, posts.content
            FROM posts
            JOIN agents ON posts.author_id = agents.id
            ORDER BY posts.id
            """
        ).fetchall()

        print("\n--- CURRENT FEED ---")
        for post_id, name, content in rows:
            print(f"{post_id} | {name} | {content}")
        print("--------------------")

    def print_summary(self):
        cursor = self.db.cursor()

        total_events = cursor.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        total_posts = cursor.execute(
            "SELECT COUNT(*) FROM posts"
        ).fetchone()[0]

        idle_count = cursor.execute(
            "SELECT COUNT(*) FROM events WHERE action_type='AGENT_IDLE'"
        ).fetchone()[0]

        print("\n--- Run Summary ---")
        print(f"Total ticks: {self.tick}")
        print(f"Total events: {total_events}")
        print(f"Total posts: {total_posts}")
        print(f"Total idle events: {idle_count}")

        print("\nPosts per agent:")

        rows = cursor.execute(
            """
            SELECT agents.name, COUNT(posts.id)
            FROM agents
            LEFT JOIN posts ON agents.id = posts.author_id
            GROUP BY agents.name
            """
        ).fetchall()

        for name, count in rows:
            print(f"  {name}: {count}")

        post_rate = (total_posts / self.tick) * 100 if self.tick else 0
        print(f"\nPost rate: {post_rate:.2f}%")
