<h1 align = "center">VIRTUAL MOUSE</h1>
<h3 align = "center">Made with :heart: and <img title = "Python" src = "https://user-images.githubusercontent.com/92143521/166102826-59081947-8e61-4e41-87d6-58ef893f0187.svg" height = "20px"> by Mr00Magician
</h3>
<br>

## FAST FORWARD
- [About](#ABOUT)
- [How to Run](#HOW-TO-RUN)
- [Instructions](#INSTRUCTIONS)
- [Customisation](#CUSTOMISATION)
- [Screenshots](#SCREENSHOTS)
- [Demo GIF](#GIF)
- [Note](#NOTE)

<h2 id ="ABOUT"> ABOUT THE APP </h2>

Developed using OpenCV and Mediapipe, this app will allow you to use your computer without a physical mouse by allowing you to perform basic mouse operations by using certain hand gestures and movements in front of your webcam. <br> <br>

<h2 id ="HOW-TO-RUN"> HOW TO RUN </h2>

To run this app, follow these simple steps:
- See that you have `Python` installed.
- Clone this repository.
- Create a new Python environment and install the dependencies in it. This can be done as follows:
  - Open `command prompt` and `cd` to the directory where you have cloned the repo.
  - Run the command `Python -m venv env` to create a new virtual environment named `env`
  - Activate the enviroment by running the command `env\Scripts\activate.bat`
  - Install depencies by running the command `pip install -r requirements.txt` <br> 

The above steps will create a python virtual environment and install the required depndencies in it. Now whenever you want to run the app, follow these steps:
- Open `command prompt` and `cd` to the directory where you have cloned the repo.
- Activate the python environment by running the command `env\Scripts\activate.bat`.
- Run the app by the command `Python Virtual_Mouse.py`. <br> <br>

<h2 id ="INSTRUCTIONS"> INSTRUCTIONS ON HOW TO USE THE APP </h2>

Upon running the app, your webcam will be turned on and will be used to track your hand and fingers. As of now, you can only use your right hand to use this app. Support for left hand is coming soon.
This app works in 4 modes:
- Pointer Mode
- Left Click Mode
- Right Click Mode
- Scrolling Mode

### Pointer Mode
This mode will be triggered when only your index finger is up, while the rest are down. In this mode you can move around your index finger to move the cursor on screen. The red circle on the index finger indicates that you are in pointer mode.

### Left Click Mode
This mode will be triggered when your index and middle fingers are up while rest are down. While in this mode, bring your index and middle fingers closer to perform a typical mouse left-click. The red circle on the index and the middle finger indicates that you are in left-click mode.

### Right Click Mode
This mode will be triggered when your index finger and thumb are up while rest of the fingers are down. While in this mode, bring your index finger and thumb closer to perform a typical mouse right-click. The red circle on the index finger and the thumb indicates that you are in right-click mode.

### Scrolling Mode
This mode will be triggered when your index, ring and middle fingers are up while rest of the fingers are down. While in this mode, move your ring finger away from your middle finger to scroll up and move your index finger away from your middle finger to scroll down. The red circle on the index, ring and the middle finger indicates that you are in scrolling-click mode.


See [SCREENSHOTS](#SCREENSHOTS) for better understanding of different modes. <br> <br>

<h2 id = "CUSTOMISATION"> CUSTOMISATION </h2>

You can customise some aspects of this app based on your preferences. Few of the things you can change are:
- Sensitivity of the cursor
- Amount of smoothening applied to movement of cursor
- Enable/Disbale FPS <br>
To change these things, you can pass certain flags to this program when running it. Run the command `python Virtual_Mouse.py --help` to get help about how to use these flags and know about more customisation settings. <br> <br>

<h2 id = "SCREENSHOTS">SCREENSHOTS</h2>

|![Hand Detection](https://user-images.githubusercontent.com/92143521/189514478-a3d81356-e26b-4f6f-a39a-76743030fb60.png)|
|:--:|
|Hand Detection|
|![Pointer Mode](https://user-images.githubusercontent.com/92143521/189514543-4cf30248-185d-4de3-a81e-0de066068679.png)|
|Pointer Mode|
|![Left Click Mode](https://user-images.githubusercontent.com/92143521/189514619-944268b0-aff3-4000-a09a-e45967a50dc5.png)|
|Left Click Mode|
|![Left Click Triggered](https://user-images.githubusercontent.com/92143521/189514701-54cd7cd4-1bd1-4cb9-9bfc-5a6df165e7f8.png)|
|Bring fingers closer to trigger mouse left-click. The circle between the fingers will turn green when a click is triggered|
|![Right Click Mode](https://user-images.githubusercontent.com/92143521/189514735-cf795679-b1c8-440f-89bf-bd721e8b85da.png)|
|Right Click Mode|
|![Right Click Triggered](https://user-images.githubusercontent.com/92143521/189514749-fea7170b-43b7-47e9-b4d9-5d51355f446b.png)|
|Bring index finger and thumb closer to trigger mouse right-click. The circle between them will turn green when a click is triggered|
|![Scrolling Mode](https://user-images.githubusercontent.com/92143521/189514796-d35650f8-4c09-4f51-841d-014825c311e2.png)|
|Scrolling Mode|
|![Scroll Up](https://user-images.githubusercontent.com/92143521/189514824-4da7de44-4407-4667-b680-3037d14a8a11.png)|
|Scroll up by moving your ring finger away from Middle finger|
|![Scroll Down](https://user-images.githubusercontent.com/92143521/189514879-4f01d021-bf01-4089-a128-3fc14282d3d3.png)|
|Scroll Down by moving your index finger away from your middle finger| <br> <br>

<h2 id ="GIF"> A GIF TO DEMONSTRATE WORKING </h2>

|<img src="Assets/Demo GIF.gif">|
|:--:|
|Demo GIF| <br> <br>

<h2 id = "NOTE"> NOTE </h2>

Sometimes the position of thumb is such that its hard to detect whether it is `up` or `down` as it doesn't actually go down like rest of the fingers. This may cause issues. So keep in mind that the correct position of thumb when it will be treated as `up` or `down` or not active is as follows:

|![Thumb Up](https://user-images.githubusercontent.com/92143521/189515361-6e7651aa-e83b-4731-8326-a3ad4021c1c5.png)|
|:--:|
|Thumb Up|
|![Thumb Down](https://user-images.githubusercontent.com/92143521/189515383-f6276c7f-5cb7-4c29-8c2b-0d6a8c3f1657.png)|
|Thumb Down|
