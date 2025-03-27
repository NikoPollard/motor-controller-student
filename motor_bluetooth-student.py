import time
import board
import pwmio
import io
from adafruit_motor import motor


# see the file ew_uart.py
# I abstracted the bluetooth connection pieces
# to make this file cleaner -- you will want to do this
# as our code gets more complex
import ew_uart as ua
ua.setup("Niko UART")


# be sure your motor controller is connected to the
# correct pins
PWM_PIN_A1 = board.D10  # pick any pwm pins on their own channels
PWM_PIN_A2 = board.D9
PWM_PIN_B1 = board.D7  # pick any pwm pins on their own channels
PWM_PIN_B2 = board.D8

# DC motor setup
pwm_a1 = pwmio.PWMOut(PWM_PIN_A1, frequency=50)
pwm_a2 = pwmio.PWMOut(PWM_PIN_A2, frequency=50)
motor1 = motor.DCMotor(pwm_a1, pwm_a2)

pwm_b1 = pwmio.PWMOut(PWM_PIN_B1, frequency=50)
pwm_b2 = pwmio.PWMOut(PWM_PIN_B2, frequency=50)
motor2 = motor.DCMotor(pwm_b1, pwm_b2)

motor1.throttle = 0.0
motor2.throttle = 0.0
print("-- throttle:", motor1.throttle)
# Motor specs (Adjust for your motor)
# at 5V from Battery --> 3.8V at motor --> ~140 RPM
MAX_RPM = 140  # Motor's max RPM at 100% duty cycle


# Function to get estimated RPM
# return the duty_cycle divided by 65535 times the max_rpm
def get_estimated_rpm(duty_cycle):
    return (duty_cycle/65535)*MAX_RPM

# return a list of rpm of each motor --
# depending on the direction of the motor
# two of these will always be zero
def get_all_rpm():
    return [
        get_estimated_rpm(pwm_a1.duty_cycle),
        get_estimated_rpm(pwm_b1.duty_cycle),
    ]

# write all the rpms -- a1, a2, b1, b2
def write_rpms(rpms):
    msg = f"a1: {rpms[0]:.2f}; "
    msg += f"a2: {rpms[1]:.2f}\n"
    ua.write(msg)

# This mehtod is passed the amount of increase(which could be negative)
# for each motor
# Steps:
#  1. Determine the potential change on eahc motor
#  2. For each motor, Be sure the potential change is between 0 and 1 
#  3. For each motor, change the throttle value by the appropriate parameter
def handle_throttle(mtr1_increase, mtr2_increase):
    if motor1.throttle == None: motor1.throttle = 0
    if motor2.throttle == None: motor2.throttle = 0
    mtr1_pot_change = motor1.throttle + mtr1_increase
    mtr2_pot_change = motor2.throttle + mtr2_increase
    if mtr1_pot_change > 1: mtr1_pot_change = 1
    elif mtr1_pot_change < -1: mtr1_pot_change = -1
    if mtr2_pot_change > 1: mtr2_pot_change = 1
    elif mtr2_pot_change < -1: mtr2_pot_change = -1
    motor1.throttle = mtr1_pot_change
    motor2.throttle = mtr2_pot_change

# set your throttles to zero
def stop():
    motor1.throttle = 0
    motor2.throttle = 0

def coast():
    motor1.throttle = None
    motor2.throttle = None

counter = 0
while True:
    ua.connect()
    while ua.connected():
        counter += 1

        if counter % 50000 == 0:
            write_rpms(get_all_rpm())
        
        if ua.in_waiting():
            data = ua.read(ua.in_waiting())
            if data:
                text = data.decode("utf-8").strip()
                print("Text Sent: ", text)
                button = ua.button_press(data)
                if button == "UP":
                    handle_throttle(0.1, 0.1)
                    continue
                elif button == "DOWN":
                    handle_throttle(-0.1, -0.1)
                    continue
                elif button == "LEFT":
                    handle_throttle(0.1, -0.1)
                    continue
                elif button == "RIGHT":
                    handle_throttle(-0.1, 0.1)
                    continue
                elif button == "1":
                    stop()
                    continue
                elif button == "2":
                    coast()
                    continue
                # w go faster, s slow down, a left motor increase,
                # d right motor increase, r stop
                if text and text == "w":
                    handle_throttle(0.1, 0.1)
                elif text and text == "ww":
                    handle_throttle(2, 2)
                elif text and text == "ss":
                    handle_throttle(-2, -2)
                elif text and text == "s":
                    handle_throttle(-0.1, -0.1)
                elif text and text == "a":
                    handle_throttle(0.1, -0.1)
                elif text and text == "aa":
                    handle_throttle(2, -2)
                elif text and text == "d":
                    handle_throttle(-0.1, 0.1)
                elif text and text == "dd":
                    handle_throttle(-2, 2)
                elif text and text == "c":
                    coast()
                elif text and text == "r":
                    stop()
                write_rpms(get_all_rpm())
