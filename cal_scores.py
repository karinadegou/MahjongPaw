from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.tile import TilesConverter

def calc_hand_score(
    tiles_136,
    win_tile,
    melds=None,
    dora_indicators=None,
    player_wind=0,
    round_wind=0,
    is_riichi=False,
    is_tsumo=False
):
    calculator = HandCalculator()

    config = HandConfig(
        is_riichi=is_riichi,
        is_tsumo=is_tsumo,
        player_wind=player_wind,
        round_wind=round_wind
    )

    result = calculator.estimate_hand_value(
        tiles=tiles_136,
        win_tile=win_tile,
        melds=melds or [],
        dora_indicators=dora_indicators or [],
        config=config
    )

    if result.error:
        raise ValueError(result.error)

    yaku_list = []
    for y in result.yaku:
        han = y.han_open if result.is_open_hand else y.han_closed
        yaku_list.append((y.name, han))

    yakuman_list = [y.name for y in result.yaku if y.is_yakuman]

    return {
        "han": result.han,
        "fu": result.fu,
        "cost": result.cost,
        "yaku": [
            (
                y.name,
                y.han_open if result.is_open_hand else y.han_closed
            )
            for y in result.yaku
            if not y.is_yakuman
        ],
        "yakuman": yakuman_list,  # 役满名称列表
        "yakuman_count": len(yakuman_list)
    }


# 123m 456m 789p 234s 55s，自摸 5s
tiles_136 = TilesConverter.string_to_136_array(
    man="123456",
    pin="789",
    sou="23455"
)

# 假设最后摸到的是 5索（souzu 5）
# souzu 5 的 34 编码是 18 + 4 = 22 → 136 编码范围 88~91
win_tile = 88

result = calc_hand_score(
    tiles_136=tiles_136,
    win_tile=win_tile,
    is_riichi=True,
    is_tsumo=True,
    player_wind=0,
    round_wind=0
)

# print(result)
