import os

path = r"C:\\Users\\user\\Desktop\\Сайт\\static\\txt\\Партийная организация и партийная литература\\Партийная организация и партийная литература.txt"

def update_txt(path):
    if os.path.exists(path) and path.split("\\")[-1].endswith(".txt"):
        update_text = "" ##Улучшенный текст

        with open(path, "r") as file:
            i = 1
            text = file.read()

            for j in range(len(text)):
                if text[j] == "\n" and text[j-1] == "\n" and text[j+1] != "\n":
                    if i % 2 != 0:
                        update_text += "<p>"
                        i += 1
                    elif i % 2 == 0:
                        update_text += "</p>\n<p>"
                        i += 2

                update_text += text[j]
            print(update_text)
            
        with open(path, "w") as file:
            file.write(update_text)
        

update_txt(path)

def update_creation_name(creation_name):

    creation_name_updated = ""

    for letter in creation_name:
        if letter == "?":
            continue
        creation_name_updated += letter

    return creation_name_updated
