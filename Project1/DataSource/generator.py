import random

start = -2147483647
stop = 2147483647
limit = 100000000

random_list_of_integer = [random.randint(start, stop) for _ in range(limit)]

with open("data.txt", "w") as txt_file:
    for number in random_list_of_integer:
        txt_file.write(str(number) + "\n")
