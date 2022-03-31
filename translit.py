def translit(text):
    translit_dict = {
        "а":"a",
        "б":"b",
        "в":"v",
        "г":"g",
        "д":"d",
        "е":"e",
        "ё":"yo",
        "ж":"zh",
        "з":"z",
        "и":"i",
        "й":"y",
        "к":"k",
        "л":"l",
        "м":"m",
        "н":"n",
        "о":"o",
        "п":"p",
        "р":"r",
        "с":"s",
        "т":"t",
        "у":"u",
        "ф":"f",
        "х":"h",
        "ц":"c",
        "ч":"ch",
        "ш":"sh",
        "щ":"sch",
        "ъ":"'",
        "ы":"i",
        "ь":"'",
        "э":"e",
        "ю":"yu",
        "я":"ya",
        " ":"_"
    }

    text = text.lower()
    new_text = ""
    for i in text:
        if i not in translit_dict:
            new_text += i
        else:
            new_text += translit_dict[i]

    return new_text
