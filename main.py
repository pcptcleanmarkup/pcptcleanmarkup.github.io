from pyscript import document

ITEM_MAP = {
    "Processor": "CPU",
    "Motherboard": "Mobo",
    "Graphic Card": "GPU",
    "Power Supply": "PSU",
    "Cabinet": "Case",
    "Memory": "RAM",
    "Memory_2": "RAM2",
    "Hard drive": "HDD",
    "SSD drive": "SSD",
    "Additional Monitor": "Monitor2",
    "CPU Cooler": "Cooler",
    "Keyboard": "KBD",
    "Mouse": "MSE",
}

UNWANTED_WORDS = [
    'desktop', 'computer',
    'processor', 'lga', '1700', 'lga1700', 'lga1200',
    'cpu', 'air', 'cooler', 'socket',
    'geforce', 'radeon', 'graphics', 'graphic', 'card', 'gddr6', 'edition',
    'motherboard', 'amd', 'intel', 'nvidia',
    'ram', 'memory',
    'series', 'micro', 'atx', 'm-atx', 'tower', 'mini', 'mid-tower',
    'mini-tower', 'micro-tower', 'micro', 'case', 'full',
    'with', 'and', 'cabinet', 'tempered', 'glass', 'side', 'panel',
    'argb', 'rgb', 'controller',
    'power', 'supply', 'designer', 'fully',
    'smps', 'certified', 'certification', 'gaming',
    'internal', 'ssd', 'solid', 'state', 'drive',
    'hard', 'disk', 'surveillance', 'surveilance', '7200', '5400', 'rpm',
    'enterprise', 'industry', 'industrial', 'sata',
    'monitor', 'display', 'monitors', 'resolution', 'high',
    'keyboard', 'mouse', 'headset', 'headphone',
]

COMMON_WORD_REPLACMENTS = {
    'Cooler Master': 'CM',
    'Western Digital': 'WD',
    'Corsair Vengeance': 'Corsair',
    'HZ': 'Hz',
    ' INCH': '"',
    'INCH': '"',
    'NVME': 'NVMe'
}

def is_alphanumeric(string: str, min_numerals: int = 1) -> bool:
    """This function tells whether a string is alphanumeric."""

    letters = 0
    numbers = 0
    others = 0
    for i in string:
        if i.isalpha():
            letters += 1
        elif i.isnumeric():
            numbers += 1
        else:
            others += 1

    if numbers >= min_numerals:
        return True

    return False


def len_sans_symbols(string: str) -> int:
    """Returns the length of the string considering only alphanumeric characters"""
    return len([i for i in string if (i.isalpha() or i.isnumeric())])


def remove_brackets(string: str) -> str:
    """Removes all text within brackets from a string."""

    open_brackets = []
    close_brackets = []
    for i, j in enumerate(string):
        if j == '(':
            open_brackets.append(i)
        if j == ')':
            close_brackets.append(i)

    if len(open_brackets) != len(close_brackets):
        print("Failure")

    open_brackets.reverse()
    close_brackets.reverse()

    bracket_pairs = zip(open_brackets, close_brackets)
    for o, c in bracket_pairs:
        string = f"{string[:o].strip()} {string[c+1:].strip()}"

    return string


def smart_capitalize(string: str) -> str:
    """Smartly decides how to capitalize the given word"""

    if ' ' in string:
        raise ValueError("Argument contains spaces. Pass only one word at a time")

    symbols = './-'
    symbols_in_string = [(i, i in string) for i in symbols]

    for c, b in symbols_in_string:
        if b:
            string = c.join([smart_capitalize(i) for i in string.split(c)])

    if any(i[1] for i in symbols_in_string):
        return string

    vowels = 'aeiou'
    if len(string) < 5:
        vowel_count = sum(i in vowels for i in string)
        if vowel_count == 1 and (string[0] in vowels or string[-1] in vowels):
            new_string = string.upper()
        elif not vowel_count:
            new_string = string.upper()
        else:
            new_string = string.capitalize()
    elif is_alphanumeric(string):
        new_string = string.upper()
    else:
        new_string = string.capitalize()
    return new_string


def clean_markup(markup, repeat_ram=True, remove_source=False):
    rows = markup.split('\n')
    clean_rows = [i for i in rows if i]

    link = clean_rows[0]
    headers = clean_rows[1].split('|')
    headers[0] = 'Item'
    table = clean_rows[3:]

    config_dict = [dict(zip(headers, i.split('|'))) for i in table]
    config_dict = [i for i in config_dict if i['Selection'].strip()]

    config = []
    for i in config_dict:
        cur_dict = {}
        for k, v in i.items():
            cur_dict[k] = v.replace('**', '').strip()
        config.append(cur_dict)

    for i in config:
        item_pair = i['Selection'].split(']')
        item = remove_brackets(item_pair[0][1:].lower())
        item = ' '.join(i for i in item.split() if i not in UNWANTED_WORDS)

        ite = []
        for j in item.split():
            if len_sans_symbols(j) > 12 and is_alphanumeric(j):
                continue
            ite.append(smart_capitalize(j))
        item = ' '.join(ite)

        for k, v in COMMON_WORD_REPLACMENTS.items():
            item = item.replace(k, v)

        i['Selection'] = f"[{item}]{item_pair[1]}"
        i['Item'] = ITEM_MAP.get(i['Item'], i['Item'])
        i['Source'] = i['Source'].split()[0]

    if repeat_ram:
        ram_list = [(i, j) for i, j in enumerate(config) if j['Item']=='RAM']
        ram_dict = ram_list[0][1].copy()
        ram_dict['Item'] = 'RAM_2'
        config.insert(ram_list[0][0]+1, ram_dict)

    total_price = sum(int(i['Price']) for i in config)
    total_price_markup = f"**Total**|{'' if remove_source else '|'}|**{total_price}**"

    if remove_source:
        for i in config:
            del i['Source']

    pretty_markup = []
    keys = list(config[0].keys())
    pretty_markup.append('|'.join(keys))
    sep = '----|----|----' + ('|----' if not remove_source else '')
    pretty_markup.append(sep)
    for i in config:
        pretty_markup.append('|'.join(i.values()))

    pretty_markup.append(total_price_markup)
    config_table = link + '\n' + '\n'.join(pretty_markup)
    return config_table


def markup_cleaner(event):
    input_markup = document.querySelector("#markup")
    remove_source = document.querySelector("#remove-source").checked
    repeat_ram = document.querySelector("#repeat-ram").checked
    result = clean_markup(input_markup.value, remove_source=(remove_source), repeat_ram=repeat_ram)
    output_area = document.querySelector("#clean-markup-text")
    output_area.value = result
    output_div2 = document.querySelector("#clean-table")
    output_div2.innerHTML = '<md-block>' + result + '</md-block>'
    output_div2 = document.querySelector("#old-table")
    output_div2.innerHTML = '<md-block>' + input_markup.value + '</md-block>'