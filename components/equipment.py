from components.equipmentslots import EquipmentSlots

class Equipment:
    def __init__(self, main_hand=None, off_hand=None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    @property
    def max_hp_bonus(self):
        return self._get_attrib(lambda e : e.max_hp_bonus)
    @property
    def power_bonus(self):
        return self._get_attrib(lambda e : e.power_bonus)
    @property
    def defense_bonus(self):
        return self._get_attrib(lambda e : e.defense_bonus)

    def _get_attrib(self, getter):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += getter(self.main_hand.equippable)
        if self.off_hand and self.off_hand.equippable:
            bonus += getter(self.off_hand.equippable)
        return bonus

    def toggle_equip(self, equippable_entity):
        results = []
        slot = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({"dequipped" : equippable_entity })
            else:
                if self.main_hand:
                    results.append({"dequipped" : self.main_hand })
                self.main_hand = equippable_entity
                results.append({"equipped" : equippable_entity})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({"dequipped" : equippable_entity })
            else:
                if self.off_hand:
                    results.append({"dequipped" : self.off_hand })
                self.off_hand = equippable_entity
                results.append({"equipped" : equippable_entity})

        return results