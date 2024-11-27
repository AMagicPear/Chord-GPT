import musicpy
from collections import Counter

yuan_verse = musicpy.read("./test_midis/垣主歌带主旋律.mid")
yuan_verse.clear_tempo()
yuan_verse.bpm = 90
# print(yuan_verse(0))
# print(yuan_verse(0) in musicpy.S('C major'))
# notes = yuan_verse(0).notes
# notes_name = [note.name for note in notes]
# print(set(notes_name))
chord_test = musicpy.chord('C#,D#,F,F#,G#,A#,C')

def detect_scale(piano_roll: musicpy.chord) -> musicpy.scale:
    """判定一段乐曲的调号"""
    # 歌曲中含有音名数恰好为7时 直接判定音阶
    notes_name = [note.name for note in piano_roll.notes]
    if(len(set(notes_name)) is 7):
        for i in range(12):
            if(piano_roll.up(i) in musicpy.S('C major')):
                return musicpy.S('C major').up(i)
    pass

if __name__=="__main__":
    print(detect_scale(chord_test))
    # musicpy.play(yuan_verse,wait=True)
    yuan_detected = musicpy.alg.detect_scale2(yuan_verse(0))
    print(yuan_detected)