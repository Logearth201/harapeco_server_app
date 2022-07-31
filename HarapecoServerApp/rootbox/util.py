import hashlib
import math

# ガチャ用乱数ジェネレータ
# 後からの検証が可能なため、ガチャ操作は事実上不可能。
def calculate_rnd_hash(rootbox_items, hash_num):
    min_num = 0
    max_num = 0

    for rootbox_item in rootbox_items:
        max_num += rootbox_item.permutation

    # ハッシュ関数（SHA512）を計算
    s256 = hashlib.sha256(hash_num.encode()).hexdigest()

    # 文字数がxxxの「0xfff...fff + 1」をつくる
    s256maxstr = "10000000000000000000000000000000000000000000000000000000000000000"

    # ハッシュ関数の範囲から数値換算
    nowval = int('0x' + s256, 16) * (max_num) / int('0x' + s256maxstr, 16)
    
    # 答えを返す(0～max_num - 1の範囲で)
    ans_base = math.floor(nowval)

    # 対応場所を求め、計算結果を反映させる
    for rootbox_item in rootbox_items:
        if ans_base < rootbox_item.permutation:
            return rootbox_item.id
        ans_base -= rootbox_item.permutation

    return -1