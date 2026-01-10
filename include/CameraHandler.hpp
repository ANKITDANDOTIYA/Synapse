#pragma once
#include <opencv2/opencv.hpp>

class CameraHandler {
public:
    CameraHandler();            // Constructor
    bool initCamera(int id);    // Method declaration
    cv::Mat getFrame();         // Method declaration

private:
    cv::VideoCapture cap;       // Ye hai wo object jo aap access karna chahte ho
};