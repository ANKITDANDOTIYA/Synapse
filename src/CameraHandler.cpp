#include "CameraHandler.hpp"

// Constructor
CameraHandler::CameraHandler() {
    // Yahan initialization hoti hai
}

bool CameraHandler::initCamera(int id) {
    return cap.open(id); // Ab ye 'cap' ko pehchan lega
}

cv::Mat CameraHandler::getFrame() {
    cv::Mat frame;
    cap >> frame; // Camera se frame nikaal kar frame Mat mein daalna
    return frame;
}