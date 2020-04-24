class Mode(object):
    Ajout = 1
    Modification = 2
    Suppression = 3

    def __init__(self, mode: int):
        self.mode = mode

    def toStr(self):
        if self.mode == Mode.Ajout:
            return "Ajout"
        elif self.mode == Mode.Modification:
            return "Modification"
        elif self.mode == Mode.Suppression:
            return "Suppression"
