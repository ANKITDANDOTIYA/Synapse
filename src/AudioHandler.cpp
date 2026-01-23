#define MINIAUDIO_IMPLEMENTATION
#include "../include/AudioHandler.h"
#include "../include/NetworkHandler.h" // NetworkHandler include karna zaroori hai
#include <iostream>

// --- GLOBAL CALLBACK (UPDATED) ---
// Ab ye encoder nahi, balki NetworkHandler use karega
void data_callback(ma_device* pDevice, void* pOutput, const void* pInput, ma_uint32 frameCount) {
    // UserData se NetworkHandler nikalo
    NetworkHandler* net = (NetworkHandler*)pDevice->pUserData;

    if (net == NULL) return;

    // Data Size Calculation:
    // FrameCount * Channels (1) * SizeOfFloat (4 bytes)
    size_t dataSize = frameCount * 1 * sizeof(float);

    // Seedha Network par fenk do!
    net->sendAudioChunk(pInput, dataSize);
}

// --- CONSTRUCTOR ---
AudioHandler::AudioHandler() : isInitialized(false), isRecording(false), netHandler(nullptr) {
}

// --- DESTRUCTOR ---
AudioHandler::~AudioHandler() {
    stopRecording();
    if (isInitialized) {
        ma_device_uninit(&device);
    }
}

// --- INIT (UPDATED) ---
// Ab filename nahi, NetworkHandler chahiye
bool AudioHandler::init(NetworkHandler* network) {
    this->netHandler = network; // Store pointer

    ma_device_config deviceConfig;

    // Microphone Setup
    deviceConfig = ma_device_config_init(ma_device_type_capture);
    deviceConfig.capture.format = ma_format_f32; // Float 32 (Standard for AI)
    deviceConfig.capture.channels = 1;             // Mono
    deviceConfig.sampleRate = 44100;         // 44.1 kHz
    deviceConfig.dataCallback = data_callback;

    // CRITICAL: Callback ko NetworkHandler pass kar rahe hain
    deviceConfig.pUserData = this->netHandler;

    if (ma_device_init(NULL, &deviceConfig, &device) != MA_SUCCESS) {
        std::cerr << "❌ AudioHandler: Mic open nahi ho raha!" << std::endl;
        return false;
    }

    isInitialized = true;
    return true;
}

// --- START ---
bool AudioHandler::startRecording() {
    if (!isInitialized) return false;
    if (isRecording) return true;

    if (ma_device_start(&device) != MA_SUCCESS) {
        std::cerr << "❌ AudioHandler: Start fail!" << std::endl;
        return false;
    }

    isRecording = true;
    std::cout << "🎙️ Audio Streaming Started (Live)..." << std::endl;
    return true;
}

// --- STOP ---
void AudioHandler::stopRecording() {
    if (!isInitialized || !isRecording) return;
    ma_device_stop(&device);
    isRecording = false;
    std::cout << "🛑 Audio Streaming Stopped." << std::endl;
}