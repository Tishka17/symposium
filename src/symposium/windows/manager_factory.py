from symposium.core import Router
from symposium.windows.impl.simple_manager import SimpleDialogManager
from symposium.windows.impl.transitions import TransitionManager
from symposium.windows.protocols.dialog_manager import DialogManager
from symposium.windows.protocols.storage import ContextQuery, StackStorage
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
    ) -> DialogManager:
        stack, context = await self.storge.load_locked(query)
        transition_manager = TransitionManager(
            chat=query.chat,
            context=context,
            stack=stack,
            storage=self.storge,
        )
        return SimpleDialogManager(
            chat=query.chat,
            registry=self.registry,
            transition_manager=transition_manager,
        )
