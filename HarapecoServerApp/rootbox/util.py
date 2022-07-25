import hashlib
import math

# ガチャ用乱数ジェネレータ
# 後からの検証が可能なため、ガチャ操作は事実上不可能。
def calculate_rnd_hash(min_num, max_num, hash_num):
    # ハッシュ関数（SHA512）を計算
    s256 = hashlib.sha256(hash_num.encode()).hexdigest()

    # 文字数がxxxの「0xfff...fff + 1」をつくる
    s256maxstr = "10000000000000000000000000000000000000000000000000000000000000000"

    # ハッシュ関数の範囲から数値換算
    nowval = int('0x' + s256, 16) * (max_num - min_num) / int('0x' + s256maxstr, 16)

    # 数値を返す
    return min_num + math.floor((max_num + 1 - min_num) * nowval)