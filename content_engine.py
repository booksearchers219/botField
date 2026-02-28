class RuleBasedContentEngine:
    """
    Deterministic rule-based content generator.
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


class OllamaContentEngine:
    """
    Simple Ollama-powered content generator.
    """

    def generate_post(self, agent, tick, context):
        import subprocess

        prompt = f"You are {agent.name}, a {agent.voice} personality. Write a short 1-2 sentence social media post."

        try:
            result = subprocess.run(
                ["ollama", "run", "llama2"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=60
            )

            if result.returncode != 0:
                return f"[LLM ERROR] {agent.name} failed to generate post."

            response = result.stdout.strip()

            if not response:
                return f"{agent.name} is thinking..."

            return response

        except subprocess.TimeoutExpired:
            return f"[LLM TIMEOUT] {agent.name} took too long."
        except Exception as e:
            return f"[LLM EXCEPTION] {str(e)}"
