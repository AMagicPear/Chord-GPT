import musicpy

# 调式转换字典
scale_encode: dict = {
    "major": 0,
    "dorian": 1,
    "phrygian": 2,
    "lydian": 3,
    "mixolydian": 4,
    "minor": 5,
    "locrian": 6,
    "harmonicMinor": 7,
    "phrygianDominant": 8,
}

# 调式反转换列表
scale_decode: list = [
    "major",
    "dorian",
    "phrygian",
    "lydian",
    "mixolydian",
    "minor",
    "locrian",
    "harmonicMinor",
    "phrygianDominant",
]


class Chord:
    """首调记法的和弦"""

    def __init__(self):
        self.root = 0  # 和弦的根音，以相对于调式根音的半音数表示
        self.beat = 0  # 和弦的起始拍（以绝对拍数计，从曲子的开始算起）
        self.duration = 0  # 和弦的持续时间（以拍为单位）
        self.type = 0  # 和弦的类型
        self.inversion = (
            0  # 和弦的转位，表示最低音的变化 0: 原位 1: 第一转位 2: 第二转位
        )
        self.applied = 0  # 功能性应用和弦（如副属和弦）。值为0表示不是应用和弦。
        self.adds = []  # 额外添加的音，列出添加音相对于根音的音程（半音数）。
        self.omits = []  # 省略的音，列出省略的音相对于根音的音程（半音数）。
        self.alterations = []  # 和弦的变音或音程修饰
        self.suspensions = []  # 挂留音，表示悬挂了某个和弦音并未解决。
        self.alternate = ""
        self.borrowed = ""  # 借用和弦，表示和弦来源于其他调性或调式。
        self.isRest = False  # 是否为休止符
        self.recordingEndBeat = None


def encode(chords: list[Chord]) -> list[list[int]]:
    """将每个和弦编码为数字列表"""
    encoded_chords = []
    for chord in chords:
        encoded_chord = [
            chord.root,
            chord.beat,
            chord.duration,
            chord.type,
            chord.inversion,
            chord.applied,
            chord.adds,
            chord.omits,
            chord.alterations,
            chord.suspensions,
            chord.alternate,
            scale_encode[chord.borrowed],
            chord.isRest,
            chord.recordingEndBeat,
        ]
        encoded_chords.append(encoded_chord)
    return encoded_chords

def decode(encoded_chords: list[list[int]]) -> list[Chord]:
    """将和弦的数字列表解码回和弦对象列表"""
    chords = []
    for encoded_chord in encoded_chords:
        chord = Chord()
        (
            chord.root,
            chord.beat,
            chord.duration,
            chord.type,
            chord.inversion,
            chord.applied,
            chord.adds,
            chord.omits,
            chord.alterations,
            chord.suspensions,
            chord.alternate,
            scale_decode[chord.borrowed],
            chord.isRest,
            chord.recordingEndBeat,
        ) = encoded_chord
        chords.append(chord)
    return chords

def chords_to_musicpy(chords: list[Chord]) -> musicpy.chord:
    """把本代码中定义和弦对象转换为musicpy的和弦对象"""
    pass
