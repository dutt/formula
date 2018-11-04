from components.ingredients import Ingredient
from components.spell import Spell


class SpellBuilder:
    def __init__(self, num_slots, num_spells):
        self.currslot = 0
        self.currspell = 0
        self.num_slots = num_slots
        self.num_spells = num_spells
        self.slots = [[Ingredient.EMPTY for i in range(num_slots)] for i in range(num_spells)]

    def set_slot(self, slot, ingredient):
        print("setting spell {} slot {} to {}".format(self.currspell, slot, ingredient))
        self.slots[self.currspell][slot] = ingredient

    @property
    def current_slots(self):
        return self.slots[self.currspell]

    def slots_for_spell(self, spell_index):
        return self.slots[spell_index]


class SpellEngine:
    def __init__(self, player):
        self.player = player

    @staticmethod
    def evaluate(spellbuilder):
        retr = []
        for idx, spell in enumerate(range(spellbuilder.num_spells)):
            slots = spellbuilder.slots_for_spell(spell)
            damage = 10
            distance = 1
            area = 1
            cooldown = len(slots)
            for slot in slots:
                if slot == Ingredient.EMPTY:
                    cooldown -= 1
                elif slot == Ingredient.FIRE:
                    damage += 10
                elif slot == Ingredient.RANGE:
                    distance += 5
                elif slot == Ingredient.AREA:
                    area += 1
            print("Spell {} evalutaed to range={}, damage={}, area={}".format(idx, distance, damage, area))
            retr.append(Spell(slots=slots, cooldown=cooldown, damage=damage, distance=distance, area=area))
        return retr


builder = SpellBuilder(num_slots=3, num_spells=1)
builder.slots = [[Ingredient.FIRE for i in range(3)]]
Spell.EMPTY = SpellEngine.evaluate(builder)[0]
