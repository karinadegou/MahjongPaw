# -*- coding: utf-8 -*-
"""
麻将游戏启动模块
"""
import sys
import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

# 导入现有的模块
from world_model.entities.mahjong_tile import MahjongTile, MahjongTileSet, Tile
from world_model.entities.mahjong_meld import Meld
from world_model.entities.mahjong_player import Player
from world_model.entities.mahjong_table import GameTable


class GamePhase(Enum):
    """游戏阶段"""
    PREPARE = "prepare"  # 准备阶段
    DRAW = "draw"  # 摸牌阶段
    DISCARD = "discard"  # 打牌阶段
    ACTION = "action"  # 行动阶段（碰杠吃）
    RIICHI = "riichi"  # 立直阶段
    WIN = "win"  # 和牌阶段
    END = "end"  # 结束阶段


class ActionType(Enum):
    """玩家动作类型"""
    DRAW = "draw"  # 摸牌
    DISCARD = "discard"  # 打牌
    PON = "pon"  # 碰
    CHI = "chi"  # 吃
    KAN = "kan"  # 杠
    RIICHI = "riichi"  # 立直
    TSUMO = "tsumo"  # 自摸
    RON = "ron"  # 荣和
    PASS = "pass"  # 过
    SKIP = "skip"  # 跳过


