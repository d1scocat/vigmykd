from context import GameContext
from game.model import GameState
from player import Player
from registry import registries
from view.renderer import Renderer
from view.renderable import Renderable

from uuid import UUID


class ViewSystem:
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.renderables: dict[UUID, Renderable] = {}

    def update(self, model: GameState):
        adapter = registries.view_adapters[Player]
        if adapter is None:
            raise ValueError("No view adapter found for type Player")

        # current_render_tick can be float in the future
        # if i happen to be between logic ticks? idk just future-proofing
        # for now it isnt
        current_render_tick = float(model.tick_idx)

        for player in model.players.values():
            if player.player_id not in self.renderables:
                self.renderables[player.player_id] = adapter.create(player)

            renderable = self.renderables[player.player_id]
            adapter.update(player, renderable, model, current_render_tick)

    def submit(self, renderer: Renderer):
        for renderable in self.renderables.values():
            renderer.queue_renderable(renderable)
