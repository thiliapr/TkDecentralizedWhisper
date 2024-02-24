import secrets
from typing import Any

key_chars = "abcdefghijklmnopqrstuvwxyz_"
default_max_random_int = 65536
u_split_str_num = 4
u_random_list_value_num = 4


def generate_random_value(word_dict: dict[int, list[str]], max_random_int: int = default_max_random_int,
                          type_exclude=None, value_in_list: bool = False) -> int | str | bool | list[Any]:
    if type_exclude is None:
        type_exclude = []
    word_lengths: list[int] = list(word_dict.keys())

    v_type = secrets.choice([t for t in [int, str, bool, list] if (t not in type_exclude)])
    if v_type == int:
        value = secrets.randbelow(max_random_int)
    elif v_type == str:
        value = secrets.choice(word_dict[secrets.choice(word_lengths)])
    elif v_type == bool:
        value = secrets.choice([True, False])
    else:
        if not value_in_list:
            value = [generate_random_value(word_dict, max_random_int=max_random_int, value_in_list=True)
                     for _ in range(u_random_list_value_num + secrets.randbelow(3) - 2)]
        else:
            value = []

    return value


def WLER_confuse(src: dict[str, Any], word_list: list[str]) -> dict[str, Any]:
    # Convert word list to dict
    word_lengths = {len(word) for word in word_list}
    word_dict: dict[int, list[str]] = {length: [word for word in word_list if len(word) == length] for length in
                                       word_lengths}

    # Replace keys
    result = {secrets.choice(word_dict.get(
        len(k),
        ["".join([secrets.choice(key_chars) for _ in range(len(k))])]
    )): src[k] for k in src}

    # Add more key and values
    for i in range(secrets.randbelow(2) + 2):
        key = secrets.choice(word_dict[secrets.choice(list(word_lengths))])
        if len(key) in [len(k) for k in result.keys()]:
            continue

        result[key] = generate_random_value(word_dict)

    # Split string
    for k in result:
        if isinstance(result[k], str):
            while (split_str_num := u_split_str_num + secrets.randbelow(3) - 2) == 0:
                pass
            str_char_num_avg = len(result[k]) // split_str_num

            s = result[k]
            result[k] = [generate_random_value(word_dict, type_exclude=[int, bool, list])]
            while s != "":
                char_num = str_char_num_avg + secrets.randbelow(6) - 2

                if secrets.randbelow(2):
                    result[k].append(
                        generate_random_value(word_dict, max_random_int=default_max_random_int, type_exclude=[str]))

                result[k].append(s[:char_num])
                s = s[char_num:]
        elif isinstance(result[k], list):
            result[k] = [[generate_random_value(word_dict)]] + result[k]

    # Return
    return result


def WLER_deobfuscate(src: dict[str, Any], original_keys: list[str]) -> dict:
    # Define result
    original_key_lengths = [len(k) for k in original_keys]
    result = {original_keys[original_key_lengths.index(len(k))]: src[k] for k in src if len(k) in original_key_lengths}

    # Concat split strings
    for key in result:
        if isinstance(result[key], list):
            if isinstance(result[key][0], list):
                del result[key][0]
                continue
            elif isinstance(result[key][0], str):
                result[key] = "".join([split_str for split_str in result[key][1:] if isinstance(split_str, str)])

    # Return
    return result
