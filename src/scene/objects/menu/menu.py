from pygame.event import Event

from context import GameContext
from event.events import HTTPResponseEvent, SceneSwitchRequestEvent
from game.model import GameState
from scene.objects.menu import actions
from scene.scene import Scene
from ui.components.page import UIPage
from ui.components.text import UITextElement
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

import pygame

from typing import Any, Callable


class MenuScene(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("menu")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        local = ctx.local_player_id
        authenticated = local is not None

        self._ui_page = self.get_ui(
            ctx.ui_path / f"main-menu-{'' if authenticated else 'un'}authenticated.json"
        )

        self.action_mapping: dict[str, Callable[['Scene', GameState, GameContext], Any] | None] = {
            "show_login_overlay": actions.show_login_overlay,
            # "open_settings": ...,
            # "exit": ...,
            "submit_login_attempt": actions.submit_login_attempt,
            "play": actions.play,
        }

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def tick(self):
        super().default_tick(self.ctx, self.input_router)

    def render(self, view: Renderer, view_system: ViewSystem):
        view.drop_render_queue()

        self.page.process()
        self.page.resolve_layout(self.ctx.screen_size, self.ctx)
        self.page.submit_ui(view)

        view_system.update(self.model)
        view_system.submit(view)

    def login_listener(self, event: HTTPResponseEvent):
        if not hasattr(self, "login_req_id"):
            return

        waiting_id = getattr(self, "login_req_id")
        if event.request_id != waiting_id:
            return

        if not event.success:
            error_msg = self.page.by_id("stub-error")
            if error_msg is None or not isinstance(error_msg, UITextElement):
                self.ctx.logger.warning("No 'stub-error' available for MenuScene")
                return
            error_msg.set_raw(event.payload["error"])
            error_msg.set_state("shown")
            return

        # recreating a menu scene, now having successfully authenticated
        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(
            self.model, self.ctx
        )))

    def on_enter(self):
        self.lid = self.ctx.event_manager.register_listener(
            event_type=HTTPResponseEvent,
            func=self.login_listener
        )

    def on_exit(self):
        self.ctx.event_manager.unregister_listener(self.lid)

    def on_load(self):
        pass

    def find_action(self, action_name: str) -> Callable[[Scene, GameState, GameContext], Any] | None:
        return self.action_mapping.get(action_name)

    def on_event(self, event: Event) -> bool:
        return False
