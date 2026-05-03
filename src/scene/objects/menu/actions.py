from context import GameContext
from scene.scene import Scene


def show_login_overlay(scene: Scene, ctx: GameContext):
    form = scene.page.by_id("login-form")
    button = scene.page.by_id("login-button")
    if not form or not button:
        ctx.logger.warning("No 'login-form' or no 'login-button' available for MenuScene")
        return

    form.set_state("shown")
    button.set_state("hidden")
