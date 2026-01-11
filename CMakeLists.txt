cmake_minimum_required(VERSION 3.15)
project(Trinetra_Vision)

# 1. Header files ka folder (Aapke screenshot mein 'include' folder hai)
include_directories(include)


set(SOURCES 
    src/main.cpp   
    src/CameraHandler.cpp
    include/NetworkHandler.h
    include/CameraHandler.hpp
)  

# 3. Libraries dhoondo
find_package(OpenCV REQUIRED)
find_package(cppzmq CONFIG REQUIRED)

# 4. Executable banao
add_executable(${PROJECT_NAME} ${SOURCES})

# 5. Link karo
target_link_libraries(${PROJECT_NAME} PRIVATE ${OpenCV_LIBS} cppzmq)