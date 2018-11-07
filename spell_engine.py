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
            damage = 5
            damage_per_step = 5
            distance = 1
            distance_per_step = 3
            area = 0.5
            area_per_step = 0.5
            cooldown_per_slot = 3
            cooldown = len(slots) * cooldown_per_slot
            for slot in slots:
                if slot == Ingredient.EMPTY:
                    cooldown -= cooldown_per_slot
                elif slot == Ingredient.FIRE:
                    damage += damage_per_step
                elif slot == Ingredient.RANGE:
                    distance += distance_per_step
                elif slot == Ingredient.AREA:
                    area += area_per_step
            retr.append(Spell(slots=slots, cooldown=cooldown, spellidx=idx,
                              damage=damage, distance=distance, area=area))
        return retr


builder = SpellBuilder(num_slots=3, num_spells=1)
builder.slots = [[Ingredient.EMPTY for i in range(3)]]
#builder.slots = [[Ingredient.FIRE for i in range(3)]]
#builder.slots = [[Ingredient.FIRE, Ingredient.RANGE, Ingredient.AREA]]
Spell.EMPTY = SpellEngine.evaluate(builder)[0]
