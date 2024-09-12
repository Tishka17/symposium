from symposium.core import Router
from symposium.windows.impl.simple_manager import SimpleTransitionManager
from symposium.windows.protocols.storage import ContextQuery, StackStorage
from symposium.windows.protocols.transition_manager import TransitionManager
from symposium.windows.registry import DialogRegistry


class ManagerFactory:
    def __init__(
        self,
        router: Router,
        storge: StackStorage,
        registry: DialogRegistry,
    ):
        self.router = router
        self.storge = storge
        self.registry = registry

    async def manager(
        self,
        query: ContextQuery,
    ) -> TransitionManager:
        stack, context = await self.storge.load_locked(query)
        return SimpleTransitionManager(
            chat=query.chat,
            context=context,
            stack=stack,
            registry=self.registry,
            storage=self.storge,
        )
