import os
from gpiozero import Button, DigitalOutputDevice
from time import sleep

# GPIO setup
hall_sensor_1 = Button(2)  # Hall Effect Sensor for Motor 1 connected to GPIO2
hall_sensor_2 = Button(3)  # Hall Effect Sensor for Motor 2 connected to GPIO3

# Define GPIO pins for Motor 1
PUL_PIN_1 = 22
DIR_PIN_1 = 27

# Define GPIO pins for Motor 2
PUL_PIN_2 = 23
DIR_PIN_2 = 24

# Step delay in seconds
STEP_DELAY = 0.001  # Adjust as needed
DEBOUNCE_DELAY = 0.1  # Adjust debounce delay if necessary
delayBeforeHome = 1  # Delay before homing in seconds

# Set homeSteps for both motors
homeSteps = 150  # Number of steps to move Motor 1 to "home"
homeSteps2 = 350  # Number of steps to move Motor 2 to "home"

# Initialize GPIO devices for Motor 1
pulse_1 = DigitalOutputDevice(PUL_PIN_1)
direction_1 = DigitalOutputDevice(DIR_PIN_1)

# Initialize GPIO devices for Motor 2
pulse_2 = DigitalOutputDevice(PUL_PIN_2)
direction_2 = DigitalOutputDevice(DIR_PIN_2)

def start_camera_stream():
    """
    Start the MJPEG stream for live camera streaming.
    """
    print("Starting live camera stream...")
    os.system("mjpg_streamer -i \"/usr/local/lib/mjpg-streamer/input_uvc.so -d /dev/video0 -r 1280x720 -f 60\" -o \"/usr/local/lib/mjpg-streamer/output_http.so -w /usr/local/share/mjpg-streamer/www\" &")

def move_to_home(motor_pulse, motor_dir, steps, step_delay):
    """
    Move the motor a specific number of steps after delay.
    
    Args:
    motor_pulse: GPIO pin controlling motor pulse
    motor_dir: GPIO pin controlling motor direction
    steps: Number of steps to move
    step_delay: Delay between steps
    """
    print(f"Moving motor to home position for {steps} steps...")
    
    for _ in range(steps):
        motor_pulse.on()
        sleep(step_delay)
        motor_pulse.off()
        sleep(step_delay)
    
    print("Motor has reached the home position.")
    motor_pulse.off()

def spin_motor_until_sensor(motor_pulse, motor_dir, hall_sensor, home_steps, reverse_direction=False):
    """
    Spin the motor until the associated Hall sensor is triggered, then move it to home.
    
    Args:
    motor_pulse: GPIO pin controlling motor pulse
    motor_dir: GPIO pin controlling motor direction
    hall_sensor: GPIO pin connected to the Hall sensor
    home_steps: Number of steps to move the motor to home
    reverse_direction: If True, reverse the direction for homing
    """
    print("Spinning motor...")
    motor_dir.on()  # Set direction for spinning (CW for Motor 1)

    while not hall_sensor.is_pressed:
        motor_pulse.on()
        sleep(STEP_DELAY)
        motor_pulse.off()
        sleep(STEP_DELAY)

    # Motor has reached the sensor, stop the motor
    motor_pulse.off()
    sleep(DEBOUNCE_DELAY)  # Debounce delay to ensure stability

    print("Hall sensor triggered, stopping motor.")
    sleep(delayBeforeHome)  # Add the delay before moving to home

    if reverse_direction:
        motor_dir.off()  # Reverse direction (CCW for Motor 1)
    
    move_to_home(motor_pulse, motor_dir, home_steps, STEP_DELAY)

# Keep the program running
try:
    print("Starting Motor 1...")
    spin_motor_until_sensor(pulse_1, direction_1, hall_sensor_1, homeSteps, reverse_direction=True)  # Motor 1 with reversed direction (CCW)

    print("Starting Motor 2...")
    spin_motor_until_sensor(pulse_2, direction_2, hall_sensor_2, homeSteps2)  # Motor 2 with default direction
    
    print("Live stream starting...")
    print("URL: http://miror.local:8080/?action=stream")
    start_camera_stream()

except KeyboardInterrupt:
    print("Execution interrupted, cleaning up GPIO...")

finally:
    # Clean up GPIO resources
    pulse_1.off()
    pulse_2.off()
    direction_1.close()
    direction_2.close()
    pulse_1.close()
    pulse_2.close()