class GameController:
    """
    游戏控制器
    负责管理游戏流程和玩家交互
    """

    def __init__(self, player_names: List[str] = None):
        """
        初始化游戏控制器

        参数:
        ----------
        player_names : List[str], 可选
            玩家名称列表，默认为["玩家", "AI东", "AI南", "AI西"]
        """
        if player_names is None:
            player_names = ["玩家", "AI东", "AI南", "AI西"]

        if len(player_names) != 4:
            raise ValueError("麻将游戏需要4名玩家")

        # 初始化玩家
        self.players = []
        for i, name in enumerate(player_names):
            player = Player(seat=i, dealer_seat=0)
            player.name = name
            self.players.append(player)

        # 创建游戏桌
        self.game_table = GameTable(self.players)

        # 设置玩家与游戏桌的关联
        for player in self.players:
            player.game_table = self.game_table

        # 游戏状态
        self.current_phase = GamePhase.PREPARE
        self.current_player = 0  # 当前行动玩家
        self.last_action = None  # 上一个动作
        self.pending_actions = {}  # 待处理的玩家动作
        self.game_over = False

        # AI玩家标记
        self.ai_players = [i for i, player in enumerate(self.players) if "AI" in player.name]

        print("=" * 60)
        print("麻将游戏初始化完成")
        print(f"玩家列表: {[p.name for p in self.players]}")
        print(f"庄家: {self.players[self.game_table.dealer_seat].name}")
        print("=" * 60)

    def start_game(self):
        """开始游戏"""
        print("\n🎮 开始新游戏 🎮")

        # 初始化回合
        self.game_table.init_round()

        # 发手牌
        self._deal_hands()

        # 设置游戏阶段
        self.current_phase = GamePhase.DRAW
        self.current_player = self.game_table.dealer_seat

        # 显示初始状态
        self._display_game_state()

        # 开始游戏主循环
        self._game_loop()

    def _deal_hands(self):
        """发手牌"""
        print("\n🃏 发手牌 🃏")

        # 标准麻将发牌流程：每人13张，庄家14张
        # 每次发4张，发3轮，共12张
        for _ in range(3):
            for player in self.players:
                # 每人摸4张
                for _ in range(4):
                    if self.game_table.wall:
                        tile = self.game_table.wall.pop(0)
                        player.hand.append(tile)

        # 第4轮：庄家摸2张，其他玩家摸1张
        for i, player in enumerate(self.players):
            draw_count = 2 if i == self.game_table.dealer_seat else 1
            for _ in range(draw_count):
                if self.game_table.wall:
                    tile = self.game_table.wall.pop(0)
                    player.hand.append(tile)

        # 整理手牌
        for player in self.players:
            self._sort_hand(player)

        print("手牌发放完成")

    def _sort_hand(self, player: Player):
        """整理玩家手牌"""
        # 按136编码排序，这样同种牌会在一起
        player.hand.sort(key=lambda tile: tile.id)

    def _game_loop(self):
        """游戏主循环"""
        while not self.game_over and self.game_table.end == 0:
            # 处理当前玩家的回合
            self._process_player_turn()

            # 检查游戏结束条件
            if self.game_table.end != 0:
                self.game_over = True
                break

            # 切换到下一个玩家
            self._next_player()

        # 游戏结束
        self._end_game()

    def _process_player_turn(self):
        """处理玩家回合"""
        player = self.players[self.current_player]

        print(f"\n{'=' * 50}")
        print(f"回合 {self.game_table.turn}: {player.name} 的回合")
        print(f"{'=' * 50}")

        # 1. 摸牌阶段
        if self.current_phase == GamePhase.DRAW:
            self._draw_phase(player)

        # 2. 打牌阶段
        elif self.current_phase == GamePhase.DISCARD:
            self._discard_phase(player)

        # 3. 检查其他玩家是否可以行动（碰杠吃）
        if self.last_action == ActionType.DISCARD:
            self._check_player_actions(player)

        # 4. 更新回合计数
        self.game_table.init_turn()

    def _draw_phase(self, player: Player):
        """摸牌阶段"""
        if not self.game_table.wall:
            print("牌山已空，游戏结束")
            self.game_table.end = 2  # 流局结束
            return

        # 摸一张牌
        tile = self.game_table.wall.pop(0)
        player.hand.append(tile)
        self._sort_hand(player)

        print(f"{player.name} 摸牌: {tile}")

        # 记录动作
        self.last_action = ActionType.DRAW

        # 切换到打牌阶段
        self.current_phase = GamePhase.DISCARD

    def _discard_phase(self, player: Player):
        """打牌阶段"""
        # 获取玩家要打出的牌
        discard_tile = self._get_discard_tile(player)

        if discard_tile:
            # 从手牌中移除
            player.hand.remove(discard_tile)

            # 添加到牌河
            player.river.append(discard_tile)
            self.game_table.river[player.seat].append(discard_tile)

            # 记录当前牌河（用于其他玩家行动判断）
            self.game_table.cur_river.append({
                'tile': discard_tile,
                'player': player.seat,
                'turn': self.game_table.turn
            })

            print(f"{player.name} 打牌: {discard_tile}")

            # 记录动作
            self.last_action = ActionType.DISCARD
            self.last_discard = discard_tile
            self.last_discard_player = player.seat

            # 重置阶段
            self.current_phase = GamePhase.DRAW
        else:
            print(f"{player.name} 无法打牌，手牌为空")

    def _get_discard_tile(self, player: Player) -> Optional[MahjongTile]:
        """获取玩家要打出的牌（AI或人类）"""
        if not player.hand:
            return None

        # AI玩家：使用简单策略
        if player.seat in self.ai_players:
            return self._ai_choose_discard(player)

        # 人类玩家：模拟选择（实际中应该通过UI选择）
        else:
            return self._human_choose_discard(player)

    def _ai_choose_discard(self, player: Player) -> MahjongTile:
        """AI选择打出的牌（简单策略）"""
        # 简单策略：优先打出孤立的字牌，然后打出边张
        hand = player.hand

        # 检查是否有字牌
        honor_tiles = [tile for tile in hand if tile.id // 4 >= 27]
        if honor_tiles:
            # 选择第一张字牌
            return honor_tiles[0]

        # 没有字牌，选择数字牌
        # 优先打出边张（1或9）
        terminal_tiles = []
        for tile in hand:
            tile_34 = tile.id // 4
            if tile_34 < 27:  # 数字牌
                number = (tile_34 % 9) + 1
                if number in [1, 9]:
                    terminal_tiles.append(tile)

        if terminal_tiles:
            return terminal_tiles[0]

        # 否则随机选择一张
        return random.choice(hand)

    def _human_choose_discard(self, player: Player) -> MahjongTile:
        """人类玩家选择打出的牌（模拟）"""
        # 显示手牌
        print(f"\n你的手牌 ({len(player.hand)}张):")
        for i, tile in enumerate(player.hand):
            print(f"  [{i}] {tile}")

        # 模拟选择：随机选择一张
        # 在实际游戏中，这里应该等待玩家输入
        if player.hand:
            # 简单策略：选择第一张非字牌，如果没有则选择第一张
            non_honor_tiles = [t for t in player.hand if t.id // 4 < 27]
            if non_honor_tiles:
                return non_honor_tiles[0]
            else:
                return player.hand[0]

        return None

    def _check_player_actions(self, discard_player: Player):
        """检查其他玩家是否可以行动（碰杠吃）"""
        discard_tile = self.last_discard
        from_seat = self.last_discard_player

        print(f"\n检查其他玩家对 {discard_tile} 的行动:")

        # 收集可能的动作
        possible_actions = {}

        for player in self.players:
            if player.seat == from_seat:
                continue

            # 检查是否可以碰
            if self._can_pon(player, discard_tile):
                possible_actions[player.seat] = {
                    'type': ActionType.PON,
                    'player': player,
                    'tile': discard_tile
                }

            # 检查是否可以杠（大明杠）
            if self._can_kan(player, discard_tile):
                possible_actions[player.seat] = {
                    'type': ActionType.KAN,
                    'player': player,
                    'tile': discard_tile
                }

            # 检查是否可以吃（只有下家可以）
            if self._can_chi(player, discard_tile, from_seat):
                possible_actions[player.seat] = {
                    'type': ActionType.CHI,
                    'player': player,
                    'tile': discard_tile
                }

        # 如果有动作，处理之
        if possible_actions:
            self._resolve_actions(possible_actions)

    def _can_pon(self, player: Player, tile: MahjongTile) -> bool:
        """检查是否可以碰"""
        # 检查手牌中是否有2张相同的牌
        same_tiles = [t for t in player.hand if t.id // 4 == tile.id // 4]
        return len(same_tiles) >= 2

    def _can_kan(self, player: Player, tile: MahjongTile) -> bool:
        """检查是否可以杠（大明杠）"""
        # 检查手牌中是否有3张相同的牌
        same_tiles = [t for t in player.hand if t.id // 4 == tile.id // 4]
        return len(same_tiles) >= 3

    def _can_chi(self, player: Player, tile: MahjongTile, from_seat: int) -> bool:
        """检查是否可以吃"""
        # 只有下家可以吃
        if (player.seat - from_seat) % 4 != 1:
            return False

        # 字牌不能吃
        if tile.id // 4 >= 27:
            return False

        # 这里简化处理，实际应该检查是否可以组成顺子
        return True

    def _resolve_actions(self, actions: Dict):
        """解析并执行动作"""
        # 按优先级排序：杠 > 碰 > 吃
        action_list = list(actions.values())

        # 简单选择：选择第一个动作
        if action_list:
            action = action_list[0]
            player = action['player']
            tile = action['tile']

            print(f"{player.name} {action['type'].value} {tile}!")

            # 执行动作
            if action['type'] == ActionType.PON:
                self._execute_pon(player, tile, self.last_discard_player)
            elif action['type'] == ActionType.KAN:
                self._execute_kan(player, tile, self.last_discard_player)
            elif action['type'] == ActionType.CHI:
                self._execute_chi(player, tile, self.last_discard_player)

    def _execute_pon(self, player: Player, tile: MahjongTile, from_seat: int):
        """执行碰牌"""
        # 从手牌中找出两张相同的牌
        same_tiles = [t for t in player.hand if t.id // 4 == tile.id // 4][:2]

        # 创建副露
        meld_tiles = same_tiles + [tile]
        meld = Meld(
            type=Meld.PON,
            tiles=meld_tiles,
            open=True,
            called=tile.id,
            from_whom=from_seat,
            by_whom=player.seat
        )

        # 添加到玩家副露
        player.meld.append(meld)
        self.game_table.meld[player.seat].append(meld)

        # 从手牌中移除两张牌
        for t in same_tiles:
            player.hand.remove(t)

        # 碰牌后，该玩家成为当前玩家
        self.current_player = player.seat
        self.current_phase = GamePhase.DISCARD

        print(f"{player.name} 碰了 {tile}!")

    def _execute_kan(self, player: Player, tile: MahjongTile, from_seat: int):
        """执行杠牌（大明杠）"""
        # 从手牌中找出三张相同的牌
        same_tiles = [t for t in player.hand if t.id // 4 == tile.id // 4][:3]

        # 创建副露
        meld_tiles = same_tiles + [tile]
        meld = Meld(
            type=Meld.KAN,
            tiles=meld_tiles,
            open=True,
            called=tile.id,
            from_whom=from_seat,
            by_whom=player.seat
        )

        # 添加到玩家副露
        player.meld.append(meld)
        self.game_table.meld[player.seat].append(meld)

        # 从手牌中移除三张牌
        for t in same_tiles:
            player.hand.remove(t)

        # 杠牌后，从岭上摸一张牌
        if self.game_table.dead_wall:
            bonus_tile = self.game_table.dead_wall.pop(0)
            player.hand.append(bonus_tile)
            self._sort_hand(player)
            print(f"{player.name} 从岭上摸牌: {bonus_tile}")

        # 杠牌后，该玩家成为当前玩家
        self.current_player = player.seat
        self.current_phase = GamePhase.DISCARD

        print(f"{player.name} 杠了 {tile}!")

    def _execute_chi(self, player: Player, tile: MahjongTile, from_seat: int):
        """执行吃牌"""
        # 简化处理：假设可以吃
        print(f"{player.name} 吃 {tile} (简化处理)")

        # 吃牌后，该玩家成为当前玩家
        self.current_player = player.seat
        self.current_phase = GamePhase.DISCARD

    def _next_player(self):
        """切换到下一个玩家"""
        self.current_player = (self.current_player + 1) % 4

    def _display_game_state(self):
        """显示游戏状态"""
        print("\n" + "=" * 60)
        print("当前游戏状态:")
        print("=" * 60)

        # 显示牌山信息
        print(f"牌山剩余: {len(self.game_table.wall)}张")
        print(f"岭上剩余: {len(self.game_table.dead_wall)}张")
        print(f"宝牌指示牌: {[Tile.t136_to_g(t.id) for t in self.game_table.dora_indicators]}")

        # 显示立直棒
        print(f"立直棒: {self.game_table.riichi_sticks}本")

        # 显示玩家状态
        print("\n玩家状态:")
        for player in self.players:
            hand_display = Tile.t136_to_g([t.id for t in player.hand]) if player.hand else "空"
            discard_display = Tile.t136_to_g([t.id for t in player.river[-5:]]) if player.river else "空"

            status = []
            if player.seat == self.current_player:
                status.append("当前回合")
            if player.seat == self.game_table.dealer_seat:
                status.append("庄家")
            if player.riichi >= 0:
                status.append("立直")

            status_str = "(" + ", ".join(status) + ")" if status else ""

            print(f"  {player.name}: 手牌{len(player.hand)}张 {hand_display}")
            print(f"        牌河{len(player.river)}张 {discard_display} {status_str}")

        print("=" * 60)

    def _end_game(self):
        """结束游戏"""
        print("\n" + "=" * 60)
        print("游戏结束!")
        print("=" * 60)

        if self.game_table.end == 1:
            print("和牌结束!")
            if self.game_table.winner:
                winners = [self.players[i].name for i in self.game_table.winner]
                print(f"和牌者: {', '.join(winners)}")
        elif self.game_table.end == 2:
            print("流局结束!")

        # 显示最终得分
        print("\n最终得分:")
        for player in self.players:
            print(f"  {player.name}: {player.score}点")

        print("\n感谢游戏！")


class SimpleGameUI:
    """
    简单的游戏UI（命令行界面）
    """

    @staticmethod
    def show_main_menu():
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("          日本麻将游戏")
        print("=" * 60)
        print("1. 开始新游戏")
        print("2. 游戏规则")
        print("3. 退出游戏")
        print("=" * 60)

        choice = input("请选择 (1-3): ")
        return choice

    @staticmethod
    def show_game_rules():
        """显示游戏规则"""
        print("\n" + "=" * 60)
        print("游戏规则说明:")
        print("=" * 60)
        print("1. 游戏人数: 4人")
        print("2. 牌种: 136张标准麻将牌")
        print("3. 目标: 通过吃、碰、杠组成特定的牌型")
        print("4. 特殊规则:")
        print("   - 立直: 宣布听牌，之后不能换牌")
        print("   - 宝牌: 增加番数")
        print("   - 流局: 牌山摸完无人和牌")
        print("=" * 60)
        input("按回车键返回主菜单...")


def main():
    """主函数"""
    print("正在启动麻将游戏...")

    # 创建UI
    ui = SimpleGameUI()

    while True:
        choice = ui.show_main_menu()

        if choice == "1":
            # 开始新游戏
            player_names = ["玩家", "AI东", "AI南", "AI西"]

            # 创建游戏控制器
            game = GameController(player_names)

            # 开始游戏
            game.start_game()

            # 询问是否再来一局
            again = input("\n是否再来一局? (y/n): ")
            if again.lower() != 'y':
                print("返回主菜单...")

        elif choice == "2":
            # 显示游戏规则
            ui.show_game_rules()

        elif choice == "3":
            # 退出游戏
            print("\n感谢游戏，再见!")
            sys.exit(0)

        else:
            print("无效选择，请重新输入!")

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter

if __name__ == "__main__":
    # 初始化计算器
    calculator = HandCalculator()

    # 计算手牌
    tiles = TilesConverter.string_to_136_array(man='123', pin='456', sou='789', honors='11122')
    win_tile = TilesConverter.string_to_136_array(honors='2')[0]

    result = calculator.estimate_hand_value(tiles, win_tile)
    print(result)
    exit()
    main()