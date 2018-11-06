import tcod

from messages import Message


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        self.owner = None

    def add_item(self, item):
        results = []
        if len(self.items) >= self.capacity:
            results.append({
                "item_added": None,
                "message": Message("Your inventory is full", tcod.yellow)
            })
        else:
            results.append({
                "item_added": item,
                "message": Message("You pick up {}".format(item.name), tcod.light_blue)
            })
            self.items.append(item)
        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_func is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({"equip": item_entity})
            else:
                results.append({"message": Message("The {} can't be used".format(item_entity.name))})
        else:
            if item_component.targeting and not (kwargs.get("target_x") or kwargs.get("target_y")):
                results.append({"targeting": item_entity})
            else:
                kwargs = {**item_component.func_kwargs, **kwargs}
                item_use_results = item_component.use_func(self.owner, **kwargs)

                for res in item_use_results:
                    if res.get("consumed"):
                        self.remove_item(item_entity)

                results.extend(item_use_results)
        return results

    def drop(self, item):
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y
        self.remove_item(item)
        msg = Message("You dropped the {}".format(item.name))
        results.append({"item_dropped": item, "message": msg})
        return results

    def remove_item(self, item):
        self.items.remove(item)
