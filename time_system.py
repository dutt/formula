from collections import deque

class TimeSystem():
    def __init__(self):
        self.travellers = deque()

    def register(self, actor):
        self.travellers.append((actor))

    def release(self, actor):
        self.travellers.remove(actor)

    def tick(self, game_data):
        results = []
        if len(self.travellers) > 0:
            actor = self.travellers[0]
            print("actor {}".format(actor))
            self.travellers.rotate()
            actor.action_points += actor.speed
            turn_data = actor.take_turn(game_data)
            while turn_data:
                results.extend(turn_data.result)
                actor.action_points -= turn_data.action.cost
                turn_data = actor.take_turn(game_data)
        return results
