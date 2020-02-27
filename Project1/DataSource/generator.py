import random

start = -2147483648
stop = 2147483647
limit = 100000

randomListOfIntegers = [random.randint(start, stop) for _ in range(limit)]

with open("data.txt", "w") as txt_file:
    for number in randomListOfIntegers:
        txt_file.write(str(number) + "\n")
