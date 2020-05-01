class Inventory():
    def __init__(self, max_count, num_quickslots):
        self.items = []
        self.max_count = max_count
        self.quickslots = self.setup_quickslots(num_quickslots)

    def setup_quickslots(self, count):
        retr = {}
        for idx in range(count):
            retr[idx] = None
        return retr

    def get_quickslot(self, index):
        if not index in self.quickslots:
            return None
        return self.quickslots[index]

    def set_quickslot(self, index, item):
        if item:
            assert item in self.items
        self.quickslots[index] = item

    def has_free_spot(self):
        return self.max_count > len(self.items)

    def add(self, item):
        if len(self.items) >= self.max_count:
            return False

        self.items.append(item)

        # set unused quickslot
        for idx, qsitem in self.quickslots.items():
            if not qsitem:
                self.set_quickslot(idx, item)
                break
        return True

    def use(self, item):
        assert item
        assert item in self.items
        self.items.remove(item)
        for qs_index, qs_item in self.quickslots.items():
            if qs_item != item:
                continue
            for i in self.items:
                if type(i) == type(item):
                    self.set_quickslot(qs_index, i)
                    break
            else:
                self.set_quickslot(qs_index, None)
