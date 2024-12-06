from src.prepare_data import load_harmonys

# import musicpy.database
import musicpy as mp
import musicpy.database as db


def make_up_chord(raw_chord: dict[str, any]):
    """使用MusicPy库，将原始和弦数据转换为MusicPy和弦类型"""
    # 由于本项目使用首调，所以不妨设根音为C，不会影响其他判断
    base_note = mp.N("C5").up(raw_chord["root_pitch_class"])
    raw_interval = raw_chord["root_position_intervals"]
    chord = mp.chord(
        [base_note]
        + [base_note.up(sum(raw_interval[: i + 1])) for i in range(len(raw_interval))]
    )
    return chord


_polychords_dict = {
    (1, 4, 1, 4, 11): 0,
    (2, 3, 2, 4, 9): 1,
    (3, 3, 1, 4, 10): 2,
    (3, 4, 7, 4): 3,
    (3, 3, 3, 8): 4,
    (2, 3, 2, 4, 7): 5,
    (5, 1, 8): 6,
    (4, 3, 4, 4, 5): 7,
    (4, 3, 8, 3): 8,
    (4, 4, 3, 2, 6, 2): 9,
    (4, 3, 6, 4): 10,
    (4, 3, 3, 8, 2): 11,
}


def _encode_chord_type(chord_type):
    """对三音及以上的普通和弦类型编码"""
    chord_types = db.chordTypes.keys()
    chord_type_dict = {
        chord: idx for idx, chords in enumerate(chord_types) for chord in chords
    }
    return chord_type_dict.get(chord_type, None)


vocab_size = (
    len(db.NAME_OF_INTERVAL) + len(db.chordTypes.keys()) + len(_polychords_dict.keys())
)
print("vs:", vocab_size)


def encode_chord_interval(raw_chord: dict[str, any]):
    """根据和弦每两个音之间的相对音程列表编码和弦音程类型"""
    raw_interval = raw_chord["root_position_intervals"]
    # 当和弦是单音时直接返回0
    if len(raw_interval) == 0:
        return 0
    # 双音及以上和弦使用MusicPy分析
    chord = make_up_chord(raw_chord)
    detect = mp.alg.detect(
        chord,
        show_degree=True,
        get_chord_type=True,
    )
    # 当和弦是双音时编码为双音间音程
    if len(raw_interval) == 1:
        interval_name = detect.interval_name
        return db.NAME_OF_INTERVAL[interval_name]
    chord_type = detect.chord_type
    polychords = detect.polychords
    num_intervals = len(db.NAME_OF_INTERVAL)  # 22
    num_chord_types = len(db.chordTypes.keys())  # 61
    # 是普通和弦时接着前面继续编码
    if chord_type:
        # 可以正确得到编码时返回附加编码，否则返回-1
        code = _encode_chord_type(chord_type)
        return (code + num_intervals) if code != None else None
    # 是复合和弦时
    if polychords:
        offset = num_intervals + num_chord_types
        code = _polychords_dict[tuple(raw_interval)]
        print("p:", offset + code)
        return offset + code
        # polychords_encode_list = []
        # for chord_compose in polychords:
        #     polychords_encode_list.append(encode_chord_type(chord_compose.chord_type))
        # polychord_code = (
        #     offset
        #     + polychords_encode_list[0] * num_chord_types
        #     + polychords_encode_list[1]
        # )
        # print(polychords)
        # print(polychords_encode_list)
        # return polychord_code
        # # 仅对出现的复合和弦进行编码
        # # 创建或更新复合和弦编码字典
        # if not hasattr(encode_chord_interval, 'polychord_code_dict'):
        #     encode_chord_interval.polychord_code_dict = {}
        #     encode_chord_interval.next_polychord_code = num_intervals + num_chord_types  # 起始编码83
        # polychord_code_dict = encode_chord_interval.polychord_code_dict
        # # 获取复合和弦的名称
        # polychord_names = tuple(chord_compose.chord_type for chord_compose in polychords)
        # # 如果复合和弦未编码，分配新编码
        # if polychord_names not in polychord_code_dict:
        #     polychord_code_dict[polychord_names] = encode_chord_interval.next_polychord_code
        #     encode_chord_interval.next_polychord_code += 1
        # # 返回复合和弦的编码
        # return polychord_code_dict[polychord_names]
    return None

if __name__ == '__main__':
    harmonys = load_harmonys("test")
    # print(polychords[(1, 4, 1, 4, 11)])

    # for polychord in polychords:
    #     print(
    #         encode_chord_interval(
    #             {"root_position_intervals": polychord, "root_pitch_class": 0}
    #         )
    #     )
    # test_chord = load_harmonys("test")[0][0]

    # print(detect)


    # print(db.INTERVAL)
    # print(db.NAME_OF_INTERVAL)

    # print(db.chordTypes)

    # for _ in range(100):
    #     random_song = random.choice(harmonys)
    #     test_chord = random.choice(random_song)
    #     test_position_intervals = test_chord["root_position_intervals"]
    #     encode_chord_interval(test_position_intervals)

    count_chord_type = [0] * vocab_size
    for harmony in harmonys.values():
        for chord in harmony:
            count_chord_type[encode_chord_interval(chord)] += 1
    print(count_chord_type)


    # encode_chord_interval([2,3,2,4,9])
    # total_chord_types = len(db.chordTypes.keys())
    # print(total_chord_types)
