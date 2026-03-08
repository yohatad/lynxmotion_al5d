#ifndef LYNXMOTION_AL5D_DESCRIPTION__BRICK_HPP_
#define LYNXMOTION_AL5D_DESCRIPTION__BRICK_HPP_

#include <string>
#include <memory>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "geometry_msgs/msg/point.hpp"
#include "geometry_msgs/msg/quaternion.hpp"
#include "gazebo_msgs/msg/model_states.hpp"
#include "gazebo_msgs/srv/set_model_state.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"
#include "lynxmotion_al5d_description/srv/teleport_absolute.hpp"
#include "lynxmotion_al5d_description/srv/teleport_relative.hpp"
#include "lynxmotion_al5d_description/msg/pose.hpp"

#define PUBLISH_FREQUENCY 10

typedef struct RPY
{
    double roll, pitch, yaw;
} RPY;

double degrees(double radians);
double radians(double degrees);
geometry_msgs::msg::Quaternion quaternionFromRPY(double roll, double pitch, double yaw);
RPY RPYFromQuaternion(geometry_msgs::msg::Quaternion quat);

class Brick : public rclcpp::Node
{
public:
    Brick(std::string _color, std::string _name, double _x = 0, double _y = 0, double _z = 0,
          double _roll = 0.00, double _pitch = 0.00, double _yaw = 0.00);
    ~Brick();

    std::string getColor();
    std::string getName();
    geometry_msgs::msg::Pose& getPose();
    void setPose(geometry_msgs::msg::Pose& _newPose);
    bool teleport(geometry_msgs::msg::Pose& pose);

private:
    void publishPose();
    void updatePose(const gazebo_msgs::msg::ModelStates::SharedPtr msg);
    bool teleportAbsolute(
        const std::shared_ptr<lynxmotion_al5d_description::srv::TeleportAbsolute::Request> req,
        std::shared_ptr<lynxmotion_al5d_description::srv::TeleportAbsolute::Response> res);
    bool teleportRelative(
        const std::shared_ptr<lynxmotion_al5d_description::srv::TeleportRelative::Request> req,
        std::shared_ptr<lynxmotion_al5d_description::srv::TeleportRelative::Response> res);

    std::string color;
    std::string name;
    geometry_msgs::msg::Pose pose_;
    
    rclcpp::Publisher<lynxmotion_al5d_description::msg::Pose>::SharedPtr pose_pub_;
    rclcpp::Subscription<gazebo_msgs::msg::ModelStates>::SharedPtr pose_sub_;
    rclcpp::Service<lynxmotion_al5d_description::srv::TeleportAbsolute>::SharedPtr teleport_absolute_srv_;
    rclcpp::Service<lynxmotion_al5d_description::srv::TeleportRelative>::SharedPtr teleport_relative_srv_;
    rclcpp::TimerBase::SharedPtr timer_;
};

#endif // LYNXMOTION_AL5D_DESCRIPTION__BRICK_HPP_