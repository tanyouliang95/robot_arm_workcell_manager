/*
 * Fiducial Markers Handler
 * Author: Tan You Liang
 */

#ifndef __FIDUCIAL_MARKERS_HANDLER_HPP__
#define __FIDUCIAL_MARKERS_HANDLER_HPP__

#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <yaml-cpp/yaml.h>

// ros stuffs
#include <ros/ros.h>
#include <geometry_msgs/Pose.h>
#include <tf/transform_broadcaster.h>
#include <tf/transform_listener.h>

// dependecies
#include <fiducial_msgs/FiducialTransformArray.h>


class FiducialMarkersHandler{

    public:
        FiducialMarkersHandler();
        
        ~FiducialMarkersHandler();

        // ------ Execution -----

        bool getTransformPose(std::string target_frame_id, std::string frame_id, tf::Transform *target_transform = new tf::Transform);
        
        // Set target marker and generate extended tf; @return: Marker's Type
        std::string setTargetMarker(std::string marker_id);

        bool removeTargetMarker();

        // TODO
        bool getAllSpottedMarkersID();
    
    protected:

        bool loadParameters();

        tf::Quaternion reorientateMarker(tf::Quaternion quat);

        // TODO: to work on this
        // To make sure tf transform will not be depreciated?? or another method to change this.... 10s for tf now
        // void republishTfHandler(); // keep markers tf alive

    private:
        std::string marker_type; // TBC

        std::vector<tf::StampedTransform> markers_extended_tf_array_;
        
        // param
        YAML::Node MARKERS_TF_CONFIG_;
        std::string camera_frame_id_;
        bool is_marker_flipped_;

        // ros stuffs
        ros::NodeHandle nh_;
        ros::Subscriber markers_sub_;
        tf::TransformBroadcaster tf_broadcaster_;  
        tf::TransformListener tf_listener_;
        ros::Timer marker_extended_tf_timer_;
        std::string tf_prefix_;

        void updateFiducialArrayCallback(const fiducial_msgs::FiducialTransformArrayConstPtr& msg);        

        void MarkerExtendedTfTimerCallback(const ros::TimerEvent& event);

};

#endif
