from symposium.core import Router
from symposium.windows.impl.simple_manager import SimpleDialogManager
from symposium.windows.impl.transitions import TransitionManager
from symposium.windows.protocols.dialog_manager import DialogManager
from symposium.windows.protocols.storage import ContextQuery, StackStorage
from symposium.windows.protocols.window_sender import WindowSender
from symposium.windows.registry import DialogRegistry


class ManagerFactory:
    def __init__(
        self,
        router: Router,
        storge: StackStorage,
        registry: DialogRegistry,
        window_sender: WindowSender,
    ):
        self.router = router
        self.storge = storge
        self.registry = registry
        self.window_sender = window_sender

    async def manager(
        self,
        query: ContextQuery,
        framework_data: dict,
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
            window_sender=self.window_sender,
            framework_data=framework_data,
        )
