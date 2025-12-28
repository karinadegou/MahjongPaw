# -*- coding: utf-8 -*-
import random

class Tile:
    """
    麻将牌类:
    麻将牌堆本质上是136个元素被分成了34个集合，其中赤宝牌像是被打上了特殊的记号
    麻将牌类的属性本质就是一个维护了各种麻将牌编码的映射族
    """

    """
    第一位1,2,3,4,5代表万，筒，索，字，赤宝；
    第二位代表顺序：万筒索，1-9.东南西北，白发中
    """
    tile_dict = {11: 0, 12: 1, 13: 2, 14: 3, 15: 4, 16: 5, 17: 6, 18: 7, 19: 8,
                 21: 9, 22: 10, 23: 11, 24: 12, 25: 13, 26: 14, 27: 15, 28: 16, 29: 17,
                 31: 18, 32: 19, 33: 20, 34: 21, 35: 22, 36: 23, 37: 24, 38: 25, 39: 26,
                 41: 27, 42: 28, 43: 29, 44: 30, 45: 31, 46: 32, 47: 33,
                 51: 4, 52: 13, 53: 22}
    """
    34编码
    """
    tile_graph_dict = [
        "🀇", "🀈", "🀉", "🀊", "🀋", "🀌", "🀍", "🀎", "🀏", "🀙", "🀚", "🀛", "🀜", "🀝", "🀞", "🀟", "🀠", "🀡",
        "🀐", "🀑", "🀒", "🀓", "🀔", "🀕", "🀖", "🀗", "🀘", "🀀", "🀁", "🀂", "🀃", "🀆", "🀅", "🀄", "[🀋]", "[🀝]",
        "[🀔]"
    ]
    """
    宝牌指示牌
    """
    bonus_dict = {8: 0, 17: 9, 26: 18, 30: 27, 33: 31}

    EAST, SOUTH, WEST, NORTH = 27, 28, 29, 30
    BLANK, FORTUNE, CENTER = 31, 32, 33
    WINDS = [27, 28, 29, 30]
    THREES = [31, 32, 33]
    HONORS = [27, 28, 29, 30, 31, 32, 33]

    ONES, NINES = [0, 9, 18], [8, 17, 26]
    TERMINALS = [0, 8, 9, 17, 18, 26]
    ONENINE = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]
    GREENS = [19, 20, 21, 23, 25, 32]
    GOOD_PAIR = ONENINE + [1, 7, 10, 16, 19, 25]

    RED_MAN, RED_PIN, RED_SOU = 16, 52, 88
    RED_BONUS = [16, 52, 88]

    index_to_chow = [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8],
                     [9, 10, 11], [10, 11, 12], [11, 12, 13], [12, 13, 14], [13, 14, 15], [14, 15, 16], [15, 16, 17],
                     [18, 19, 20], [19, 20, 21], [20, 21, 22], [21, 22, 23], [22, 23, 24], [23, 24, 25], [24, 25, 26]]

    desc = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
            '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
            '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
            'east', 'south', 'west', 'north', 'blank', 'fortune', 'center']

    @staticmethod
    def cal_bonus_tiles(bonus_indicators_34):
        """
        根据宝牌指示牌计算真正的宝牌（34 种编号制）

        参数：
            bonus_indicators_34:
                - int  ：单张宝牌指示牌（0~33）
                - list ：多张宝牌指示牌列表（用于里宝牌 / 多宝牌）

        返回：
            list[int] ：对应的宝牌编号（34 制）
        """
        p1_dict = {8: 0, 17: 9, 26: 18, 30: 27, 33: 31}
        if isinstance(bonus_indicators_34, int):
            return [p1_dict.get(bonus_indicators_34, bonus_indicators_34 + 1)]
        if isinstance(bonus_indicators_34, list):
            res = []
            for b in bonus_indicators_34:
                res.append(p1_dict.get(b, b + 1))
            return res

    @staticmethod
    def has_chow(tiles, chow):
        """
        判断手牌中是否可以组成指定的吃（顺子）

        参数：
            tiles : list[int]
                玩家当前手牌（34 种编号制）

            chow : list[int]
                目标顺子，例如：
                    [0, 1, 2]   → 123万
                    [9, 10, 11] → 123筒
                    [18,19,20]  → 123索

        返回：
            bool
                True  ：手牌中可以组成该顺子
                False ：不可以
        """
        return all(t in tiles and t//9 == chow[0]//9 and t < 27 for t in chow)

    @staticmethod
    def tiles34_to_string(tiles):
        """
        将一组麻将牌转化为格式化字符串
        :param tiles:
        :return:
        """
        tiles.sort()
        man = [t for t in tiles if t < 9]
        pin = [t - 9 for t in tiles if 9 <= t < 18]
        suo = [t - 18 for t in tiles if 18 <= t < 27]
        chr = [t - 27 for t in tiles if t >= 27]
        m = man and ''.join([str(m + 1) for m in man]) + 'm' or ''
        p = pin and ''.join([str(p + 1) for p in pin]) + 'p' or ''
        s = suo and ''.join([str(b + 1) for b in suo]) + 's' or ''
        z = chr and ''.join([str(ch + 1) for ch in chr]) + 'z' or ''
        return m + p + s + z

    @staticmethod
    def t34_to_g(tiles):
        """
        34编码麻将牌转图像
        :param tiles:
        :return:
        """
        if isinstance(tiles, int):
            if tiles >= 0:
                return Tile.tile_graph_dict[tiles]
        if isinstance(tiles, list):
            if len(tiles) > 0 and isinstance(tiles[0], list):
                graphs = ""
                for meld in tiles:
                    graphs += ''.join([Tile.tile_graph_dict[t] for t in meld if t >= 0]) + " "
                return graphs
            else:
                graphs = [Tile.tile_graph_dict[t] for t in tiles if t >= 0]
                return ''.join(graphs)

    @staticmethod
    def tile136_to_string(tiles):
        """
        把136编码的一组麻将牌转为格式化字符串
        :param tiles:
        :return:
        """
        tiles34 = [t//4 for t in tiles]
        return Tile.tiles34_to_string(tiles34)

    @staticmethod
    def t136_to_g(tiles):
        """
        136编码麻将牌转图像
        :param tiles:
        :return:
        """
        tiles34 = None
        if isinstance(tiles, int):
            tiles34 = tiles // 4
        if isinstance(tiles, list):
            if len(tiles) > 0 and isinstance(tiles[0], list):
                tiles34 = [[t // 4 for t in m] for m in tiles]
            else:
                tiles34 = [t // 4 for t in tiles]
        if tiles34:
            return Tile.t34_to_g(tiles34)
        else:
            return ""

    @staticmethod
    def print_partition(melds):
        """
        列表转字符串
        :param melds:
        :return:
        """
        res = ""
        for m in melds:
            res += Tile.t34_to_g(m) + " "
        print(res)

    @staticmethod
    def partition_graph(melds):
        """
        列表转字符串
        :param melds:
        :return:
        """
        res = ""
        for m in melds:
            res += Tile.t34_to_g(m) + " "
        return res

    @staticmethod
    def to_34(tiles):
        """
        从整型或列表中返回34编码的麻将牌
        :param tiles: 两位编码
        :return: 34编码
        """
        if isinstance(tiles, int):
            return Tile.tile_dict[tiles]
        elif isinstance(tiles, list):
            return [Tile.tile_dict[t] for t in tiles]
        else:
            print("Wrong parameters: Tile.to_34()")

    @staticmethod
    def indicator60_to_bonus(tiles60):
        """
        将两位编码转为34编码，然后返回宝牌
        dict.get(key, default)，有kv，则返回v，否则返回default
        :param tiles60:
        :return:
        """
        if isinstance(tiles60, int):
            return Tile.bonus_dict.get(Tile.to_34(tiles60), Tile.to_34(tiles60) + 1)
        elif isinstance(tiles60, list):
            return [Tile.bonus_dict.get(t, t + 1) for t in Tile.to_34(tiles60)]
        else:
            print("Wrong parameters: Tile.indicator_to_bonus(tiles60)")

    @staticmethod
    def self_winds(dealer):
        """
        返回玩家自风
        :param dealer: 玩家
        :return: 自风
        """
        return Tile.WINDS[(4 - dealer):] + Tile.WINDS[0:(4 - dealer)]

    @staticmethod
    def same_type(a, b):
        """
        判断牌的类型是否相同
        :param a:
        :param b:
        :return:
        """
        return a // 9 == b // 9

class MahjongTile:
    """
    麻将牌类：
    麻将牌可以是一个长方形块，也可以是一张纸牌，脱离了实体进入软件中，就成了带有名字的对象。
    """

    code_34 = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
     '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
     '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
     'east', 'south', 'west', 'north', 'blank', 'fortune', 'center']

    bonus_dict = {8: 0, 17: 9, 26: 18, 30: 27, 33: 31}

    EAST, SOUTH, WEST, NORTH = 27, 28, 29, 30
    BLANK, FORTUNE, CENTER = 31, 32, 33
    WINDS = [27, 28, 29, 30]
    THREES = [31, 32, 33]
    HONORS = [27, 28, 29, 30, 31, 32, 33]

    ONES, NINES = [0, 9, 18], [8, 17, 26]
    TERMINALS = [0, 8, 9, 17, 18, 26]
    ONENINE = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]
    GREENS = [19, 20, 21, 23, 25, 32]
    GOOD_PAIR = ONENINE + [1, 7, 10, 16, 19, 25]

    index_to_chow = [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8],
                     [9, 10, 11], [10, 11, 12], [11, 12, 13], [12, 13, 14], [13, 14, 15], [14, 15, 16], [15, 16, 17],
                     [18, 19, 20], [19, 20, 21], [20, 21, 22], [21, 22, 23], [22, 23, 24], [23, 24, 25], [24, 25, 26]]

    AREA = ['Wall', 'River', 'Dead_Wall', 'Hand', 'Meld']

    "136编码"
    RED_MAN, RED_PIN, RED_SOU = 16, 52, 88
    RED_BONUS = [16, 52, 88]

    # 中文名称对照
    chinese_names = {
        '1m': '一万', '2m': '二万', '3m': '三万', '4m': '四万', '5m': '五万',
        '6m': '六万', '7m': '七万', '8m': '八万', '9m': '九万',
        '1p': '一筒', '2p': '二筒', '3p': '三筒', '4p': '四筒', '5p': '五筒',
        '6p': '六筒', '7p': '七筒', '8p': '八筒', '9p': '九筒',
        '1s': '一条', '2s': '二条', '3s': '三条', '4s': '四条', '5s': '五条',
        '6s': '六条', '7s': '七条', '8s': '八条', '9s': '九条',
        'east': '东', 'south': '南', 'west': '西', 'north': '北',
        'blank': '白', 'fortune': '发', 'center': '中'
    }

    # 麻将牌图像
    tile_graph_dict = [
        "🀇", "🀈", "🀉", "🀊", "🀋", "🀌", "🀍", "🀎", "🀏", "🀙", "🀚", "🀛", "🀜", "🀝", "🀞", "🀟", "🀠", "🀡",
        "🀐", "🀑", "🀒", "🀓", "🀔", "🀕", "🀖", "🀗", "🀘", "🀀", "🀁", "🀂", "🀃", "🀆", "🀅", "🀄", "[🀋]", "[🀝]",
        "[🀔]"
    ]

    def __init__(self, _136):
        if not 0 <= _136 <= 135:
            raise ValueError(f"136编码必须在0-135之间，当前值: {_136}")
        self.id = _136
        self.name = MahjongTile.code_34[self.id // 4]
        self.is_aka_dora = True if self.id in MahjongTile.RED_BONUS else False
        self.is_dora = False
        self.area = None
        self.player = None

    def __str__(self):
        if self.is_aka_dora:
            return '赤' + MahjongTile.chinese_names[self.name]
        else:
            return MahjongTile.chinese_names[self.name]

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, MahjongTile):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

class MahjongTileSet:

    def __init__(self):
        """
        初始化麻将牌堆
        创建136张标准麻将牌
        """
        self.tiles = [MahjongTile(i) for i in range(136)]  # 所有136张牌的列表
        random.shuffle(self.tiles)

if __name__ == '__main__':
    a = MahjongTileSet()
    print(a.tiles)