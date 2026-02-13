import plasma
import machine
import utime
from pimoroni import RGBLED, Button

# Led-nauhan pituus
NUM_LEDS = 50

# Ajastimen pituudet minuuteissa
#WORK_MINS = 25
#BREAK_MINS = 5

# Ajastimen pituudet testaamista varten
WORK_SECS = 0.5 * 60
BREAK_SECS = 0.1 * 60

# Värit (Hue, Saturation, Value)
# Hue välillä 0.0 - 1.0 (0 = punainen, 0.33 = vihreä, 0.66 = sininen)
# Saturation ja Value myös välillä 0.0 - 1.0
COLOR_WORK = (0.33, 1.0, 0.8)
COLOR_BREAK = (0.0, 1.0, 0.8)
COLOR_FLASH = (0.66, 1.0, 1.0)

led_strip = plasma.WS2812(NUM_LEDS)

user_sw = Button("USER_SW", repeat_time=0)
button_a = Button("BUTTON_A", repeat_time=0)
try:
    # Button B is only available on Plasma 2040
    button_b = Button("BUTTON_B", repeat_time=0)
except ValueError:
    button_b = None
led = RGBLED("LED_R", "LED_G", "LED_B")
    
state = "idle"
start_time = 0
last_button_press = 0

def clear_strip():
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i, 0, 0, 0)
        
def flash(h, s, v, times=3, delay=0.1):
    for _ in range(times):
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, h, s, v)
        utime.sleep(delay)
        clear_strip()
        utime.sleep(delay)
        
led_strip.start()

clear_strip()
print("Pomodoro-ajastin valmiina. Paina nappia A aloittaaksesi ajastimen")

while True:
    current_time = utime.ticks_ms()
    
    if button_a.read():
        if state == "work" or state == "break":
            state = "idle"
            clear_strip()
            print("Ajastin nollattu.")
            
        elif state == "idle":
            state = "work"
            start_time = current_time
            print(f"Aloitetaan {WORK_SECS / 60} minuutin työjakso")
        
    if button_b.read():
        # Toggle test mode and real pomodoro timer
        if WORK_SECS == 25 * 60:
            WORK_SECS = 0.5 * 60
            BREAK_SECS = 0.1 * 60
            led.set_rgb(0, 255, 0)
        else:
            WORK_SECS = 25 * 60
            BREAK_SECS = 5 * 60
            led.set_rgb(255, 0, 0)
            
    if state == "work":
        elapsed_time_secs = utime.ticks_diff(current_time, start_time) / 1000
        leds_to_light = int((elapsed_time_secs / WORK_SECS) * NUM_LEDS) + 1
        
        for i in range(NUM_LEDS):
            if i < leds_to_light:
                led_strip.set_hsv(i, *COLOR_WORK)
            else:
                led_strip.set_rgb(i, 0, 0, 0)
                
        if elapsed_time_secs >= WORK_SECS:
            state = "break"
            start_time = current_time
            print(f"Aloitetaan {BREAK_SECS / 60} minuutin tauko")
            flash(*COLOR_FLASH)
            
    elif state == "break":
        elapsed_time_secs = utime.ticks_diff(current_time, start_time) / 1000
        
        leds_to_keep_lit = NUM_LEDS - int((elapsed_time_secs / BREAK_SECS) * NUM_LEDS)
        
        for i in range(NUM_LEDS):
            if i < leds_to_keep_lit:
                led_strip.set_hsv(i, *COLOR_BREAK)
            else:
                led_strip.set_rgb(i, 0, 0, 0)
                
        if elapsed_time_secs >= BREAK_SECS:
            state = "idle"
            print("Tauko päättyi. Paina nappia aloittaaksesi uuden jakson.")
            flash(*COLOR_FLASH)
            clear_strip()
                
    utime.sleep(0.01)