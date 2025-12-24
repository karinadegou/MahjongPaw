# -*- coding: utf-8 -*-
"""
人类玩家麻将游戏启动器 - 修复版本
玩家可以控制主玩家进行游戏
"""

import random
from world_model.entities.mahjong_player import MainPlayer, OpponentPlayer
from world_model.entities.mahjong_table import GameTable
from world_model.entities.mahjong_tile import Tile
from world_model.entities.mahjong_meld import Meld


class HumanPlayer(MainPlayer):
    """人类玩家类，扩展MainPlayer以支持人类交互"""

    def __init__(self):
        super().__init__()
        self.name = "玩家"
        self.level = "人类"

    def get_user_discard_choice(self):
        """获取用户打牌选择"""
        print(f"\n你的手牌: {self.str_hand_tiles()}")
        print(f"刚摸的牌: {Tile.t136_to_g(self.last_draw) if self.last_draw else '无'}")

        # 显示手牌编号
        print("\n你的手牌(编号):")
        sorted_tiles = sorted(self.tiles136)
        for i, tile136 in enumerate(sorted_tiles):
            tile34 = tile136 // 4
            print(f"  [{i + 1}] {Tile.tile_graph_dict[tile34]} ({Tile.desc[tile34]})")

        while True:
            try:
                choice = input("\n请选择要打出的牌 (输入编号1-14，或输入'h'查看手牌，'q'退出): ").strip().lower()

                if choice == 'h':
                    print(f"\n你的手牌: {self.str_hand_tiles()}")
                    continue
                elif choice == 'q':
                    return None

                idx = int(choice) - 1
                if 0 <= idx < len(sorted_tiles):
                    tile136 = sorted_tiles[idx]
                    return tile136
                else:
                    print(f"无效选择，请输入1-{len(sorted_tiles)}之间的数字")
            except ValueError:
                print("请输入有效的数字")

    def get_user_meld_choice(self, possible_melds):
        """获取用户鸣牌选择"""
        if not possible_melds:
            return None

        print("\n可以鸣牌:")
        for i, meld_info in enumerate(possible_melds):
            meld_type = meld_info.get('type', '未知')
            tiles = meld_info.get('tiles', [])
            tile_names = [Tile.desc[t // 4] for t in tiles]
            print(f"  [{i + 1}] {meld_type}: {Tile.t136_to_g(tiles)} ({', '.join(tile_names)})")

        while True:
            try:
                choice = input("\n是否鸣牌? (输入编号鸣牌，或输入'n'跳过): ").strip().lower()

                if choice == 'n':
                    return None

                idx = int(choice) - 1
                if 0 <= idx < len(possible_melds):
                    return possible_melds[idx]
                else:
                    print(f"无效选择，请输入1-{len(possible_melds)}之间的数字")
            except ValueError:
                print("请输入有效的数字")


class HumanMahjongGame:
    """人类玩家麻将游戏主控制器"""

    def __init__(self):
        self.round_number = 0
        self.honba_sticks = 0
        self.reach_sticks = 0
        self.dealer_seat = 0

        # 初始化所有牌
        self.all_tiles136 = []
        for tile34 in range(34):
            for _ in range(4):
                self.all_tiles136.append(tile34 * 4)

        # 初始化牌山
        self.wall = []
        self.reset_wall()

        # 初始化人类玩家
        self.human_player = HumanPlayer()

        # 初始化游戏桌
        self.game_table = GameTable(self.human_player, OpponentPlayer, None)

        # 玩家座位映射
        self.players = {
            0: self.human_player,
            1: self.game_table.get_player(1),
            2: self.game_table.get_player(2),
            3: self.game_table.get_player(3)
        }

        # 当前回合玩家
        self.current_player = 0

        # 游戏状态
        self.game_state = "waiting"
        self.winner = None

        # 对手名字
        self.opponent_names = ["AI东", "AI南", "AI西"]

    def reset_wall(self):
        """重置牌山"""
        self.wall = self.all_tiles136.copy()
        random.shuffle(self.wall)

    def init_round(self):
        """初始化一局游戏"""
        # 重置牌山
        self.reset_wall()

        # 宝牌指示牌
        bonus_indicators = []
        for i in range(5):
            if len(self.wall) > 0:
                bonus_indicators.append(self.wall.pop())

        # 设置玩家分数
        scores = [250, 250, 250, 250]  # 每人25000点

        # 初始化游戏桌
        self.game_table.init_round(
            round_number=self.round_number,
            honba_sticks=self.honba_sticks,
            reach_sticks=self.reach_sticks,
            bonus_tile_indicator=bonus_indicators,
            dealer_seat=self.dealer_seat,
            scores=scores
        )

        # 设置玩家个人信息
        player_info = [
            {"name": self.human_player.name, "level": self.human_player.level},
            {"name": self.opponent_names[0], "level": "AI"},
            {"name": self.opponent_names[1], "level": "AI"},
            {"name": self.opponent_names[2], "level": "AI"}
        ]
        self.game_table.set_personal_info(player_info)

        # 发牌
        for player_seat in range(4):
            player = self.players[player_seat]
            hand_tiles = []
            for _ in range(13):
                if len(self.wall) > 0:
                    hand_tiles.append(self.wall.pop())

            # 人类玩家特殊处理
            if player_seat == 0:
                player.init_hand(hand_tiles)

        # 从庄家开始游戏
        self.current_player = self.dealer_seat
        self.game_state = "playing"

        print(f"\n{'=' * 50}")
        print(f"🀄 麻将游戏开始 🀄")
        print(f"{'=' * 50}")
        print(f"局数: {self.get_round_name()}")
        print(f"庄家: 座位{self.dealer_seat} ({self.players[self.dealer_seat].name})")
        print(f"宝牌指示牌: {Tile.t136_to_g(bonus_indicators)}")
        print(f"玩家手牌: {Tile.t136_to_g(self.human_player.tiles136)}")
        print(f"剩余牌数: {len(self.wall)}张")
        print(f"{'=' * 50}")

    def get_round_name(self):
        """获取当前局数名称"""
        winds = ["东", "南", "西", "北"]
        wind_index = self.round_number // 4
        round_in_wind = (self.round_number % 4) + 1
        return f"{winds[wind_index]}{round_in_wind}局"

    def draw_tile(self, player_seat):
        """玩家摸牌"""
        if len(self.wall) <= 0:
            print("牌山已空，游戏结束")
            self.game_state = "finished"
            return None

        tile = self.wall.pop()
        player = self.players[player_seat]

        if player_seat == 0:  # 人类玩家
            player.draw_tile(tile)
            print(f"\n你摸了一张牌: {Tile.t136_to_g(tile)} ({Tile.desc[tile // 4]})")
        else:
            # 对手玩家摸牌
            print(f"\n{player.name} 摸了一张牌")

        return tile

    def get_possible_melds(self, player_seat, discarded_tile):
        """获取可能的鸣牌组合"""
        if player_seat != 0:  # 只检查人类玩家
            return []

        player = self.players[player_seat]
        possible_melds = []

        # 只实现简单的碰牌判断
        tile34 = discarded_tile // 4

        # 检查是否可以碰
        hand_tiles34 = [t // 4 for t in player.tiles136]
        if hand_tiles34.count(tile34) >= 2:
            # 找到两张相同的手牌
            same_tiles = [t for t in player.tiles136 if t // 4 == tile34][:2]
            meld_tiles = same_tiles + [discarded_tile]

            possible_melds.append({
                'type': Meld.PON,
                'tiles': meld_tiles,
                'called_tile': discarded_tile,
                'from_whom': (player_seat - 1) % 4
            })

        return possible_melds

    def process_meld(self, player_seat, meld_info):
        """处理鸣牌"""
        if not meld_info:
            return

        player = self.players[player_seat]
        meld = Meld(
            type=meld_info['type'],
            tiles=meld_info['tiles'],
            called=meld_info['called_tile'],
            from_whom=meld_info['from_whom'],
            by_whom=player_seat
        )

        player.call_meld(meld)
        print(f"{player.name} 鸣牌: {meld.type} {meld.tiles_graph}")

    def discard_tile(self, player_seat, tile136=None):
        """玩家打牌"""
        player = self.players[player_seat]

        if player_seat == 0:  # 人类玩家
            if tile136 is None:
                # 获取用户选择
                tile136 = self.human_player.get_user_discard_choice()

                if tile136 is None:
                    print("游戏结束")
                    self.game_state = "finished"
                    return None

            player.discard_tile(tile136)
            print(f"你打出了: {Tile.t136_to_g(tile136)} ({Tile.desc[tile136 // 4]})")

            # 从手牌中移除（MainPlayer的discard_tile已处理）
            self.game_table.discard_tile(player_seat, tile136)

        else:
            # 对手AI打牌
            tile136 = self.ai_discard_tile(player_seat)
            print(f"{player.name} 打出了: {Tile.t136_to_g(tile136)} ({Tile.desc[tile136 // 4]})")

            # 记录到游戏桌
            self.game_table.discard_tile(player_seat, tile136)

            # 检查人类玩家是否可以鸣牌
            if player_seat != 0:  # 对手打牌时
                possible_melds = self.get_possible_melds(0, tile136)
                if possible_melds:
                    meld_choice = self.human_player.get_user_meld_choice(possible_melds)
                    if meld_choice:
                        self.process_meld(0, meld_choice)
                        # 鸣牌后需要再打一张牌
                        self.discard_tile(0)

        return tile136

    def ai_discard_tile(self, player_seat):
        """AI对手打牌策略"""
        # 从所有牌中随机选择一张（不包括已出现的牌）
        available_tiles = [t for t in self.all_tiles136 if t not in self.get_all_revealed_tiles()]

        if available_tiles:
            return random.choice(available_tiles)
        else:
            # 如果没有可用牌，返回任意一张牌
            return random.choice(self.all_tiles136)

    def get_all_revealed_tiles(self):
        """获取所有已出现的牌"""
        revealed = []

        # 获取所有玩家的弃牌
        for seat in range(4):
            player = self.players[seat]
            revealed.extend(player.discard136)

        # 获取所有玩家的鸣牌
        for seat in range(4):
            player = self.players[seat]
            for meld in player.meld136:
                revealed.extend(meld.tiles)

        # 宝牌指示牌
        revealed.extend(self.game_table.bonus_indicator)

        return revealed

    def next_turn(self):
        """进入下一回合"""
        self.current_player = (self.current_player + 1) % 4

        # 如果牌山剩余少于一定数量，流局
        if len(self.wall) < 20:
            print("\n牌山剩余不足，流局")
            self.game_state = "finished"
            return False

        return True

    def check_win_condition(self, player_seat):
        """检查和牌条件（简化版）"""
        # 只检查人类玩家
        if player_seat != 0:
            return False

        player = self.players[player_seat]

        # 简化和牌条件：手牌+最后摸的牌能组成4组面子+1对将
        hand_tiles = player.tiles136.copy()
        if player.last_draw:
            hand_tiles.append(player.last_draw)

        # 将手牌转换为34制并排序
        hand34 = [t // 4 for t in hand_tiles]
        hand34.sort()

        # 简单检查：如果手牌数达到14张，检查是否和牌
        if len(hand_tiles) == 14:
            # 这里可以添加和牌检查逻辑
            # 暂时返回False
            return False

        return False

    def play_turn(self):
        """执行一个回合"""
        if self.game_state != "playing":
            return False

        player = self.players[self.current_player]
        print(f"\n{'=' * 30}")
        print(f"当前回合: {player.name} (座位{self.current_player})")
        print(f"剩余牌数: {len(self.wall)}张")

        # 1. 摸牌
        drawn_tile = self.draw_tile(self.current_player)
        if drawn_tile is None:
            return False

        # 2. 检查和牌条件（只检查人类玩家）
        if self.current_player == 0:
            if self.check_win_condition(self.current_player):
                self.game_state = "finished"
                self.winner = self.current_player
                print(f"🎉 {player.name} 和牌！")
                return False

        # 3. 打牌
        discarded_tile = self.discard_tile(self.current_player)
        if discarded_tile is None:
            return False

        # 4. 进入下一回合
        return self.next_turn()

    def start_game(self, num_rounds=1):
        """开始游戏"""
        for round_num in range(num_rounds):
            print(f"\n第{round_num + 1}局开始")

            # 初始化本局
            self.init_round()

            # 游戏主循环
            turn_count = 0
            while self.game_state == "playing" and turn_count < 100:
                if not self.play_turn():
                    break
                turn_count += 1

            # 本局结束
            if self.winner is not None:
                print(f"\n本局结束: {self.players[self.winner].name} 获胜！")
            else:
                print("\n本局结束: 流局")

            # 显示最终分数
            self.show_scores()

            # 重置游戏状态
            self.game_state = "waiting"
            self.winner = None

            # 如果还有下一局，更新局数
            if round_num < num_rounds - 1:
                self.round_number += 1
                self.dealer_seat = (self.dealer_seat + 1) % 4
                input("\n按Enter键开始下一局...")

        print(f"\n{'=' * 50}")
        print("游戏全部结束")
        print(f"{'=' * 50}")

    def show_scores(self):
        """显示玩家分数"""
        print("\n当前分数:")
        for seat in range(4):
            player = self.players[seat]
            print(f"  {player.name}: {player.score}点")

    def show_help(self):
        """显示游戏帮助"""
        print("\n游戏帮助:")
        print("  1. 每个回合你会摸一张牌，然后选择打出一张牌")
        print("  2. 输入1-13之间的数字选择要打出的牌")
        print("  3. 输入'h'查看当前手牌")
        print("  4. 输入'q'退出游戏")
        print("  5. 当对手打牌时，如果有鸣牌机会，系统会提示")
        print("  6. 目标: 组成4组面子(刻子或顺子) + 1对将牌")
        print("\n牌型说明:")
        print("  🀇-🀏: 1万-9万")
        print("  🀙-🀡: 1筒-9筒")
        print("  🀐-🀘: 1索-9索")
        print("  🀀🀁🀂🀃: 东南西北")
        print("  🀆🀅🀄: 白发中")


def main():
    """主函数：启动人类玩家麻将游戏"""
    print("🀄 人类玩家麻将游戏 🀄")
    print("=" * 50)

    # 显示游戏帮助
    game = HumanMahjongGame()
    game.show_help()

    # 开始游戏
    input("\n按Enter键开始游戏...")
    game.start_game(num_rounds=1)


if __name__ == "__main__":
    main()