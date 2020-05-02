from util import Pos


class Console:
    @staticmethod
    def parse(command):
        return command

    @staticmethod
    def run(data, game):
        global_data = {"game": game, "Pos": Pos}
        try:
            if "=" in data and "==" not in data:
                return exec(data, global_data)
            else:
                return eval(data, global_data)
        except Exception as ex:
            return str(ex)

    @staticmethod
    def encode(result_data):
        return repr(result_data)

    @staticmethod
    def execute(command, game_data):
        data = Console.parse(command)
        result_data = Console.run(data, game_data)
        if not result_data:
            return []
        result_text = Console.encode(result_data)
        return [result_text]
