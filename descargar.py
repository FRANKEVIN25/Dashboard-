from urllib import request


def descargar():
    file = open("enlaces.txt", "r")
    counter = 0
    word = ""
    for line in file:
        for letter in line:
            if letter != " " and letter != "\n" and letter != "\t":
                word = word + letter
            else:
                request.urlretrieve(word, str(2012 + counter)+"-Gastos.csv")
                print("Descargado " + str(2012 + counter)+"-Gastos.csv")
                word = ""
                counter += 1