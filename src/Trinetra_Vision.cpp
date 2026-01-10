// Trinetra_Vision.cpp : Defines the entry point for the application.
//

#include "Trinetra_Vision.h"
#include <opencv2/opencv.hpp>
#include <CameraHandler.hpp>

using namespace std;

int main()
{
	CameraHandler handler;
	if (!handler.initCamera(0)) {
		std::cerr << "Ghatak Error: Camera nahi mil raha!" << std::endl;
		return -1;
	}

	std :: cout << "Handler opened the camera" << endl;

	while (true) {
		if (cv::waitKey(30) == 27) {
			break;
		}
		cv::Mat frame = handler.getFrame();
		if (frame.empty()) {
			std::cerr << "Frames are empty()" << endl;
		}
		cv::imshow("Window", frame);
	}
}
