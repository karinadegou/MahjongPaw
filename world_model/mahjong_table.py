# -*- coding: utf-8 -*-
from mitmproxy.addons import default_addons

from world_model.entities.mahjong_meld import Meld
from world_model.entities.mahjong_tile import MahjongTile, MahjongTileSet


class GameTable:
    # players
    bot = None
    opponents = None
    # game round info
    dealer_seat = 0
    bonus_indicator = None
    round_number = 0
    reach_sticks = 0
    honba_sticks = 0
    count_players = 4
    count_remaining_tiles = 0
    revealed_tiles = None
    # rule
    open_tanyao = False
    aka_dora = False

    def __init__(self, players):
        self.mahjong_tiles = MahjongTileSet()
        self.players = players
        self.round = 0
        self.turn = 0
        self.end = 0 # 胡牌结束 1 流局结束 2
        # 游戏区域
        self.wall = self.mahjong_tiles.tiles[:122]       # 牌山
        self.dead_wall = self.mahjong_tiles.tiles[122:]  # 岭上
        self.river = [[], [], [], []]      # 牌河（所有玩家弃牌）
        self.meld = [[], [], [], []]
        self.dora_indicators = self.dead_wall[5:10]
        self.dora_indicators_pointer = 0
        self.in_dora = self.dead_wall[0:5]
        self.cur_river = []

        self.riichi_sticks = 0

        self.winner = []

    def init_round(self):
        self.round_number = self.round_number + 1
        self.mahjong_tiles = MahjongTileSet()
        self.turn = 0
        self.end = 0 # 胡牌结束 1 流局结束 2
        self.wall = self.mahjong_tiles.tiles[:122]  # 牌山
        self.dead_wall = self.mahjong_tiles.tiles[122:]  # 岭上
        self.river = [[], [], [], []]  # 牌河（所有玩家弃牌）
        self.meld = [[], [], [], []]
        self.dora_indicators = self.dead_wall[5:10]
        self.dora_indicators_pointer = 0
        self.in_dora = self.dead_wall[0:5]
        self.cur_river.clear()
        self.riichi_sticks = 0
        # 换庄
        if not self.players[0] in self.winner:
            for p in self.players:
                p.seat = (p.seat + 1) % 4
        self.winner.clear()

    def init_turn(self):
        self.turn = self.turn + 1
        self.cur_river.clear()
