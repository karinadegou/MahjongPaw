from ultralytics import YOLO
import cv2
import os


def perceive():
    # 1. 加载模型
    model = YOLO("Mahjong_YOLO/trained_models_v2/yolo11m_best.pt")
    # model = YOLO("trained_models_v2/yolo11m_best.pt")
    # 2. 读取图片并调整大小到640x640
    img = cv2.imread("Mahjong_YOLO/test.png")
    # img = cv2.imread("test.png")
    img_resized = cv2.resize(img, (640, 640))

    # 3. 模型预测
    results = model.predict(source=img_resized, imgsz=640)  # imgsz可以显式指定

    # 4. 收集玩家手牌区域的麻将牌
    r = results[0]
    hand_tiles = []

    for box in r.boxes:
        cls = int(box.cls[0])  # 类别ID
        conf = float(box.conf[0])  # 置信度
        x1, y1, x2, y2 = box.xyxy[0].tolist()  # 左上角和右下角坐标
        tile = model.names[cls]  # 对应牌型

        # 判断是否在玩家手牌区域
        if x1 >= 70 and x2 <= 610 and y1 >= 530 and y2 <= 610:
            hand_tiles.append((x1, tile, conf, (x1, y1, x2, y2)))

    # 5. 按 x 坐标从左到右排序
    hand_tiles.sort(key=lambda x: x[0])

    # print("=== 玩家手牌区域（从左到右） ===")
    for _, tile, conf, box_coords in hand_tiles:
        x1, y1, x2, y2 = box_coords
        # print(f"Tile: {tile}, Conf: {conf:.3f}, Box: ({x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f})")

    # print(f'玩家手牌区域总共识别到 {len(hand_tiles)} 张牌')

    # 6. 将牌列表转换为麻将字符串表示
    hand_string = convert_tiles_to_mahjong_string_generic(hand_tiles)
    # print(f'麻将字符串表示: {hand_string}')

    # 7. 保存预测结果图片
    # r.show()
    result_plot = r.plot()
    save_path = "Mahjong_YOLO/prediction_result.jpg"
    
    # 如果文件已存在，先删除
    if os.path.exists(save_path):
        try:
            os.remove(save_path)
        except Exception as e:
            print(f"删除旧文件失败: {e}")

    cv2.imwrite(save_path, result_plot)
    # print(f"预测结果图片已保存至: {save_path}")

    return hand_tiles, hand_string


def convert_tiles_to_mahjong_string(hand_tiles):
    """
    将识别出的牌列表转换为麻将字符串表示
    格式如: 123456789m123s11z

    Args:
        hand_tiles: 列表，每个元素为 (x坐标, 牌名, 置信度, 坐标框)

    Returns:
        str: 麻将字符串表示
    """
    # 分离不同花色的牌
    man_tiles = []  # 万子
    pin_tiles = []  # 筒子
    sou_tiles = []  # 索子
    honor_tiles = []  # 字牌

    # 牌名到数字的映射
    honor_mapping = {
        'dong': '1',  # 东
        'nan': '2',  # 南
        'xi': '3',  # 西
        'bei': '4',  # 北
        'bai': '5',  # 白
        'fa': '6',  # 发
        'zhong': '7'  # 中
    }

    for _, tile_name, _, _ in hand_tiles:
        # 将牌名转换为小写以统一处理
        tile_name_lower = tile_name.lower()

        if 'm' in tile_name_lower:  # 万子
            # 提取数字部分（如 "1m" -> "1"）
            num = tile_name_lower.replace('m', '')
            man_tiles.append(int(num))
        elif 'p' in tile_name_lower:  # 筒子
            num = tile_name_lower.replace('p', '')
            pin_tiles.append(int(num))
        elif 's' in tile_name_lower:  # 索子
            num = tile_name_lower.replace('s', '')
            sou_tiles.append(int(num))
        else:  # 字牌
            # 处理常见的中文字牌名
            if tile_name_lower in honor_mapping:
                honor_tiles.append(honor_mapping[tile_name_lower])
            elif tile_name_lower.isdigit() and 1 <= int(tile_name_lower) <= 7:
                # 如果是数字1-7，直接作为字牌
                honor_tiles.append(tile_name_lower)
            else:
                # 尝试其他可能的表示
                if 'dong' in tile_name_lower or 'east' in tile_name_lower:
                    honor_tiles.append('1')
                elif 'nan' in tile_name_lower or 'south' in tile_name_lower:
                    honor_tiles.append('2')
                elif 'xi' in tile_name_lower or 'west' in tile_name_lower:
                    honor_tiles.append('3')
                elif 'bei' in tile_name_lower or 'north' in tile_name_lower:
                    honor_tiles.append('4')
                elif 'bai' in tile_name_lower or 'hak' in tile_name_lower:
                    honor_tiles.append('5')
                elif 'fa' in tile_name_lower or 'hatsu' in tile_name_lower:
                    honor_tiles.append('6')
                elif 'zhong' in tile_name_lower or 'chun' in tile_name_lower:
                    honor_tiles.append('7')

    # 按数字排序
    man_tiles.sort()
    pin_tiles.sort()
    sou_tiles.sort()
    honor_tiles.sort()

    # 构建字符串
    result_parts = []

    if man_tiles:
        man_str = ''.join(str(num) for num in man_tiles) + 'm'
        result_parts.append(man_str)

    if pin_tiles:
        pin_str = ''.join(str(num) for num in pin_tiles) + 'p'
        result_parts.append(pin_str)

    if sou_tiles:
        sou_str = ''.join(str(num) for num in sou_tiles) + 's'
        result_parts.append(sou_str)

    if honor_tiles:
        honor_str = ''.join(honor_tiles) + 'z'
        result_parts.append(honor_str)

    # 如果没有识别到任何牌，返回空字符串
    if not result_parts:
        return ""

    return ''.join(result_parts)


