# mahjong_config_renderer_fixed.py - 修复编码问题的麻将配置渲染器

# -*- coding: utf-8 -*-
"""
麻将配置渲染器 - 修复Windows编码问题
将配置文件渲染成麻将桌的图形化展示
"""

import json
import os
import sys
from datetime import datetime
from world_model.entities.mahjong_tile import Tile
from world_model.entities.mahjong_meld import Meld


class MahjongTableRenderer:
    """麻将桌渲染器 - 修复编码问题"""

    def __init__(self, config=None, config_file=None):
        """初始化渲染器"""
        self.config = config
        self.config_file = config_file

        # 麻将桌尺寸
        self.table_width = 80

        # 玩家位置映射
        self.player_positions = {
            0: "南",  # 玩家自己 (底部)
            1: "东",  # 右侧
            2: "北",  # 顶部
            3: "西"  # 左侧
        }

        # 玩家颜色（Windows CMD可能不支持，提供选项）
        self.use_colors = self.check_color_support()

        if self.use_colors:
            self.player_colors = {
                0: "\033[92m",  # 绿色 - 玩家自己
                1: "\033[93m",  # 黄色 - 东
                2: "\033[94m",  # 蓝色 - 北
                3: "\033[95m",  # 紫色 - 西
            }
            self.reset_color = "\033[0m"
        else:
            # 不使用颜色
            self.player_colors = {i: "" for i in range(4)}
            self.reset_color = ""

    def check_color_support(self):
        """检查终端是否支持颜色"""
        # Windows CMD通常不支持ANSI颜色，但Windows Terminal支持
        if sys.platform == "win32":
            # 检查是否在Windows Terminal或支持ANSI的终端中
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 尝试启用虚拟终端处理
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        else:
            # Linux/macOS通常支持
            return True

    def set_config(self, config):
        """设置配置"""
        self.config = config

    def load_config_from_file(self, filename):
        """从文件加载配置"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.config_file = filename
            print(f"✓ 配置已从文件加载: {filename}")
            return True
        except Exception as e:
            print(f"✗ 加载配置失败: {e}")
            return False

    def get_round_name(self, round_num):
        """获取局数名称"""
        winds = ["东", "南", "西", "北"]
        wind_index = round_num // 4
        round_in_wind = (round_num % 4) + 1
        return f"{winds[wind_index]}{round_in_wind}局"

    def calculate_text_width(self, text):
        """计算文本在终端中的显示宽度（考虑中文字符和麻将牌字符）"""
        width = 0
        for char in text:
            # 麻将牌字符（Unicode麻将符号）通常算作2个字符宽度
            if '\U0001f000' <= char <= '\U0001f02b':
                width += 2
            # 中文字符
            elif '\u4e00' <= char <= '\u9fff':
                width += 2
            # 其他字符（英文、数字、符号）
            else:
                width += 1
        return width

    def render_table_top(self):
        """渲染牌桌顶部"""
        lines = []

        # 顶部边界
        lines.append("╔" + "═" * (self.table_width - 2) + "╗")

        # 游戏信息行
        if self.config:
            round_num = self.config.get("round", 0)
            dealer_seat = self.config.get("dealer", 0)
            honba = self.config.get("honba", 0)
            reach_sticks = self.config.get("reach_sticks", 0)

            round_name = self.get_round_name(round_num)
            dealer_name = self.config.get("players", [{} for _ in range(4)])[dealer_seat].get("name", "Unknown")

            info_line = f" {round_name} | 庄家: {dealer_name} | 本场: {honba} | 立直棒: {reach_sticks}"

            # 宝牌指示牌
            bonus = self.config.get("bonus", [])
            if bonus:
                try:
                    bonus_str = Tile.t34_to_g(bonus)
                    info_line += f" | 宝牌指示牌: {bonus_str}"
                except:
                    info_line += f" | 宝牌指示牌: {bonus}"

            # 居中显示
            text_width = self.calculate_text_width(info_line)
            padding = max(0, self.table_width - text_width - 4)
            left_pad = padding // 2
            right_pad = padding - left_pad

            lines.append("║" + " " * left_pad + info_line + " " * right_pad + "║")
        else:
            lines.append("║" + " " * (self.table_width - 2) + "║")

        # 分隔线
        lines.append("╠" + "═" * (self.table_width - 2) + "╣")

        return "\n".join(lines)

    def render_table_bottom(self):
        """渲染牌桌底部"""
        return "╚" + "═" * (self.table_width - 2) + "╝"

    def render_player_north(self, player_idx):
        """渲染北家（座位2）"""
        if not self.config or player_idx >= len(self.config.get("players", [])):
            return " " * self.table_width

        players = self.config.get("players", [])
        player = players[player_idx]

        # 玩家信息
        player_name = player.get("name", f"玩家{player_idx}")
        player_score = player.get("score", 0)
        player_reach = player.get("reach", False)

        # 手牌（北家不显示手牌）
        hand_tiles = []
        hand_str = "🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫"  # 13张背面牌

        # 牌河
        discards = player.get("discards", [])
        try:
            discards_str = Tile.t34_to_g(discards) if discards else "无"
        except:
            discards_str = str(discards) if discards else "无"

        # 副露
        melds = player.get("melds", [])
        melds_str = ""
        if melds:
            meld_parts = []
            for meld in melds:
                tiles = meld.get("tiles", [])
                meld_type = meld.get("type", "unknown")
                try:
                    tile_str = Tile.t34_to_g(tiles)
                except:
                    tile_str = str(tiles)
                meld_parts.append(f"{meld_type} {tile_str}")
            melds_str = " ".join(meld_parts)

        # 构建北家显示行
        color = self.player_colors.get(player_idx, "")

        # 第一行：玩家信息
        info_line = f"{color}北 [{player_name}] 分数:{player_score}"
        if player_reach:
            info_line += " [立直]"
        info_line += self.reset_color

        # 第二行：牌河
        discards_line = f"  牌河: {discards_str}"

        # 第三行：副露
        melds_line = f"  副露: {melds_str}" if melds_str else "  副露: 无"

        # 第四行：手牌（背面）
        hand_line = f"  手牌: {hand_str}"

        # 组合所有行
        lines = [
            self.center_text(info_line),
            self.center_text(discards_line),
            self.center_text(melds_line),
            self.center_text(hand_line)
        ]

        return "\n".join(lines)

    def render_player_south(self, player_idx):
        """渲染南家（座位0）- 玩家自己"""
        if not self.config or player_idx >= len(self.config.get("players", [])):
            return " " * self.table_width

        players = self.config.get("players", [])
        player = players[player_idx]

        # 玩家信息
        player_name = player.get("name", f"玩家{player_idx}")
        player_score = player.get("score", 0)
        player_reach = player.get("reach", False)

        # 手牌
        hand = player.get("hand", [])
        try:
            hand_str = Tile.t34_to_g(hand) if hand else "🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫"
        except:
            hand_str = str(hand) if hand else "🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫🀫"

        # 牌河
        discards = player.get("discards", [])
        try:
            discards_str = Tile.t34_to_g(discards) if discards else "无"
        except:
            discards_str = str(discards) if discards else "无"

        # 副露
        melds = player.get("melds", [])
        melds_str = ""
        if melds:
            meld_parts = []
            for meld in melds:
                tiles = meld.get("tiles", [])
                meld_type = meld.get("type", "unknown")
                try:
                    tile_str = Tile.t34_to_g(tiles)
                except:
                    tile_str = str(tiles)
                meld_parts.append(f"{meld_type} {tile_str}")
            melds_str = " ".join(meld_parts)

        # 构建南家显示行
        color = self.player_colors.get(player_idx, "")

        # 第一行：玩家信息
        info_line = f"{color}南 [{player_name}] 分数:{player_score}"
        if player_reach:
            info_line += " [立直]"
        info_line += self.reset_color

        # 第二行：手牌
        hand_line = f"  手牌: {hand_str}"

        # 第三行：牌河
        discards_line = f"  牌河: {discards_str}"

        # 第四行：副露
        melds_line = f"  副露: {melds_str}" if melds_str else "  副露: 无"

        # 组合所有行
        lines = [
            self.center_text(info_line),
            self.center_text(hand_line),
            self.center_text(discards_line),
            self.center_text(melds_line)
        ]

        return "\n".join(lines)

    def render_player_east(self, player_idx):
        """渲染东家（座位1）"""
        if not self.config or player_idx >= len(self.config.get("players", [])):
            return ""

        players = self.config.get("players", [])
        player = players[player_idx]

        # 玩家信息
        player_name = player.get("name", f"玩家{player_idx}")
        player_score = player.get("score", 0)
        player_reach = player.get("reach", False)

        # 手牌（东家不显示手牌）
        hand_str = "🀫" * 13  # 13张背面牌

        # 牌河
        discards = player.get("discards", [])
        try:
            discards_str = Tile.t34_to_g(discards) if discards else "无"
        except:
            discards_str = str(discards) if discards else "无"

        # 副露
        melds = player.get("melds", [])
        melds_str = ""
        if melds:
            meld_parts = []
            for meld in melds:
                tiles = meld.get("tiles", [])
                meld_type = meld.get("type", "unknown")
                try:
                    tile_str = Tile.t34_to_g(tiles)
                except:
                    tile_str = str(tiles)
                meld_parts.append(f"{meld_type} {tile_str}")
            melds_str = " ".join(meld_parts)

        # 构建东家显示行（右侧）
        color = self.player_colors.get(player_idx, "")

        # 信息行
        info_line = f"{color}东 [{player_name}] 分数:{player_score}"
        if player_reach:
            info_line += " [立直]"
        info_line += self.reset_color

        # 创建东家的垂直显示
        lines = []

        # 第一行：玩家信息
        lines.append(info_line)

        # 第二行：牌河
        lines.append(f"牌河: {discards_str}")

        # 第三行：副露
        if melds_str:
            lines.append(f"副露: {melds_str}")
        else:
            lines.append("副露: 无")

        # 第四行：手牌（背面）
        lines.append(f"手牌: {hand_str}")

        # 垂直显示，每行右对齐
        max_len = max(self.calculate_text_width(line) for line in lines)
        right_aligned_lines = []
        for line in lines:
            padding = max_len - self.calculate_text_width(line)
            right_aligned_lines.append(" " * padding + line)

        return "\n".join(right_aligned_lines)

    def render_player_west(self, player_idx):
        """渲染西家（座位3）"""
        if not self.config or player_idx >= len(self.config.get("players", [])):
            return ""

        players = self.config.get("players", [])
        player = players[player_idx]

        # 玩家信息
        player_name = player.get("name", f"玩家{player_idx}")
        player_score = player.get("score", 0)
        player_reach = player.get("reach", False)

        # 手牌（西家不显示手牌）
        hand_str = "🀫" * 13  # 13张背面牌

        # 牌河
        discards = player.get("discards", [])
        try:
            discards_str = Tile.t34_to_g(discards) if discards else "无"
        except:
            discards_str = str(discards) if discards else "无"

        # 副露
        melds = player.get("melds", [])
        melds_str = ""
        if melds:
            meld_parts = []
            for meld in melds:
                tiles = meld.get("tiles", [])
                meld_type = meld.get("type", "unknown")
                try:
                    tile_str = Tile.t34_to_g(tiles)
                except:
                    tile_str = str(tiles)
                meld_parts.append(f"{meld_type} {tile_str}")
            melds_str = " ".join(meld_parts)

        # 构建西家显示行（左侧）
        color = self.player_colors.get(player_idx, "")

        # 信息行
        info_line = f"{color}西 [{player_name}] 分数:{player_score}"
        if player_reach:
            info_line += " [立直]"
        info_line += self.reset_color

        # 创建西家的垂直显示
        lines = []

        # 第一行：玩家信息
        lines.append(info_line)

        # 第二行：牌河
        lines.append(f"牌河: {discards_str}")

        # 第三行：副露
        if melds_str:
            lines.append(f"副露: {melds_str}")
        else:
            lines.append("副露: 无")

        # 第四行：手牌（背面）
        lines.append(f"手牌: {hand_str}")

        return "\n".join(lines)

    def center_text(self, text):
        """居中文本"""
        text_width = self.calculate_text_width(text)
        padding = max(0, self.table_width - text_width - 4)  # 减去边框和空格
        left_pad = padding // 2
        right_pad = padding - left_pad
        return "║" + " " * left_pad + text + " " * right_pad + "║"

    def render_wall_info(self):
        """渲染牌山信息"""
        if not self.config:
            return self.center_text("")

        wall_remaining = self.config.get("wall", 70)
        current_player = self.config.get("current", 0)
        players = self.config.get("players", [])
        current_name = players[current_player].get("name", f"玩家{current_player}") if current_player < len(
            players) else "Unknown"

        wall_line = f"牌山剩余: {wall_remaining}张 | 当前回合: {current_name}"
        return self.center_text(wall_line)

    def render_table_middle(self, west_lines, east_lines):
        """渲染牌桌中间部分（包含西家和东家）"""
        lines = []

        # 计算每侧的最大宽度
        west_width = 0
        if west_lines:
            for line in west_lines.split('\n'):
                west_width = max(west_width, self.calculate_text_width(line))

        east_width = 0
        if east_lines:
            for line in east_lines.split('\n'):
                east_width = max(east_width, self.calculate_text_width(line))

        # 中间区域的宽度
        middle_width = self.table_width - west_width - east_width - 4  # 4个边框字符

        # 确保中间区域有最小宽度
        if middle_width < 20:
            middle_width = 20

        # 分割西家、中间、东家
        west_lines_list = west_lines.split('\n') if west_lines else [""]
        east_lines_list = east_lines.split('\n') if east_lines else [""]

        # 确保行数一致
        max_lines = max(len(west_lines_list), len(east_lines_list))
        while len(west_lines_list) < max_lines:
            west_lines_list.append(" " * west_width)
        while len(east_lines_list) < max_lines:
            east_lines_list.append(" " * east_width)

        # 构建中间行
        for i in range(max_lines):
            # 西侧行（左对齐）
            west_line = west_lines_list[i]
            west_padding = west_width - self.calculate_text_width(west_line)
            west_display = west_line + " " * west_padding

            # 东侧行（右对齐）
            east_line = east_lines_list[i]
            east_padding = east_width - self.calculate_text_width(east_line)
            east_display = " " * east_padding + east_line

            # 中间区域可以显示一些信息
            middle_line = ""
            if i == 0:
                middle_line = "🀄 麻将桌 🀄"
            elif i == 1:
                middle_line = "═" * (middle_width // 2) + "╬" + "═" * (middle_width // 2)
            elif i == 2:
                # 显示宝牌信息
                if self.config and "bonus" in self.config and self.config["bonus"]:
                    bonus = self.config["bonus"]
                    try:
                        bonus_str = Tile.t34_to_g(bonus)
                        middle_line = f"宝牌指示牌: {bonus_str}"
                    except:
                        middle_line = f"宝牌指示牌: {bonus}"
                else:
                    middle_line = " "

            # 居中中间文本
            middle_display = middle_line.center(middle_width)

            lines.append(f"║{west_display}{middle_display}{east_display}║")

        return "\n".join(lines)

    def render(self):
        """渲染整个麻将桌"""
        if not self.config:
            return "无配置数据"

        # 渲染各部分
        table_top = self.render_table_top()

        # 渲染北家（顶部）
        north_player = self.render_player_north(2)  # 座位2是北家

        # 渲染西家和东家（两侧）
        west_player = self.render_player_west(3)  # 座位3是西家
        east_player = self.render_player_east(1)  # 座位1是东家

        # 渲染中间部分
        table_middle = self.render_table_middle(west_player, east_player)

        # 渲染牌山信息
        wall_info = self.render_wall_info()

        # 渲染南家（玩家自己）
        south_player = self.render_player_south(0)  # 座位0是南家

        # 渲染底部
        table_bottom = self.render_table_bottom()

        # 组合所有部分
        result = [
            table_top,
            north_player,
            table_middle,
            wall_info,
            south_player,
            table_bottom
        ]

        return "\n".join(result)

    def render_text_only_view(self):
        """渲染纯文本视图（不使用麻将符号）"""
        if not self.config:
            return "无配置数据"

        lines = []

        # 游戏信息
        round_num = self.config.get("round", 0)
        dealer_seat = self.config.get("dealer", 0)
        round_name = self.get_round_name(round_num)

        lines.append("=" * 60)
        lines.append(f"麻将配置视图 (纯文本模式)")
        lines.append("=" * 60)
        lines.append(f"局数: {round_name} | 庄家: 座位{dealer_seat}")

        # 宝牌信息
        bonus = self.config.get("bonus", [])
        if bonus:
            lines.append(f"宝牌指示牌: {bonus}")
            # 计算宝牌
            dora_list = []
            for b in bonus:
                dora = Tile.bonus_dict.get(b, b + 1)
                dora_list.append(dora)
            lines.append(f"宝牌: {dora_list}")

        lines.append("-" * 60)

        # 玩家信息
        players = self.config.get("players", [])
        for seat in range(4):
            player = players[seat] if seat < len(players) else {}
            player_name = player.get("name", f"玩家{seat}")
            player_score = player.get("score", 0)
            player_reach = player.get("reach", False)

            direction = self.player_positions.get(seat, "?")

            # 手牌
            hand = player.get("hand", [])
            hand_desc = []
            for tile in hand:
                if 0 <= tile <= 33:
                    hand_desc.append(Tile.desc[tile])

            # 牌河
            discards = player.get("discards", [])
            discards_desc = [Tile.desc[t] for t in discards if 0 <= t <= 33]

            # 副露
            melds = player.get("melds", [])

            # 构建玩家行
            reach_mark = " [立直]" if player_reach else ""
            lines.append(f"{direction} {player_name} ({player_score}){reach_mark}")

            if seat == 0 and hand_desc:  # 玩家自己显示手牌
                lines.append(f"  手牌: {', '.join(hand_desc)}")
            elif seat != 0:
                lines.append(f"  手牌: {'未知' if hand else '未设置'}")

            if discards_desc:
                lines.append(f"  牌河: {', '.join(discards_desc)}")
            else:
                lines.append(f"  牌河: 无")

            lines.append(f"  副露: {len(melds)}组")

            # 显示副露详情
            for i, meld in enumerate(melds):
                tiles = meld.get("tiles", [])
                meld_type = meld.get("type", "unknown")
                tile_names = [Tile.desc[t] for t in tiles if 0 <= t <= 33]
                lines.append(f"    {i + 1}. {meld_type}: {', '.join(tile_names)}")

            lines.append("")

        # 其他信息
        wall_remaining = self.config.get("wall", 70)
        current_player = self.config.get("current", 0)
        current_name = players[current_player].get("name", f"玩家{current_player}") if current_player < len(
            players) else "Unknown"

        lines.append(f"剩余牌数: {wall_remaining}张")
        lines.append(f"当前回合: {current_name}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def render_simple_view(self):
        """渲染简化视图（适合窄终端）"""
        # 根据编码支持选择渲染方式
        try:
            # 尝试渲染麻将符号
            return self._render_simple_view_with_tiles()
        except:
            # 如果失败，使用纯文本
            return self.render_text_only_view()

    def _render_simple_view_with_tiles(self):
        """渲染带麻将符号的简化视图"""
        if not self.config:
            return "无配置数据"

        lines = []

        # 游戏信息
        round_num = self.config.get("round", 0)
        dealer_seat = self.config.get("dealer", 0)
        round_name = self.get_round_name(round_num)

        lines.append("🀄 麻将配置视图 🀄")
        lines.append(f"局数: {round_name} | 庄家: 座位{dealer_seat}")

        # 宝牌信息
        bonus = self.config.get("bonus", [])
        if bonus:
            bonus_str = Tile.t34_to_g(bonus)
            lines.append(f"宝牌指示牌: {bonus_str}")

            # 计算宝牌
            dora_list = []
            for b in bonus:
                dora = Tile.bonus_dict.get(b, b + 1)
                dora_list.append(dora)
            dora_str = Tile.t34_to_g(dora_list)
            lines.append(f"宝牌: {dora_str}")

        lines.append("-" * 40)

        # 玩家信息
        players = self.config.get("players", [])
        for seat in range(4):
            player = players[seat] if seat < len(players) else {}
            player_name = player.get("name", f"玩家{seat}")
            player_score = player.get("score", 0)
            player_reach = player.get("reach", False)

            direction = self.player_positions.get(seat, "?")

            # 手牌
            hand = player.get("hand", [])
            if seat == 0:  # 玩家自己
                hand_str = Tile.t34_to_g(hand) if hand else "未设置"
            else:
                hand_str = "🀫" * len(hand) if hand else "未知"

            # 牌河
            discards = player.get("discards", [])
            discards_str = Tile.t34_to_g(discards) if discards else "无"

            # 副露
            melds = player.get("melds", [])
            melds_count = len(melds)

            # 构建玩家行
            reach_mark = " [立直]" if player_reach else ""
            player_line = f"{direction} {player_name} ({player_score}){reach_mark}"
            lines.append(player_line)

            if seat == 0:  # 玩家自己显示手牌
                lines.append(f"  手牌: {hand_str}")

            lines.append(f"  牌河: {discards_str}")
            lines.append(f"  副露: {melds_count}组")

            # 显示副露详情
            for i, meld in enumerate(melds):
                tiles = meld.get("tiles", [])
                meld_type = meld.get("type", "unknown")
                try:
                    tile_str = Tile.t34_to_g(tiles)
                except:
                    tile_str = str(tiles)
                lines.append(f"    {i + 1}. {meld_type}: {tile_str}")

            lines.append("")

        # 其他信息
        wall_remaining = self.config.get("wall", 70)
        current_player = self.config.get("current", 0)
        current_name = players[current_player].get("name", f"玩家{current_player}") if current_player < len(
            players) else "Unknown"

        lines.append(f"剩余牌数: {wall_remaining}张")
        lines.append(f"当前回合: {current_name}")

        return "\n".join(lines)


def load_example_config():
    """加载示例配置"""
    return {
        "round": 0,
        "dealer": 0,
        "current": 0,
        "wall": 50,
        "honba": 1,
        "reach_sticks": 1,

        "players": [
            {
                "name": "玩家",
                "score": 300,
                "hand": [0, 1, 2, 9, 10, 11, 18, 19, 20, 27, 27, 27, 27],
                "discards": [3, 4, 5],
                "melds": [],
                "reach": False
            },
            {
                "name": "AI东",
                "score": 250,
                "hand": [],
                "discards": [1, 3, 5, 7, 9, 11, 13, 15, 17, 10],
                "melds": [{"type": "pon", "tiles": [28, 28, 28], "called": 28, "from": 2}],
                "reach": True
            },
            {
                "name": "AI南",
                "score": 200,
                "hand": [],
                "discards": [2, 4, 6, 8, 10, 12, 14, 16, 18],
                "melds": [{"type": "chi", "tiles": [1, 2, 3], "called": 2, "from": 3}],
                "reach": False
            },
            {
                "name": "AI西",
                "score": 250,
                "hand": [],
                "discards": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
                "melds": [
                    {"type": "chi", "tiles": [9, 10, 11], "called": 10, "from": 0},
                    {"type": "pon", "tiles": [31, 31, 31], "called": 31, "from": 1}
                ],
                "reach": False
            }
        ],

        "bonus": [8, 17, 26]
    }


def setup_windows_encoding():
    """设置Windows编码"""
    if sys.platform == "win32":
        try:
            # 尝试设置UTF-8编码
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            return True
        except:
            try:
                # 尝试设置控制台编码
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleOutputCP(65001)  # UTF-8
                return True
            except:
                return False
    return True


def main():
    """主函数：渲染配置文件"""
    print("🀄 麻将配置渲染器 🀄")
    print("=" * 60)

    # 设置Windows编码（如果必要）
    if sys.platform == "win32":
        if not setup_windows_encoding():
            print("注意: Windows编码设置可能不完美，麻将符号可能无法正常显示")
            print("将使用纯文本模式显示")

    # 创建渲染器
    renderer = MahjongTableRenderer()

    # 选择配置源
    print("选择配置源:")
    print("  1. 示例配置")
    print("  2. 从文件加载配置")
    print("  3. 从JSON字符串输入")
    print("=" * 60)

    choice = input("请选择 (1/2/3): ").strip()

    config = None

    if choice == "1":
        config = load_example_config()
        print("✓ 使用示例配置")
    elif choice == "2":
        filename = input("请输入配置文件名: ").strip()
        if not filename:
            filename = "config.json"

        if renderer.load_config_from_file(filename):
            config = renderer.config
        else:
            print("加载失败，使用示例配置")
            config = load_example_config()
    elif choice == "3":
        print("请输入JSON配置字符串 (输入空行结束):")
        json_lines = []
        while True:
            line = input()
            if not line:
                break
            json_lines.append(line)

        json_str = '\n'.join(json_lines)

        try:
            config = json.loads(json_str)
            print("✓ JSON配置加载成功")
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析错误: {e}")
            print("使用示例配置")
            config = load_example_config()
    else:
        print("无效选择，使用示例配置")
        config = load_example_config()

    # 设置配置
    renderer.set_config(config)

    print("\n" + "=" * 60)
    print("麻将桌渲染:")
    print("=" * 60)

    # 检查终端宽度
    try:
        terminal_width = os.get_terminal_size().columns
    except:
        terminal_width = 80

    # 根据终端宽度和编码支持选择渲染方式
    try:
        # 测试是否支持麻将符号
        test_tile = Tile.t34_to_g([0])
        if terminal_width >= 80:
            # 尝试使用完整渲染
            print(renderer.render())
        else:
            # 使用简化渲染
            print("终端宽度较小，使用简化视图")
            print(renderer.render_simple_view())
    except Exception as e:
        print(f"注意: 麻将符号显示失败 ({e})，使用纯文本模式")
        print(renderer.render_text_only_view())

    print("\n" + "=" * 60)

    # 保存配置选项
    save_choice = input("是否保存当前配置到文件? (y/n): ").strip().lower()
    if save_choice == 'y':
        filename = input("请输入文件名 (默认: mahjong_config_rendered.json): ").strip()
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mahjong_config_rendered_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✓ 配置已保存到: {filename}")
        except Exception as e:
            print(f"✗ 保存失败: {e}")


if __name__ == "__main__":
    main()