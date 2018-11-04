from random import randint

def random_choice_index(chances):
    rnd = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if rnd <= running_sum:
            return choice
        choice += 1

def random_choice_from_dict(data):
    choices = list(data.keys())
    chances = list(data.values())
    return choices[random_choice_index(chances)]

def from_dungeon_level(table, dungeon_level):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0
