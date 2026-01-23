#include "main.h"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <thread>
#include <chrono>

#include "CameraHandler.hpp"
#include "NetworkHandler.h"
#include "AudioHandler.h"

using namespace std;

int main() {
    std::cout << "--- TRINETRA VISION: LIVE STREAMING MODE ---" << std::endl;

    // 1. Camera Init
    CameraHandler ch;
    if (!ch.initCamera(0)) return -1;

    // 2. NETWORK SETUP
    // Video Port (5555)
    NetworkHandler nh_video;
    nh_video.init("tcp://*:5555");

    // Audio Port (5556) - Dedicated for Audio Stream
    NetworkHandler nh_audio;
    nh_audio.init("tcp://*:5556");

    // 3. AUDIO SETUP
    AudioHandler audio;
    // Yahan hum nh_audio ka address (&) bhej rahe hain
    if (!audio.init(&nh_audio)) {
        return -1;
    }

    // Streaming shuru! (Ye background me chalta rahega)
    audio.startRecording();

    std::cout << "🚀 Streaming Video (5555) & Audio (5556)..." << std::endl;

    while (true) {
        // Video Processing Loop
        cv::Mat frame = ch.getFrame();
        if (frame.empty()) continue;

        nh_video.sendFrame(frame);
        cv::imshow("Trinetra", frame);

        if (cv::waitKey(1) == 27) break;
    }

    audio.stopRecording();
    return 0;
}