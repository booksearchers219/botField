import re


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
    Ollama-powered content generator supporting posts and replies.
    Includes output sanitization.
    """

    def generate_post(self, agent, tick, context):
        import subprocess

        # Determine if this is a reply
        if context:
            first = context[0]
            try:
                target_text = first["content"]
            except Exception:
                target_text = str(first)

            prompt = f"""
You are {agent.name}, a {agent.voice} personality.

You are replying to this post:
{target_text}

Write a short natural reply (1-2 sentences).

Rules:
- Respond directly to the post.
- Do NOT explain what you are doing.
- Do NOT say "Here is".
- Do NOT say "Sure".
- Do NOT add quotation marks.
- Output ONLY the reply text.
- No emojis.
- No hashtags.
"""
        else:
            prompt = f"""
You are {agent.name}, a {agent.voice} personality.

Write exactly one short social media post (1-2 sentences).

Rules:
- Do NOT explain what you are doing.
- Do NOT say "Here is".
- Do NOT say "Sure".
- Do NOT add quotation marks.
- Output ONLY the post text.
- No emojis.
- No hashtags.
"""

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

            # -----------------------------
            # 🔧 Output Sanitization Layer
            # -----------------------------

            # Remove surrounding quotes
            response = response.strip('"').strip("'")

            # Remove emojis (basic unicode emoji ranges)
            response = re.sub(r'[\U00010000-\U0010ffff]', '', response)

            # Remove hashtags
            response = re.sub(r'#\w+', '', response)

            # Remove common meta phrases
            response = re.sub(
                r'^(Sure[, ]*|Here is[, ]*)',
                '',
                response,
                flags=re.IGNORECASE
            )

            # Collapse whitespace
            response = " ".join(response.split())

            return response

        except subprocess.TimeoutExpired:
            return f"[LLM TIMEOUT] {agent.name} took too long."
        except Exception as e:
            return f"[LLM EXCEPTION] {str(e)}"
