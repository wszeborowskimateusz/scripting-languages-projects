﻿#include <iostream>
#include <fstream>
#include <vector>
#include <chrono> 
#include <Windows.h>
using namespace std::chrono;

const std::string DATA_SOURCE_FILE_PATH = "..\\..\\..\\DataSource\\data.txt";
const std::string DATA_DESTINATION_FILE_PATH = "..\\..\\..\\Output\\result_cpp.txt";
const int NUMBER_OF_ITERATION = 100000000;

int absImpl(int x);
std::vector<int> readDataFile();
void saveResultsToFile(std::vector<int>);
void performExperiment();
long testEmptyLoop();
long testRealData();

int main() {
	performExperiment();

	return 0;
}

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
	if (dataFile.is_open()) {
		int number;
		while (dataFile >> number) {
			data.push_back(number);
		}
	}
	dataFile.close();
	return data;
}

 void saveResultsToFile(std::vector<int> result) {
	std::ofstream dataFile;
	dataFile.open(DATA_DESTINATION_FILE_PATH);
	if (dataFile.is_open()) {
		for (std::vector<int>::iterator it = result.begin(); it != result.end(); ++it) {	
			dataFile << (*it) << "\n";
		}
	}
	dataFile.close();
}

void performExperiment() {
	std::cout << "Starting experiment: " << std::endl;
	long emptyLoopTime = testEmptyLoop();
	double emptyLoopOneIterationTime = ((double)emptyLoopTime) / NUMBER_OF_ITERATION;
	long realDataTime = testRealData();
	double realDataAverageTime = ((double)realDataTime) / NUMBER_OF_ITERATION;
	long experimentTime = emptyLoopTime + realDataTime;


	std::cout << "Experiment took " << experimentTime << "ms (" << experimentTime / 1000.0 << "s)" << std::endl;
	std::cout << "Average experiment time from "<< NUMBER_OF_ITERATION <<" interations: " << realDataAverageTime - emptyLoopOneIterationTime << "ms" <<std::endl;
}

void donotoptimize() {}

long testEmptyLoop() {
	auto start = high_resolution_clock::now();
	//TODO: Perform operation - fake loop - 
	for (int i = 0; i < NUMBER_OF_ITERATION; i++) { donotoptimize(); }
	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop - start);

	return duration.count();
}

long testRealData() {
	std::vector<int> data = readDataFile();
	std::vector<int> result = std::vector<int>();
	auto start = high_resolution_clock::now();
	for (int i = 0; i < NUMBER_OF_ITERATION; i++) {
		for (std::vector<int>::iterator it = data.begin(); it != data.end(); ++it) {
			if (i == NUMBER_OF_ITERATION - 1) {
				result.push_back(absImpl(*it));
			} else {
				absImpl(*it);
			}
			
		}
	}

	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop - start);

	saveResultsToFile(result);

	return duration.count();
}
