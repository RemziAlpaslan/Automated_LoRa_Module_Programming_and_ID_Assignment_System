# Automated LoRa Module Programming and ID Assignment System
This project is an automated system designed for burning firmware and assigning unique IDs to the LoRa modules on multiple electronic boards. A pen plotter was modified to create a precise and repeatable motion system that moves to specific locations, aligns with the target LoRa module, and performs the programming operations.

## Features
### Automated Programming:

Uploads firmware (burn) and assigns unique ID codes to each LoRa module without manual intervention.

### Pen Plotter Modification:

A standard pen plotter was customized to move to exact positions over the boards.

Upon reaching a target location, a servo lowers the programming head onto the LoRa module.

### Precise Movement System:

V-Slot chassis and wheels for smooth and accurate X-Y-Z motion.

Stepper motors and servo motors controlled by Arduino ensure accurate positioning and contact.

### Mass Production Ready:

Designed to handle multiple boards in sequence, reducing programming time and increasing reliability.

## Hardware Used
Arduino Board

Stepper Motors

Servo Motors

Stepper Motor Driver Shield

Modified Pen Plotter Mechanics

3D Printer Components (e.g., brackets, couplers)

V-Slot Aluminum Profiles and Wheels

## Project Overview
The system works by:

Moving to a predefined position on the board using stepper motors.

Lowering the programming tool with a servo to make contact with the LoRa module.

Uploading the firmware and assigning the ID automatically.

Moving to the next module to repeat the process.

This ensures high efficiency, consistency, and minimizes human errors during production.

## Future Improvements
Adding a camera system for vision-based alignment.

Integration with database systems to log programmed IDs automatically.

Dynamic board mapping to adapt to different PCB layouts.
