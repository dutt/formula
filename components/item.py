class Item:
    def __init__(self, use_func=None, targeting=False, targeting_message=None, **kwargs):
        self.use_func = use_func
        self.func_kwargs = kwargs
        self.targeting = targeting
        self.targeting_message = targeting_message
