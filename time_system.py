from collections import deque

import pygame


class TimeSystem():
    def __init__(self):
        self.travellers = deque()

    def register(self, actor):
        self.travellers.append(actor)

    def release(self, actor):
        self.travellers.remove(actor)

    def tick(self, game_data, gfx_data):
        results = []
        if len(self.travellers) > 0:
            actor = self.travellers[0]
            self.travellers.rotate()
            actor.round_init()
            results.extend(actor.apply_effects())
            actor.action_points = min(actor.action_points + actor.round_speed, actor.round_speed * 1.5)
            turn_data = actor.take_turn(game_data, gfx_data)
            while turn_data:
                while not gfx_data.visuals.done:
                    gfx_data.windows.draw(game_data, gfx_data)
                    gfx_data.visuals.update(game_data, gfx_data)
                    gfx_data.clock.tick(gfx_data.fps_per_second)
                    pygame.display.flip()
                results.extend(turn_data.result)
                actor.action_points -= turn_data.action.cost
                turn_data = actor.take_turn(game_data, gfx_data)
        return results
