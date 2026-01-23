// include/AudioHandler.h
#pragma once
#include <miniaudio.h>
#include <iostream>

// Forward declaration taaki circular dependency na ho
class NetworkHandler;

class AudioHandler {
public:
    AudioHandler();
    ~AudioHandler();

    // Ab hum file name nahi, Network Object lenge
    bool init(NetworkHandler* network);

    bool startRecording();
    void stopRecording();

private:
    ma_device device;
    NetworkHandler* netHandler; // Pointer to network
    bool isInitialized;
    bool isRecording;
};