import time

DATA_SOURCE_FILE_PATH = "..\\DataSource\\data.txt"
DATA_DESTINATION_FILE_PATH = "..\\Output\\result_python_lib.txt"
NUMBER_OF_ITERATION = 20


def read_data_file():
    with open(DATA_SOURCE_FILE_PATH) as data_file:
        return [int(x) for x in data_file]


def save_result_to_file(result):
    with open(DATA_DESTINATION_FILE_PATH, 'w') as output_file:
        for number in result:
            output_file.write(str(number) + "\n")


def test_empty_loop(data):
    start = time.time()
    for i in range(NUMBER_OF_ITERATION):
        for _ in data:
            pass
    end = time.time()
    return end - start


def test_real_data(data):
    result = []
    start = time.time()
    for i in range(NUMBER_OF_ITERATION):
        for num in data:
            if i == (NUMBER_OF_ITERATION - 1):
                result.append(abs(num))
            else:
                abs(num)
    end = time.time()

    save_result_to_file(result)
    return end - start


def run_experiment():
    print("Starting experiment")
    data = read_data_file()
    empty_loop_time = test_empty_loop(data) * 1000
    real_data_time = test_real_data(data) * 1000
    empty_loop_one_iteration_time = empty_loop_time / NUMBER_OF_ITERATION
    real_data_average_time = real_data_time / NUMBER_OF_ITERATION

    experiment_time = empty_loop_time + real_data_time
    print("Experiment took", experiment_time, "ms")
    print("Average experiment time for", NUMBER_OF_ITERATION, "iteration is",
          real_data_average_time - empty_loop_one_iteration_time, "ms")

    print("Real data time", real_data_time, "ms, Empty loop time", empty_loop_time, "ms")
    print("Experiment finished")


if __name__ == "__main__":
    run_experiment()
