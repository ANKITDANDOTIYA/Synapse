// -> include/AudioHandler.h
#pragma once
#include <miniaudio.h>
#include <iostream>

// -> Forward declaration: NetworkHandler class ki existence batata hai 
// -> taaki unnecessary header files include na karni padein.
class NetworkHandler;

// -> AudioHandler class: Microphone se audio capture karne aur use NetworkHandler ke zariye stream karne ka kaam hai...
class AudioHandler {
public:
// -> Constructor: Variables ko default values pe set karta hai...
    AudioHandler();

// -> Destructor: Program band hone par resources (mic device) ko safe tarike se release karta hai.
    ~AudioHandler();

// -> Audio device ko setup karta hai aur use network handler se connect karta hai...
// -> network: NetworkHandler ka pointer jahan audio data bheja jayega...
// -> return: true agar initialization successful ho, warna false...
    bool init(NetworkHandler* network);

    bool startRecording();
    void stopRecording();

private:
    ma_device device; // -> Miniaudio ki core structure jo hardware (mic) ko represent karti hai...
    NetworkHandler* netHandler; // -> Pointer to network handler jahan audio data bheja jayega...
    bool isInitialized; // -> Audio device initialized hai ya nahi, taaki startRecording se pehle check kar sakein...
    bool isRecording; // -> Recording chal rahi hai ya nahi, taaki stopRecording sahi se kaam kare...
};