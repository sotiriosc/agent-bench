from dataclasses import dataclass


@dataclass
class AgentConfig:
    model_provider: str = "local-dummy"  # 'openai', 'anthropic', etc.
    temperature: float = 0.2
    max_steps: int = 8
    self_consistency: int = 1
