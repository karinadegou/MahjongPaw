# -*- coding: utf-8 -*-
from world_model.entities.mahjong_tile import Tile

class Meld:
    """
    吃、碰、杠、加杠、拔北（四人麻将中没有拔北）
    """
    CHI = 'chi'
    PON = 'pon'
    KAN = 'kan'
    CHANKAN = 'chankan'
    # NUKI = 'nuki'

    def __init__(self, type=None, tiles=None, open=True, called=None, from_whom=None, by_whom=None):
        """
        初始化麻将副露实例，绑定副露的各项核心属性
        :param type: str/None，可选，副露类型标识
        :param tiles: list/None，可选，副露涉及的完整牌组
        :param open: bool，可选，默认True，副露是否公开（明暗标识）
        :param called: int/None，可选，触发副露的被叫牌（仅明副露有效）
        :param from_whom: int/str/None，可选，被叫牌的来源玩家标识
        :param by_whom: int/str/None，可选，执行副露操作的玩家标识
        """
        self.type = type
        self.tiles = tiles
        self.open = open
        self.called_tile = called
        self.from_whom = from_whom
        self.by_whom = by_whom

    def __str__(self):
        return f'{self.type}, {self.tiles}'

    def __repr__(self):
        return self.__str__()
