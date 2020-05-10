import json

from components.ingredients import Ingredient, IngredientSerialization

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Ingredient):
            return { "__type__" : "Ingredient",
                     "value" : obj.name }
        return json.JSONEncoder.default(obj)

def JSONDecoder(data):
    if "__type__" in data:
        t = data["__type__"]
        if t == "Ingredient":
            return IngredientSerialization.deserialize(data["value"])
    return data

def serialize(data, indent=None):
    return json.dumps(data, indent=indent, cls=JSONEncoder)

def deserialize(data):
    return json.loads(text, object_hook=JSONDecoder)


def main():
    data = [Ingredient.FIRE]
    print(data)
    text = json.dumps(data, cls=JSONEncoder)
    print(text)
    d2 = json.loads(text, object_hook=JSONDecoder)
    print(d2)

if __name__ == "__main__":
    main()
