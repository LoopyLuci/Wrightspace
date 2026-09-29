"""webbuilder.ai.router.modelrouter — Re-exports ModelRouter from ai package."""
from webbuilder.ai import ModelRouter


def get_router() -> ModelRouter:
    """Get the singleton ModelRouter instance."""
    return ModelRouter.get()


__all__ = ["ModelRouter", "get_router"]
