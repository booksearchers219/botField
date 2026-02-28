class RuleBasedContentEngine:
    """
    Deterministic rule-based content generator.
    This replaces hardcoded content generation in Agent.
    """

    def generate_post(self, agent, tick, context):
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

        options = templates[agent.voice]
        return options[tick % len(options)].format(tick=tick)
