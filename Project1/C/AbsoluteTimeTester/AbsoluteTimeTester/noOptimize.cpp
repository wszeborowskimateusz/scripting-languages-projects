#include "noOptimize.h"

int donotoptimize(float f) {
	if (f == 5) {
		return static_cast<int>(5.0);
	}
	return static_cast<int>(f);
}