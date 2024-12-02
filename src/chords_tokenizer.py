class Chord:
    def __init__(self):
        self.root = 0
        self.beat = 0
        self.duration = 0
        self.type = 0
        self.inversion = 0
        self.applied = 0
        self.adds = []
        self.omits = []
        self.alterations = []
        self.suspensions = []
        self.alternate = ""
        self.borrowed = ""
        self.isRest = False
        self.recordingEndBeat = None


def encode(chords: list[Chord]):
    pass


def decode() -> list[Chord]:
    pass
