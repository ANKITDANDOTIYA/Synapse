#include <zmq.hpp>
#include <opencv2/opencv.hpp>
class NetworkHandler {

private:
    zmq::context_t context; // ZMQ ka engine
    zmq::socket_t publisher; // socket jo data bhejega
public:
    NetworkHandler();
    void init(std::string protocol);
	void sendFrame(cv::Mat &frame);

};
