from context import GameContext
from scene.scene import Scene
from ui.components.text import UITextElement
from ui.components.textarea import UITextArea


def show_login_overlay(scene: Scene, ctx: GameContext):
    form = scene.page.by_id("login-form")
    button = scene.page.by_id("login-button")
    if not form or not button:
        ctx.logger.warning("No 'login-form' or no 'login-button' available for MenuScene")
        return

    form.set_state("shown")
    button.set_state("hidden")


def submit_login_attempt(scene: Scene, ctx: GameContext):
    login = scene.page.by_id("login-textarea")
    password = scene.page.by_id("password-textarea")
    if not login or not password:
        ctx.logger.warning("No 'login-textarea' or no 'password-textarea' "
                                 "available for MenuScene")
        return
    
    if not (isinstance(login, UITextArea) and isinstance(password, UITextArea)):
        ctx.logger.warning("'login-textarea' or 'password-textarea' in MenuScene "
                                 "is not textarea")
        return

    login = login.value
    password = password.value

    try:
        req_id = ctx.auth.login({"login": login, "password": password})
    except AttributeError:
        error_msg = scene.page.by_id("stub-error")
        if not error_msg or not isinstance(error_msg, UITextElement):
            ctx.logger.warning("No 'stub-error' available for MenuScene")
            return
        error_msg.set_i18n("login-form.not-everything-filled-error")
        error_msg.set_state("shown")
        return

    setattr(scene, "login_req_id", req_id)
