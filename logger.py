class Logger:
    def __init__(self, file_name : str = None, append : bool = True) -> None:
        if file_name:
            self.file = open(file_name, 'a' if append else 'w')
        else:
            self.file = None
        
    def __call__(self, msg : str) -> None:
        if self.file:
            self.file.write(msg)
        else:
            print(msg)