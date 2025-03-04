class Log:
    """
    Class representing loggings of various kind of operations as a list of dictionary entries
    """

    def __init__(self) -> None:
        self.data:list[dict] = []
    

    def add_entry(self, entry:dict) -> None:
        self.data.append(entry)

    
    def add_head_entry(self, entry:dict) -> None:
        self.data.insert(0, entry)
    

    def get_data(self) -> list[dict]:
        return self.data


    def to_string(self) -> str:
        return self.__str__()
    

    def __str__(self) -> str:
        out = ""
        for entry in self.data:
            out += str(entry) + "\n"
        return out
