from context import GameContext
from game.model import GameState
from player import Player
from registry import registries
from view.renderer import Renderer
from view.renderable import Renderable

from uuid import UUID


class ViewSystem:
    ctx: GameContext
    renderables: dict[UUID, Renderable]

    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.renderables = {}

    def update(self, model: GameState):
        adapter = registries.view_adapters[Player]
        if adapter is None:
            raise ValueError("No view adapter found for type Player")

        for player in model.players.values():
            if player.player_id not in self.renderables:
                self.renderables[player.player_id] = adapter.create(player)

            renderable = self.renderables[player.player_id]
            adapter.update(player, renderable)

    def submit(self, renderer: Renderer):
        for renderable in self.renderables.values():
            renderer.queue_renderable(renderable)
