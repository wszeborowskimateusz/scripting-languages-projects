#include <iostream>
#include <fstream>
#include <vector>

const std::string DATA_SOURCE_FILE_PATH = "..\\..\\..\\DataSource\\data.txt";
const std::string DATA_DESTINATION_FILE_PATH = "..\\..\\..\\Output\\result_cpp.txt";

int absImpl(int x) {
	if (x < 0) {
		return -1 * x;
	}
	return x;
}

std::vector<int> readDataFile() {
	std::ifstream dataFile;
	dataFile.open(DATA_SOURCE_FILE_PATH);
	std::vector<int> data = std::vector<int>();
	char output[100];
	if (dataFile.is_open()) {
		int number;
		while (dataFile >> number) {
			data.push_back(number);
		}
	}
	dataFile.close();
	return data;
}

int main()
{
	std::vector<int> data = readDataFile();
	for (std::vector<int>::iterator it = data.begin(); it != data.end(); ++it) {
		std::cout << absImpl(*it) << std::endl;
	}
}