# 如果您的模型输出格式不同，可以使用这个通用版本
def convert_tiles_to_mahjong_string_generic(tiles_list):
    """
    通用版本：将各种格式的牌名转换为麻将字符串
    """
    # 定义牌名到标准格式的映射
    tile_mapping = {
        # red
        '0m': '5m', '0s': '5s', '0p': '5p',
        # 万子
        '1m': '1m', '2m': '2m', '3m': '3m', '4m': '4m', '5m': '5m',
        '6m': '6m', '7m': '7m', '8m': '8m', '9m': '9m',
        'man1': '1m', 'man2': '2m', 'man3': '3m', 'man4': '4m', 'man5': '5m',
        'man6': '6m', 'man7': '7m', 'man8': '8m', 'man9': '9m',

        # 筒子
        '1p': '1p', '2p': '2p', '3p': '3p', '4p': '4p', '5p': '5p',
        '6p': '6p', '7p': '7p', '8p': '8p', '9p': '9p',
        'pin1': '1p', 'pin2': '2p', 'pin3': '3p', 'pin4': '4p', 'pin5': '5p',
        'pin6': '6p', 'pin7': '7p', 'pin8': '8p', 'pin9': '9p',

        # 索子
        '1s': '1s', '2s': '2s', '3s': '3s', '4s': '4s', '5s': '5s',
        '6s': '6s', '7s': '7s', '8s': '8s', '9s': '9s',
        'sou1': '1s', 'sou2': '2s', 'sou3': '3s', 'sou4': '4s', 'sou5': '5s',
        'sou6': '6s', 'sou7': '7s', 'sou8': '8s', 'sou9': '9s',

        # 字牌
        '1z': '1z', '2z': '2z', '3z': '3z', '4z': '4z', '5z': '5z', '6z': '6z', '7z': '7z',
        'dong': '1z', 'nan': '2z', 'xi': '3z', 'bei': '4z',
        'bai': '5z', 'fa': '6z', 'zhong': '7z',
        'east': '1z', 'south': '2z', 'west': '3z', 'north': '4z',
        'white': '5z', 'green': '6z', 'red': '7z',
        'ton': '1z', 'nan': '2z', 'sha': '3z', 'pei': '4z',
        'haku': '5z', 'hatsu': '6z', 'chun': '7z'
    }

    # 分离不同花色的牌
    man_tiles = []
    pin_tiles = []
    sou_tiles = []
    honor_tiles = []

    for tile_info in tiles_list:
        if len(tile_info) >= 2:
            tile_name = str(tile_info[1]).lower()

            # 查找映射
            mapped_tile = None
            for key, value in tile_mapping.items():
                if key in tile_name:
                    mapped_tile = value
                    break

            if mapped_tile:
                if mapped_tile.endswith('m'):
                    man_tiles.append(int(mapped_tile[0]))
                elif mapped_tile.endswith('p'):
                    pin_tiles.append(int(mapped_tile[0]))
                elif mapped_tile.endswith('s'):
                    sou_tiles.append(int(mapped_tile[0]))
                elif mapped_tile.endswith('z'):
                    honor_tiles.append(mapped_tile[0])
            else:
                # 尝试直接提取数字和花色
                import re
                match = re.search(r'(\d+)([mpsz])', tile_name)
                if match:
                    num, suit = match.groups()
                    if suit == 'm':
                        man_tiles.append(int(num))
                    elif suit == 'p':
                        pin_tiles.append(int(num))
                    elif suit == 's':
                        sou_tiles.append(int(num))
                    elif suit == 'z':
                        honor_tiles.append(num)

    # 排序并构建字符串
    result_parts = []

    if man_tiles:
        man_tiles.sort()
        result_parts.append(''.join(str(num) for num in man_tiles) + 'm')

    if pin_tiles:
        pin_tiles.sort()
        result_parts.append(''.join(str(num) for num in pin_tiles) + 'p')

    if sou_tiles:
        sou_tiles.sort()
        result_parts.append(''.join(str(num) for num in sou_tiles) + 's')

    if honor_tiles:
        honor_tiles.sort()
        result_parts.append(''.join(honor_tiles) + 'z')

    return ''.join(result_parts)


# 使用示例
if __name__ == "__main__":
    # 模拟数据
    perceive()