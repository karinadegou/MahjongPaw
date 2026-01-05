# -*- coding: utf-8 -*-
from copy import deepcopy

from world_model.entities.mahjong_meld import Meld
from world_model.entities.mahjong_tile import MahjongTile
from world_model.entities.mahjong_tile import MahjongTileSet
from world_model.entities.mahjong_table import GameTable


class Player:
    """
    麻将游戏玩家类，用于记录单个玩家的座位信息、游戏状态、手牌/副露/弃牌数据及积分等级等核心属性
    """
    def __init__(self, seat, dealer_seat):
        """
        初始化麻将玩家实例，绑定座位信息并初始化基础状态
        """
        # 玩家所在的游戏桌实例（后续关联游戏桌，暂初始化为None）
        self.game_table = None
        # 玩家自身的座位索引/标识
        self.seat = seat
        # 玩家昵称
        self.name = ''
        # 手牌
        self.hand = []
        # 玩家打出的弃牌列表（存储136编码的麻将牌，按打出顺序排列）
        self.river = []
        # 玩家的副露列表（存储Meld类实例，记录吃/碰/杠的副露信息）
        self.meld = []
        # 玩家当前积分（游戏过程中/结算后的分数，暂初始化为None）
        self.score = 250
        # 玩家等级（如游戏内的段位、等级标识）
        self.riichi = -1

    def __str__(self):
        return f'{self.name}-{self.score}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def call_hand(self, count=1):
        if count > len(self.game_table.wall):
            self.game_table.end = 2 # 流局结束
            return []
        drawn = self.game_table.wall[:count]
        self.game_table.wall = self.game_table.wall[count:]
        self.hand.append(drawn)

    def call_meld(self, meld):
        """
        :param meld: Meld 实例，玩家本次执行的副露操作（吃/碰/明杠/暗杠/加杠）
        :return: None，无返回值
        """
        if meld.type == Meld.CHANKAN:
            kind = meld.tiles[0] // 4
            pons = [m for m in self.meld if m.type == Meld.PON and (m.tiles[0] // 4) == kind]
            if pons:
                self.meld.remove(pons[0])
        self.meld.append(meld)

    def call_discard(self, tile):
        """
        弃牌
        """
        if tile in self.hand:
            self.hand.remove(tile)
            self.river.append(tile)
        else:
            raise ValueError(f'{tile}不在{self.name}的手牌中')

    def call_riichi(self):
        """
        宣告立直
        """
        if self.score > 10:
            self.score -= 10
            self.game_table.riichi_sticks = self.game_table.riichi_sticks + 1
            self.riichi = self.game_table.turns
        else:
            raise ValueError(f"{self.name}的点数不足，无法立直")


    @property
    def round_wind(self):
        """
        :return: 场风
        """
        return MahjongTile((self.game_table.round // 4 + MahjongTile.EAST) * 4)

    @property
    def player_wind(self):
        """
        :return: 自风
        """
        return MahjongTile((self.game_table.round // 4 + MahjongTile.EAST + self.seat) * 4)

    @property
    def bonus_honors(self):
        """
        :return: 役牌
        """
        return [MahjongTile(m * 4) for m in MahjongTile.THREES] + [self.round_wind, self.player_wind]

    @property
    def has_meld(self):
        """
        :return: 是否有副露
        """
        return len([x for x in self.meld if x.open]) > 0

    @property
    def is_dealer(self):
        """
        :return: 是否为庄家
        """
        return self.seat == 0

    def ron(self):
        pass