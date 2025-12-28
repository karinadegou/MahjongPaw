from random import choice
import sys

# 保存原始标准输出
original_stdout = sys.stdout

from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld
from mahjong.shanten import Shanten
from mahjong.agari import Agari
from cal_scores import calc_hand_score
from Mahjong_YOLO.test import perceive
from collections import Counter
import numpy as np

class FixedMahjongAnalyzer:
    """修复版的麻将分析器"""

    def __init__(self):
        self.calculator = HandCalculator()
        self.agari = Agari()
        self.shanten = Shanten()

    def _wind_to_str(self, wind):
        """将风编号转为中文"""
        wind_map = {
            0: "东",
            1: "南",
            2: "西",
            3: "北"
        }
        return wind_map.get(wind, "未知")

    def _estimate_score_fixed(
            tiles_136,
            waiting_tiles_34,
            melds=None,
            dora_indicators=None,
            player_wind=0,
            round_wind=0,
            is_riichi=False,
            is_tsumo=False
    ):
        """计算所有听牌张中点数最高的"""
        calculator = HandCalculator()
        best_result = None
        best_tile_34 = None

        for tile_34 in waiting_tiles_34:
            win_tile = tile_34 * 4  # 转换为136编码

            config = HandConfig(
                is_riichi=is_riichi,
                is_tsumo=is_tsumo,
                player_wind=player_wind,
                round_wind=round_wind
            )

            try:
                result = calculator.estimate_hand_value(
                    tiles=tiles_136,
                    win_tile=win_tile,
                    melds=melds or [],
                    dora_indicators=dora_indicators or [],
                    config=config
                )

                if result.error:
                    continue

                if best_result is None or result.cost['main'] > best_result.cost['main']:
                    best_result = result
                    best_tile_34 = tile_34

            except Exception:
                continue

        if best_result:
            yaku_list = []
            for y in best_result.yaku:
                han = y.han_open if best_result.is_open_hand else y.han_closed
                yaku_list.append((y.name, han))

            yakuman_list = [y.name for y in best_result.yaku if y.is_yakuman]

            return {
                "best_waiting_tile": best_tile_34,
                "han": best_result.han,
                "fu": best_result.fu,
                "cost": best_result.cost,
                "yaku": yaku_list,
                "yakuman": yakuman_list,
                "yakuman_count": len(yakuman_list)
            }

        return None

    def _tile_34_to_136(self, tile_34, tiles_136):
        """
        从 34 编码转换为一个可用的 136 编码实体牌
        """
        for i in range(tile_34 * 4, tile_34 * 4 + 4):
            if i not in tiles_136:
                return i
        return tile_34 * 4  # 理论上不会走到这里

    def _normalize_melds(self, melds):
        """
        将各种形式的 melds 统一为 List[Meld]
        """
        if melds is None:
            return []

        normalized = []

        for m in melds:
            # 已经是 Meld 对象
            if isinstance(m, Meld):
                normalized.append(m)
                continue

            # dict 形式
            if isinstance(m, dict):
                meld_type = m.get("type")
                tiles = m.get("tiles", [])
                if meld_type == "chi":
                    normalized.append(Meld(Meld.CHI, tiles=tiles))
                elif meld_type == "pon":
                    normalized.append(Meld(Meld.PON, tiles=tiles))
                elif meld_type == "kan":
                    normalized.append(Meld(Meld.KAN, tiles=tiles))
                continue

            # string 形式（最低信息）
            if isinstance(m, str):
                if m == "chi":
                    normalized.append(Meld(Meld.CHI, tiles=[]))
                elif m == "pon":
                    normalized.append(Meld(Meld.PON, tiles=[]))
                elif m == "kan":
                    normalized.append(Meld(Meld.KAN, tiles=[]))
                continue

            raise TypeError(f"Unsupported meld type: {type(m)}")

        return normalized

    def analyze(self, hand_str, dora_indicators=None, melds=None,
                player_wind=0, round_wind=0, is_riichi=False):
        """
        分析手牌

        参数:
            hand_str: 手牌字符串，如 "123m456p789s11122z"
            dora_indicators: 宝牌指示牌列表，如 ["5m", "3z"]
            melds: 副露列表，如 ["123m", "555p"]
            player_wind: 自风 (0=东, 1=南, 2=西, 3=北)
            round_wind: 场风 (0=东, 1=南, 2=西, 3=北)
            is_riichi: 是否立直
        """
        print("=" * 70)
        print("🀄 麻将手牌分析报告")
        print("=" * 70)

        # 1. 转换手牌
        tiles_136 = self._string_to_tiles(hand_str)
        if tiles_136 is None or len(tiles_136) == 0:
            print("❌ 手牌格式错误或为空")
            return

        print(f"\n📊 基础信息:")
        print(f"   手牌: {hand_str}")
        print(f"   牌数: {len(tiles_136)}张")
        print(f"   自风: {self._wind_to_str(player_wind)}")
        print(f"   场风: {self._wind_to_str(round_wind)}")
        print(f"   立直: {'是' if is_riichi else '否'}")

        # 转换为34编码的数量数组
        tiles_34_array = TilesConverter.to_34_array(tiles_136)

        # 转换为34编码的列表
        tiles_34_list = self._tiles_136_to_34_list(tiles_136)

        # 2. 牌型分布
        self._print_distribution_fixed(tiles_34_array)

        # 3. 向听数分析
        self._print_shanten_fixed(tiles_34_list)

        # 4. 听牌分析
        self._print_tenpai_fixed(tiles_34_list)

        print(f"\n" + "=" * 70)
        print("🎉 分析完成！")
        print("=" * 70)

    def _string_to_tiles(self, hand_str):
        """将字符串转换为136编码的牌"""
        try:
            # 分离不同的花色
            manzu = ''
            pinzu = ''
            souzu = ''
            honors = ''

            current_part = ''
            for char in hand_str:
                if char.isdigit():
                    current_part += char
                elif char in 'mpsz':
                    if char == 'm':
                        manzu = current_part
                    elif char == 'p':
                        pinzu = current_part
                    elif char == 's':
                        souzu = current_part
                    elif char == 'z':
                        honors = current_part
                    current_part = ''

            # 检查是否有数字但没有花色的情况
            if current_part:
                print(f"警告: 未指定的数字 '{current_part}'")

            return TilesConverter.string_to_136_array(
                man=manzu if manzu else None,
                pin=pinzu if pinzu else None,
                sou=souzu if souzu else None,
                honors=honors if honors else None
            )
        except Exception as e:
            print(f"转换手牌时出错: {e}")
            return None

    def _tiles_136_to_34_list(self, tiles_136):
        """将136编码列表转换为34编码列表"""
        return [tile // 4 for tile in tiles_136]

    def _print_distribution_fixed(self, tiles_34_array):
        """打印牌型分布（使用数量数组）"""
        print(f"\n🎯 牌型分布:")

        # tiles_34_array 是长度为34的数组，每个元素表示该种牌的数量
        total_tiles = sum(tiles_34_array)

        # 统计各花色牌数
        man_count = sum(tiles_34_array[0:9])  # 0-8: 万子
        pin_count = sum(tiles_34_array[9:18])  # 9-17: 筒子
        sou_count = sum(tiles_34_array[18:27])  # 18-26: 索子
        honor_count = sum(tiles_34_array[27:34])  # 27-33: 字牌

        print(f"    万子: {man_count}张")
        print(f"    筒子: {pin_count}张")
        print(f"    索子: {sou_count}张")
        print(f"    字牌: {honor_count}张")
        print(f"    总牌数: {total_tiles}张")

        # 计算幺九牌
        terminal_honor_indices = [0, 8, 9, 17, 18, 26] + list(range(27, 34))
        terminal_honor_count = sum(tiles_34_array[i] for i in terminal_honor_indices)

        if total_tiles > 0:
            ratio = terminal_honor_count / total_tiles
            print(f"    幺九牌: {terminal_honor_count}张 ({ratio:.1%})")

    def _print_shanten_fixed(self, tiles_34_list):
        """打印向听数分析"""
        print(f"\n🎲 向听数分析:")

        if len(tiles_34_list) != 13 and len(tiles_34_list) != 14:
            print(f"    ⚠️  手牌{len(tiles_34_list)}张，标准手牌应为13或14张")
            return

        try:
            # 转换为数量数组用于shanten计算
            tiles_34_array = self._list_to_array(tiles_34_list)

            # 普通和牌向听数
            regular_shanten = self.shanten.calculate_shanten(tiles_34_array)
            print(f"    普通和牌向听数: {regular_shanten}")

            if regular_shanten == -1:
                print("    ✅ 已经和牌！")
            elif regular_shanten == 0:
                print("    ✅ 听牌状态")
            elif regular_shanten == 1:
                print("    🔄 1向听，接近听牌")
            elif regular_shanten == 2:
                print("    🔄 2向听")
            else:
                print(f"    ⏳ {regular_shanten}向听，还需努力")

        except Exception as e:
            print(f"    向听数计算失败: {e}")

    def _print_tenpai_fixed_with_score(self, tiles_34_list, tiles_136=None, melds=None, dora_indicators=None,
                                       player_wind=0, round_wind=0, is_riichi=False):
        """打印听牌分析并计算每个听牌张的点数"""
        print(f"\n🎯 听牌分析:")

        if len(tiles_34_list) != 13:
            print(f"    ⚠️  当前手牌{len(tiles_34_list)}张，听牌分析需要13张")
            return

        try:
            # 转换为数量数组用于agari判断
            tiles_34_array = self._list_to_array(tiles_34_list)

            # 检查是否已经和牌
            if self.agari.is_agari(tiles_34_array):
                print("    ✅ 已经和牌！")
                return

            # 查找有效的听牌（添加后能形成和牌形的牌）
            valid_waiting_tiles = []
            for tile_34 in range(34):
                # 跳过已经满4张的牌
                if tiles_34_array[tile_34] >= 4:
                    continue

                # 模拟添加这张牌
                temp_array = tiles_34_array.copy()
                temp_array[tile_34] += 1

                # 检查是否能和牌
                if self.agari.is_agari(temp_array):
                    valid_waiting_tiles.append(tile_34)

            if not valid_waiting_tiles:
                print("    ❌ 未听牌")
                return

            print(f"    🎯 听牌！等待 {len(valid_waiting_tiles)} 种牌")
            print()

            # 计算每个有效听牌张的点数
            score_results = []

            for tile_34 in valid_waiting_tiles:
                try:
                    # 创建和牌手牌（13张手牌 + 和牌张 = 14张）
                    winning_hand_34 = tiles_34_list.copy()
                    winning_hand_34.append(tile_34)  # 添加和牌张，现在是14张

                    # 将和牌手牌转换为136编码（14张牌）
                    winning_hand_136 = self._convert_34_list_to_136(winning_hand_34)

                    # 和牌张的136编码（取最后一张牌，即刚添加的和牌张）
                    win_tile_136 = winning_hand_136[-1]

                    # 计算点数
                    score_result = calc_hand_score(
                        tiles_136=winning_hand_136,  # 14张和牌手牌
                        win_tile=win_tile_136,  # 和牌张
                        melds=melds,
                        dora_indicators=dora_indicators,
                        player_wind=player_wind,
                        round_wind=round_wind,
                        is_riichi=is_riichi,
                        is_tsumo=False  # 听牌分析一般假设荣和
                    )

                    # 获取牌名
                    tile_name = self._tile_34_to_name(tile_34)

                    # 获取牌在手牌中的数量和剩余牌数
                    in_hand = tiles_34_array[tile_34]
                    remaining = 4 - in_hand

                    # 整理结果
                    score_results.append({
                        'tile_34': tile_34,
                        'tile_name': tile_name,
                        'in_hand': in_hand,
                        'remaining': remaining,
                        'han': score_result['han'],
                        'fu': score_result['fu'],
                        'cost': score_result['cost']['main'],
                        'yaku': score_result['yaku'],
                        'yakuman': score_result['yakuman'],
                        'yakuman_count': score_result['yakuman_count']
                    })

                    print(
                        f"    ✓ 听{tile_name}: {score_result['han']}翻{score_result['fu']}符 {score_result['cost']['main']}点")

                except ValueError as e:
                    if "hand_not_winning" in str(e):
                        # 手牌可能有问题，跳过
                        print(f"    ⚠️  听{tile_34}({self._tile_34_to_name(tile_34)})不能和牌")
                    else:
                        print(f"    ⚠️  听{tile_34}({self._tile_34_to_name(tile_34)})计算失败: {e}")
                    continue
                except Exception as e:
                    print(f"    ⚠️  听{tile_34}({self._tile_34_to_name(tile_34)})发生错误: {e}")
                    continue

            if not score_results:
                print("    ❌ 所有听牌张点数计算失败")
                return

            print()

            # 按点数排序（从高到低）
            score_results.sort(key=lambda x: x['cost'], reverse=True)

            # 统计信息
            total_effective_tiles = sum(r['remaining'] for r in score_results)
            print(f"    📊 理论有效进张: {total_effective_tiles}张")
            print()

            # 按花色分组显示
            man_waiting = []
            pin_waiting = []
            sou_waiting = []
            honor_waiting = []

            for result in score_results:
                tile_34 = result['tile_34']
                tile_name = result['tile_name']
                cost = result['cost']

                # 格式化显示
                if cost >= 8000:
                    if result['yakuman_count'] > 0:
                        cost_str = f"役满{result['yakuman_count']}倍"
                    else:
                        cost_str = f"{cost // 1000}千点"
                else:
                    cost_str = f"{cost}点"

                # 添加翻数信息
                han_info = f"{result['han']}翻" if result['han'] > 0 else "无役"

                display_str = f"{tile_name}({han_info}/{cost_str})"

                if 0 <= tile_34 <= 8:
                    man_waiting.append(display_str)
                elif 9 <= tile_34 <= 17:
                    pin_waiting.append(display_str)
                elif 18 <= tile_34 <= 26:
                    sou_waiting.append(display_str)
                else:
                    honor_waiting.append(display_str)

            print("    🃏 听牌张及点数:")
            if man_waiting:
                print(f"        万子: {', '.join(man_waiting)}")
            if pin_waiting:
                print(f"        筒子: {', '.join(pin_waiting)}")
            if sou_waiting:
                print(f"        索子: {', '.join(sou_waiting)}")
            if honor_waiting:
                print(f"        字牌: {', '.join(honor_waiting)}")

            print()

            # 显示点数最高的几个听牌张的详细信息
            if len(score_results) > 0:
                print("    🏆 高打点听牌张详情:")
                top_n = min(3, len(score_results))

                for i in range(top_n):
                    result = score_results[i]

                    # 役满特殊显示
                    if result['yakuman_count'] > 0:
                        print(f"        {i + 1}. 听{result['tile_name']} - 役满{result['yakuman_count']}倍!")
                        if result['yakuman']:
                            print(f"           役满役: {', '.join(result['yakuman'])}")
                    else:
                        print(
                            f"        {i + 1}. 听{result['tile_name']} - {result['han']}翻{result['fu']}符 {result['cost']}点")

                        # 显示役种
                        if result['yaku']:
                            yaku_list = []
                            for name, han in result['yaku']:
                                if han > 0:
                                    yaku_list.append(f"{name}({han}翻)")
                            if yaku_list:
                                print(f"           役种: {', '.join(yaku_list)}")
                        else:
                            print(f"           役种: 无役")

                    # 显示牌的张数信息
                    print(f"           手牌中有{result['in_hand']}张，剩余{result['remaining']}张")
                    print()

                # 如果有役满，特别提示
                yakuman_results = [r for r in score_results if r['yakuman_count'] > 0]
                if yakuman_results:
                    print(f"    ⭐ 役满机会: {len(yakuman_results)}种牌")

                # 显示平均点数和最高点数
                avg_cost = sum(r['cost'] for r in score_results) / len(score_results)
                max_cost = score_results[0]['cost']
                max_tile = score_results[0]['tile_name']

                print(f"    📈 统计:")
                print(f"        平均点数: {int(avg_cost)}点")
                print(f"        最高点数: 听{max_tile} - {max_cost}点")

                # 根据点数给出建议
                print()
                print("    💡 建议:")
                if any(r['yakuman_count'] > 0 for r in score_results):
                    print("        有役满机会！优先追求役满听牌")
                elif max_cost >= 8000:
                    print("        有高打点机会，优先追求高点数听牌")
                elif max_cost >= 2000:
                    print("        打点中等，可以考虑立直")
                elif max_cost > 0:
                    print("        打点较低，可以考虑改良手牌或防守")
                else:
                    print("        无役听牌，需要改良")

        except Exception as e:
            print(f"    听牌分析出错: {e}")
            import traceback
            traceback.print_exc()

    def _convert_34_list_to_136(self, tiles_34_list):
        """
        将34编码列表转换为136编码列表
        为每张牌分配唯一的136编码
        """
        # 统计每种牌已经使用了几个编码
        tile_counts = {}

        tiles_136 = []
        for tile_34 in tiles_34_list:
            if tile_34 not in tile_counts:
                tile_counts[tile_34] = 0

            # 计算136编码：tile_34 * 4 + (0-3)
            tile_136 = tile_34 * 4 + tile_counts[tile_34]
            tile_counts[tile_34] += 1

            tiles_136.append(tile_136)

        return tiles_136

    def _tile_34_to_name(self, tile_34):
        """将34编码转换为牌名"""
        if tile_34 < 9:  # 万子
            return f"{tile_34 + 1}m"
        elif tile_34 < 18:  # 筒子
            return f"{tile_34 - 8}p"
        elif tile_34 < 27:  # 索子
            return f"{tile_34 - 17}s"
        else:  # 字牌
            honors = ["东", "南", "西", "北", "白", "发", "中"]
            return honors[tile_34 - 27]

    def _list_to_array(self, tiles_34_list):
        """将34编码列表转换为数量数组"""
        array = [0] * 34
        for tile in tiles_34_list:
            array[tile] += 1
        return array

    # 如果您希望保持原来的函数名，可以这样包装
    def _print_tenpai_fixed(self, tiles_34_list, *args, **kwargs):
        """兼容原函数名，调用新版函数"""
        return self._print_tenpai_fixed_with_score(tiles_34_list, *args, **kwargs)

    def _find_waiting_tiles_simple(self, tiles_34_list):
        """简单方法查找听牌"""
        waiting = []

        # 检查添加每张牌后是否能和牌
        for tile_34 in range(34):
            # 检查是否还有剩余牌
            if tiles_34_list.count(tile_34) < 4:
                test_hand = tiles_34_list + [tile_34]
                test_array = self._list_to_array(test_hand)
                if self.agari.is_agari(test_array):
                    waiting.append(tile_34)

        return waiting

    def _list_to_array(self, tiles_34_list):
        """将34编码列表转换为数量数组"""
        array = [0] * 34
        for tile in tiles_34_list:
            array[tile] += 1
        return array

    def _wind_to_str(self, wind):
        """风向数字转字符串"""
        winds = ['东', '南', '西', '北']
        return winds[wind] if 0 <= wind < 4 else '未知'

    def _tile_34_to_name(self, tile_34):
        """34编码转牌名"""
        if tile_34 < 27:
            suit = tile_34 // 9
            number = (tile_34 % 9) + 1
            suits = ['万', '筒', '索']
            return f"{number}{suits[suit]}"
        else:
            honors = ['东', '南', '西', '北', '白', '发', '中']
            return honors[tile_34 - 27]


# 测试函数
def test_analyzer():
    """测试分析器"""
    analyzer = FixedMahjongAnalyzer()

    test_cases = [
        {
            "name": "国士无双听牌",
            "hand": "19m19p19s1234567z",
            "dora": None,
            "melds": None,
            "player_wind": 0,
            "round_wind": 0,
            "riichi": False
        },
        {
            "name": "断幺九手牌",
            "hand": "234m345p456s22z",
            "dora": ["5m"],
            "melds": None,
            "player_wind": 0,
            "round_wind": 0,
            "riichi": False
        },
        {
            "name": "混一色手牌",
            "hand": "111222333m55566z",
            "dora": None,
            "melds": ["555z"],
            "player_wind": 0,
            "round_wind": 0,
            "riichi": False
        },
        {
            "name": "七对子手牌",
            "hand": "1133m5577p1199s22z",
            "dora": None,
            "melds": None,
            "player_wind": 1,
            "round_wind": 0,
            "riichi": True
        }
    ]

    for test in test_cases:
        print(f"\n{'=' * 70}")
        print(f"测试: {test['name']}")
        print(f"{'=' * 70}")

        analyzer.analyze(
            hand_str=test['hand'],
            dora_indicators=test['dora'],
            melds=test['melds'],
            player_wind=test['player_wind'],
            round_wind=test['round_wind'],
            is_riichi=test['riichi']
        )


def main():
    """主函数"""
    analyzer = FixedMahjongAnalyzer()

    print("收到你的截图了，雀宝正在努力分析ing。。。")
    # print("欢迎使用麻将手牌分析工具！")
    # print("请选择分析模式：")
    # print("1. 运行示例测试")
    # print("2. 自定义分析")

    # choice = input("请输入选择 (1/2): ").strip()

    choice = "2"

    if choice == "1":
        test_analyzer()

    elif choice == "2":
        # print("\n请输入手牌信息：")

        _, hand_str = perceive()

        # dora_input = input("宝牌指示牌 (用空格分隔，如 5m 3z，直接回车跳过): ").strip()
        dora_input = ""
        dora_indicators = dora_input.split() if dora_input else None

        # melds_input = input("副露 (用空格分隔，如 123m 555p，直接回车跳过): ").strip()
        melds_input = ""
        melds = melds_input.split() if melds_input else None

        # player_wind = input("自风 (0=东, 1=南, 2=西, 3=北，默认0): ").strip()
        player_wind = ""
        player_wind = int(player_wind) if player_wind else 0

        # round_wind = input("场风 (0=东, 1=南, 2=西, 3=北，默认0): ").strip()
        round_wind = ""
        round_wind = int(round_wind) if round_wind else 0

        # riichi_input = input("是否立直 (y/n，默认n): ").strip().lower()
        riichi_input = ""
        is_riichi = riichi_input == 'y'

        print("\n")

        # 重定向到文件
        f = open('output.txt', 'w', encoding='utf-8')
        sys.stdout = f  # 重定向到文件

        analyzer.analyze(
            hand_str=hand_str,
            dora_indicators=dora_indicators,
            melds=melds,
            player_wind=player_wind,
            round_wind=round_wind,
            is_riichi=is_riichi
        )

        f.close()
        sys.stdout = original_stdout  # 恢复标准输出

        import api

    else:
        print("无效选择")

# if __name__ == "__main__":
main()