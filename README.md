# Bus Information Terminal (VMS)

This project implements a Variable Message Sign (VMS) system for bus terminals that displays real-time information about bus routes, estimated arrival times, and passenger capacity. The system integrates GPS tracking, passenger counting, and route information to provide accurate and useful information to passengers waiting at terminals.

## System Architecture

The system consists of several interconnected components that work together to provide real-time bus information on LED displays. The main components are:


### 1. GPS Tracking Integration (Traccar)
The system connects to Traccar, an open-source GPS tracking platform, to retrieve real-time bus location data. The connection is established using HTTP Basic Authentication, and the system polls the Traccar server for the latest bus coordinates. This information is essential for determining the bus's position along its route and calculating estimated arrival times to upcoming stops. The GPS data includes latitude, longitude, speed, and course information for accurate positioning and movement tracking.


### 2. Route Mapping and Next Stop Prediction
The system uses GTFS (General Transit Feed Specification) static data to map bus routes and predict the next stop. It implements a map-matching algorithm that projects the real-time GPS coordinates onto the predefined route geometry. The algorithm calculates the closest point on the route to the current bus position and determines which segment of the route the bus is currently traversing. Based on this information, it identifies the next stop in the sequence and calculates the remaining distance to that stop.


### 3. Passenger Counting System
The passenger counting system uses computer vision to detect and count passengers inside the bus. The system implements YOLOv8n (You Only Look Once version 8 nano), a real-time object detection model, to identify people in images captured from inside the bus. The detection process includes drawing bounding boxes around detected individuals and returning the total count. The system currently uses a placeholder image for testing purposes, but in a real implementation, it would connect to a camera inside the bus to capture images every 30 seconds (as configured in the main loop). The passenger count is then converted into capacity levels: "Bajo" (Low) for 0-14 passengers, "Medio" (Medium) for 15-29 passengers, and "Alto" (High) for 30+ passengers. The hardware requirements for this system depend on the specific implementation - it could use a smartphone camera, dedicated IP cameras, or specialized counting devices installed inside the bus.


### 4. Big Data Integration (Simulated)
The system is designed to integrate with a Big Data API to retrieve historical and predictive data about travel times between stations. This data is crucial for calculating accurate estimated arrival times (ETA) based on current traffic conditions, historical patterns, and other factors. Due to legal restrictions, the actual Big Data API cannot be shown or accessed directly. However, the system includes a simulated API implementation that reads from a JSON file containing pre-defined travel times between stations. This allows for testing and development of the system without requiring access to the actual Big Data infrastructure. The simulated API returns the total length of the route and the expected travel time to the next station, which are used in the ETA calculation.


### 5. LED Display Generation (VMS)
The system generates visual output for LED displays commonly found in bus terminals. It creates a virtual P8 LED panel simulation with dimensions of 160x48 pixels (5 panels x 3 panels of 32x16 LEDs each). The display shows information in the format "Route X >> Y seconds >> Capacity Level", where X is the route ID, Y is the estimated arrival time in seconds, and Capacity Level indicates the current passenger load. The system supports colored text rendering, allowing for visual differentiation of different information elements. The LED display simulation includes proper spacing, LED shapes, and color representation to accurately simulate how the information would appear on real hardware. The output is saved as an image file (led_image.png) that can be displayed on physical LED panels or used for testing purposes.


## Launching the System

### Assets for panel
* Create the folder _assets/_
* Download the font _Seven Segment.ttf_ and install it there

### Connect to Traccar
1. Install Traccar from official webpage.
2. Open the folder of Traccar
3. Run the next command: java -jar tracker-server.jar conf\traccar.xml
4. Open localhost:8082
    * User: admin
    * Password: admin
5. On 'Devices' tool bar, create a new device:
    * Name: your phone
    * Identifier: 12345 (It doesn't matter, just a number)

### Create VPN using ngrok
1. Install ngrok from official webpage.
2. Open the folder of ngrok.
3. Run the next command: .\ngrok.exe http 5055
    * If it is your first time, run this first: ngrok config add-authtoken token.
    * The token is showed in the web page, register and login first.

### Traccar Client on Mobile
1. Download Traccar Client.
2. Go to 'Settings'
3. In 'Device Identifier' use the same on Traccar Web.
4. In Server URL use 'Forwarding' URL from ngrok.
5. Set 'Continues monitoring' enable.
    * Check in the webpage if the device is online.
