cmake_minimum_required(VERSION 3.15)

project(Trinetra_Vision)

# 1. Include directory setup
include_directories(include)

# 2. Libraries dhoondo
find_package(OpenCV REQUIRED)
find_package(cppzmq CONFIG REQUIRED)

# --- MINIAUDIO SETUP ---
# Ab vcpkg.json ki wajah se file wahan exist karegi
find_path(MINIAUDIO_PATH NAMES miniaudio.h REQUIRED)

if(MINIAUDIO_PATH)
    message(STATUS "✅ Miniaudio found at: ${MINIAUDIO_PATH}")
    include_directories(${MINIAUDIO_PATH})
else()
    message(FATAL_ERROR "❌ Miniaudio nahi mila! 'vcpkg.json' check karein.")
endif()

# 3. Source Files List
set(SOURCES 
    src/main.cpp   
    src/CameraHandler.cpp 
    src/NetworkHandler.cpp
    src/AudioHandler.cpp
    include/NetworkHandler.h     
    include/CameraHandler.hpp
    include/AudioHandler.h
)

# 4. Executable banao
add_executable(${PROJECT_NAME} ${SOURCES})

# 5. Link karo
target_link_libraries(${PROJECT_NAME} PRIVATE ${OpenCV_LIBS} cppzmq)