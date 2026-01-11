

#include "main.h"
#include <opencv2/opencv.hpp>
#include "CameraHandler.hpp"
#include "NetworkHandler.h"
#include <iostream>
using namespace std;
int main()
{
	CameraHandler ch;
	if (!ch.initCamera(0)) {
		std::cerr << "Ghatak Error: Camera nahi mil raha!" << std::endl;
		return -1;
	}

	std :: cout << "Handler opened the camera" << endl;
	NetworkHandler nh;
	nh.init("tcp://*5555");

	while (true) {
		
		cv::Mat frame = ch.getFrame();
		if (frame.empty()) {
			std::cerr << "Frames are empty skippking frames" << endl;
			continue;
		}
		
		nh.sendFrame(frame);


		cv::imshow("Window", frame);
		if (cv::waitKey(30) == 27) {
			break;
		}
		
	}
}
