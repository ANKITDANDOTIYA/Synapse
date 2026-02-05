#define MINIAUDIO_IMPLEMENTATION
#include "../include/AudioHandler.h"
#include "../include/NetworkHandler.h" // -> NetworkHandler include karna zaroori hai
#include <iostream>

// -> GLOBAL CALLBACK (Important for audio engine)
// -> Yeh function tab chalta hai jab microphone ke paas naya data aata hai
// -> pDevice: Audio device ka pointer (miniaudio se aata hai)..
// -> pOutput: Output buffer (hamare case mein use nahi karenge kyunki hum capture kar rahe hain)
// -> pInput: Input buffer jahan mic data aata hai...
// -> frameCount: Number of audio frames (samples) jo is callback mein process ho rahe hain...
// -> Is callback ka main kaam hai mic se data lena aur use NetworkHandler ke zariye stream karna...
// -> Ab ye encoder nahi, balki NetworkHandler use karega..
void data_callback(ma_device* pDevice, void* pOutput, const void* pInput, ma_uint32 frameCount) {
//-> pDevice->pUserData wahi pointer hai jo humne init() mein set kiya tha (NetworkHandler)....
//-> Isse callback ko pata chalta hai ki data kahan bhejna hai.....
    NetworkHandler* net = (NetworkHandler*)pDevice->pUserData;

    if (net == NULL) return;

    // Data Size Calculation:
    // FrameCount * Channels (1) * SizeOfFloat (4 bytes)
    size_t dataSize = frameCount * 1 * sizeof(float);

    // -> Audio data ko seedha server ki taraf stream kar do bina delay ke.....
    net->sendAudioChunk(pInput, dataSize);
}


// -> Connstructor: Initial flags ko false rakhte hain jab tak setup na ho jaye....
AudioHandler::AudioHandler() : isInitialized(false), isRecording(false), netHandler(nullptr) {
}

// -> Destructor: Stop recording agar chal rahi ho aur device ko uninitialize kar do...
// -> Program band hote waqt memory saaf karna zaroori hai.
AudioHandler::~AudioHandler() {
    stopRecording();
    if (isInitialized) {
        ma_device_uninit(&device); // -> Mic ka hardware se link tod do, taaki resources free ho jayein...
    }
}

// -> Init function: NetworkHandler ka pointer lete hain taaki callback mein use kar sakein...
// -> Hardware (Mic) aur Software (Network) ko jodne wala bridge...
bool AudioHandler::init(NetworkHandler* network) {
    this->netHandler = network; // Store pointer

    ma_device_config deviceConfig;

    // Microphone Setup
    deviceConfig = ma_device_config_init(ma_device_type_capture);
    deviceConfig.capture.format = ma_format_f32; // Float 32 (Standard for AI)
    deviceConfig.capture.channels = 1;             // Mono
    deviceConfig.sampleRate = 44100;         // 44.1 kHz
    deviceConfig.dataCallback = data_callback; // dataCallback: Yeh woh function hai jo har bar tab call hoga jab mic mein awaaz aayegi

    // CRITICAL: Callback ko NetworkHandler pass kar rahe hain
    // Callback function class ke bahar hota hai, isliye use 'this' pointer ya 
    // network pointer ka access dene ke liye pUserData ka istemal hota hai.
    deviceConfig.pUserData = this->netHandler;

    // -> Hardware Initialization: NULL ka matlab hai 'Default System Microphone' use karo...
    if (ma_device_init(NULL, &deviceConfig, &device) != MA_SUCCESS) {
        std::cerr << "❌ AudioHandler: Mic open nahi ho raha!" << std::endl;
        return false;
    }

    isInitialized = true; // State update: System ab ready hai mic se awaaz capture karne ke liye...
    return true;
}

// Yeh mic ki 'Power' on karta hai. Iske baad hi data_callback call hona shuru hota hai...
bool AudioHandler::startRecording() {
    //->  Basic checks: Bina init kiye start nahi kar sakte...
    //-> Agar already recording chal rahi hai to dobara start karne ki zaroorat nahi...
    if (!isInitialized) return false;
    if (isRecording) return true;

    // -> ma_device_start: Mic ko active mode mein dalta hai, jisse data_callback chalna shuru ho jata hai jab mic mein awaaz aati hai...
    if (ma_device_start(&device) != MA_SUCCESS) {
        std::cerr << "❌ AudioHandler: Start fail!" << std::endl;
        return false;
    }

    isRecording = true;
    std::cout << "🎙️ Audio Streaming Started (Live)..." << std::endl;
    return true;
}

// Stop recording: Mic ko 'Power Off' karta hai, jisse data_callback band ho jata hai...
// -> Yeh mic ki streaming rok deta hai par connection khatam nahi karta...
void AudioHandler::stopRecording() {
    // Agar device initialized nahi hai ya recording pehle se band hai, toh kuch mat karo...
    if (!isInitialized || !isRecording) return;

    // -> ma_device_stop: Mic hardware ko 'Sleep' mode mein dalta hai...
    ma_device_stop(&device);
    isRecording = false;
    std::cout << "🛑 Audio Streaming Stopped." << std::endl;
}