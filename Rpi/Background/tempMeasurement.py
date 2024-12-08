import subprocess
import time
import gpiod

FanPin = 17
chip = gpiod.Chip('gpiochip4')
fanLine = chip.get_line(FanPin)
fanLine.request(consumer="Fan", type=gpiod.LINE_REQ_DIR_OUT)

def getTemperature():
    result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
    temp_str = result.stdout.strip()
    temperature = float(temp_str.split('=')[1].split('\'')[0])  # Extract numeric value
    return temperature

# Example usage
#print(f"CPU Temperature: {getTemperature()}°C")

try:
	while True:
		# Getting temperature values
		time.sleep(1)
		tempValue = getTemperature()
		print(f"CPU Temperature: {tempValue}°C")
		
		# Turning fan on depend upon the temperature
		if(tempValue >= 60):
			fanLine.set_value(1)
			print("Fan ON")
		else:
			fanLine.set_value(0)
			print("Fan OFF")
						
finally:
   fanLine.release()
	
