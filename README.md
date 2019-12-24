![Logo](logo.png)

# Alexa-controlled Lego Biological ExpeRimenT (ALBERT) <!-- omit in toc -->

**!! NOTE: Some bacterial growths can be harmful to humans. Please use common sense and safe practices if attempting to build and test this project with real plates. !!**

## Table of Contents <!-- omit in toc -->
- [Background](#background)
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Design Problems](#design-problems)
- [Software Architecture](#software-architecture)
- [Build Instructions](#build-instructions)
- [About Me](#about-me)

## Background
Space. The Final Frontier. As NASA prepares to head back to the moon, the ISS has been speeding across the sky at 17,000 mph for the last twenty years, performing untold amounts of scientific research that benefit us right here on earth. One of the key themes of this research has been studying the behavior of life in microgravity, both at the human level and the microscopic scale. As humanity dreams of settling on other planets, we must first rigorously understand how biological organisms operate in microgravity. Will some pathogens, relatively harmless on earth, become dangerous in microgravity? Can artifical organs be grown and manufactured in weightless environments? Just how exactly does space change the function of cells? What medical advances are possible to save lives here on earth?

Space experiments are expensive. A single astronaut's time could be worth [$60,000 to $80,000 per hour](https://www.quora.com/What-is-the-cost-of-an-hour-of-an-ISS-astronauts-time). Many astronauts are not scientists themselves, but engineers and pilots. They receive extensive training and instructional procedures for experiments, but basic science is often not their native discipline. 

In addition, future missions to Mars may find themselves too far from Earth for real-time interaction with mission control to help run or tend to experiments. The crew must be self-supporting and have the help they need to operate the experiments if this is the case.

## Problem Statement
Due to the complexity of running and monitoring experiments in microgravity in Low Earth Orbit (LEO) and during long-duration interplanetary flight, astronauts need an intuitive method of interacting with experiments that abstracts away the need for niche knowledge of the specific scientific field and facilitates simple interaction with minimal training.

## Solution Overview
To solve this solution, I have prototyped ALBERT, or the Alexa-controlled LEGO Biological ExpeRimenT. ALBERT demonstrates the effectiveness of a voice-controlled experiment interface that would allow astronauts to intuitively interact with systems in the absence of continuous communication with mission control and without the need for extensive training.

In it's current form, ALBERT is capable of reacting to voice commands to create new bacterial growth experiments, selecting, swabbing, storing, and monitoring an agar plate. Astronauts need only insert a swab and say, "Alexa, tell ALBERT lab to use this swab." To check an experiment, the crew member can simply ask, "Alexa, tell ALBERT lab to check plate 1."

### Importance of Intuitive Voice Control
ALBERT's intuitive voice control interface is critical to its primary goal -- simplifying the interface to complex experiments to enable virtually untrained crew members to quickly and adeptly create and monitor scientific research. Extensions of the current work will allow dynamic voice interactions with multiple experiments, integration of image processing and datalogging, and critical streamlining of the entire experiment process from launch to landing.

### Why Alexa?
Alexa is the perfect voice-input method for ALBERT. By categorizing commands via intents, Alexa outperforms a simple voice recognition system by its ability to understand the purpose behind an utterance. Additionally, Alexa's ability to integrate with so many other tools and systems opens the door for its use as a unified natural language interface to complex systems such as orbiting laboratories or spacecraft with intuitive interactions.

### Applications
Like many other technologies developed for space exploration, ALBERT's impact can extend far beyond the ISS or interplanetary vehicles. Potential other applications include:
- Automating laboratories on Earth (like [this](https://www.ncbi.nlm.nih.gov/pubmed/30021077))
- Demonstrating the value of integrating laboratories with voice assistants like Alexa for a unified human-laboratory or crew-vehicle interface
- Stimulating the development of fully automated experiment monitoring tools that could leverage new deep learning and AI techniques 

## Design Problems
While building the ALBERT prototype, several key design problems were encountered. They are briefly summarized here along with the chosen solution.

### Rigid Frame
A key concern at the start of the project was ensuring the careful positioning of the necessary sections (workstation, robotic arm, sterile plate storage, and live experiment storage). Misalignment among these components can negatively affect the reliability and repeatability of the procedures. 

To mitigate this, all the key models were secured to an aluminum TETRIX frame.

### Reliable Plate Positioning
LEGO geartrains often experience a large amount of play, making very precision positioning very difficult. However, the plates must be consistently placed on the workstation in a tight area to enable the arm to lift and replace the lids reliably. Additionally, the vertical storage racks have little room for horizontal position errors.

By placing axles as guides at the base of the workstation platter, I could ensure that the plates would be guided down into the platter even in the presence of horizontal manipulator error. To ensure the plates could be consistently vertically stored, angled guides were included in the rack design.

### Swabbing the Plate
To create an experiment plate, the swab cannot simply touch the agar, but must be swiped over some amount of surface area.

Rather than require a second robotic arm to maneuver the swab over the surface of the agar, I elected to directly spin the dish to swab an arc across its surface. Simply by attaching a motor with rubber tire to the workstation allows simple rotating of the dish without the need for a complex assembly.

### Controlling Two Subsystems
To limit complexity, ALBERT is divided into two primary subsystems, the robotic arm and the workstation. ALBERT's primary controller, the EV3 Intelligent Brick, must be able to communicate with the workstation to trigger swab and monitoring operations.

The ev3dev operating system enables the EV3 to remote control the NXT over a USB connection using the `nxt-python` library.

### Two-Position Gripper/Wrist
To store plates vertically and place them horizontally in the workstation requires two arm positions, horizontal and vertical.

A wrist join enables this rotation, but care must be taken to align the wrist rotation axis with the center of the end effector. Misalignment will cause the horizontal and vertical gripper orientations to be slightly offset from each other, causing issues when placing the plate or removing the lid.

### Repeatable Base Positions
The arm must be able to repeatably position itself at the sterile rack, workstation, and storage rack. Originally, this was done with dead reckoning, but for improved performance the EV3 color sensor is used to detect colored stripes as the arm base rotates.

### Lifting the Dish Lid
Lifting the dish lid is hard. The tolerance is only about +/- 0.25 cm in my estimate, which is tough to achieve with LEGO gearing. Although ALBERT was able to lift the lid by gripping the edge several times, it was not consistent. THe lid would often pivot in the gripper, preventing it from being replaced on the dish, or slide out of the gripper entirely.

The solution was to slightly modify the dish lid to add a "handle" that the gripper could easily hold on to. This handle was made of two bevel gears and was hot-glued to the dish lid.

![lid_handles](lid_handles.jpg)
*Prototype duct tape handle and the final hot-glued bevel gear handles*

## Software Architecture
The software stack is divided into two major sections: the Alexa-hosted Node.js skill and the Python Alexa Gadget code on the EV3.

### Alexa Skill
The Alexa skill code can be browsed in the `skill` directory. Several key intents are defined and implemented, following the pattern of the sample missions for the LEGO Mindstorms Alexa Challenge.

- `MakePlateIntent` - This intent sends the "make plate" directive to the EV3 gadget
- `CheckPlateIntent` - This intent sends the "check plate" directive to the EV3 gadget along with the number of the plate to check. In most cases, this will be one, but it one be extended to devices with more than one storage rack in the future.
- `GadgetEventHandler` - This handler catches the events returned back from the EV3 gadget to report when a plate has been made or the status of a previously made plate.

### EV3 Python Gadget Code
The gadget code is designed to receive gadget commands from the cloud-based Alexa skill and activate the ALBERT. This includes a class to encapsulate ALBERT's capability in `albert.py` and a gadget class based off the sample code, written in `albert_gadget.py`. The gadget code is fairly self-explanatory. The ALBERT control code makes extensive use of keypoints defined for the manipulator (arm) to concisely encode the sequence of motions required for each task. These tasks can then be triggered from the gadget code.

The `workstation.py` file leverages the `nxt-python` library to remote control the NXT over a USB connection. The swab and check plate operations are simple, moving the head into position and rotating the dish if necessary.

## Build Instructions
All the CAD models were created using [Studio](https://www.bricklink.com/v3/studio/download.page).
### 1. Build the Arm
![Arm](models/arm.png)
The arm CAD model can be found in `models/arm.io`.
### 2. Build the Workstation
![Workstation](models/workstation.png)
Build the workstation using `models/workstation.io`.

### 3. Build the TETRIX Base and Plate Holders
![Plate Holder](models/plate_holder.png)
Build two plate holders (mirror images) using `models/plate_holder.io`. 

To create the platform with colored stripes, I used a section of foam-core board. Align the arm with each of the sterile rack, workstation, and storage rack, and place a strip of red, blue, and yellow colored tape under the sensor, respectively. 

### 4. Setup the Software Environment
1. Download ev3dev from the [download page](https://www.ev3dev.org/downloads/)
2. Flash the image to an SD card using [Etcher](https://etcher.io/)
3. Connect the EV3 brick to your computer with a USB A-to-Mini-B cable and [enable USB internet sharing](https://www.ev3dev.org/docs/tutorials/connecting-to-the-internet-via-usb/).
4. On your computer, [install Visual Studio Code](https://code.visualstudio.com/) from Microsoft. 
5. Once installed, open the extensions panel (`Ctrl+Shift+X`). Then search for and install the ev3dev-browser extension.
6. On your computer, download the source code from GitHub. If you are unfamiliar with git, just download the code as a zip file using the button at the top right of this page. Advanced users can clone this repository.
7. In order to communicate with the NXT workstation, `nxt-python` must be installed **on the EV3** (not your computer). To do this, you will need to run a few commands in the EV3 brick terminal. 
   1. To access this terminal, expand the "ev3dev Device Browser" group at the bottom of the Explorer panel (`Ctrl+Shift+E`) and connect to your brick by clicking "Click here to connect a device."
   2. Once connected, right click the ev3dev device and select "Open SSH Terminal."
   3. Run the following commands
        ```bash
        # install pip3 (python3 package manager)
        sudo apt install python3-pip

        # install pyusb for USB connection to NXT
        sudo pip3 install pyusb

        # install nxt-python (python3 beta)
        wget https://github.com/ev3dev/nxt-python/archive/ev3dev-stretch.zip
        unzip ev3dev-stretch
        cd nxt-python-ev3dev-stretch
        python3 setup.py install # you may need to prepend `sudo`
        ```
### 5. Setup the Alexa Gadget
(These steps are adapted from the [LEGO MINDSTORMS Voice Challenge Mission 1](https://www.hackster.io/alexagadgets/lego-mindstorms-voice-challenge-mission-1-f31925) example)
1. Create an [Amazon Developer](https://developer.amazon.com/) account if you do not yet have one
2. Go to the [Alexa Voice Service](https://developer.amazon.com/alexa/console/avs/home) page and click the "PRODUCTS" button.
3. Click the "CREATE PRODUCT" button at the top right of the page.
4. Name the product "MINDSTORMS EV3" with ID of "EV3_01". The product type can be "Alexa Gadget" with a category of "Animatronic or Figure". Fill out a description, choose "No" for intending commercial distribution, and "No" for if it is a child product. Finishing clicking through the product creation.
5. Click on your new device in the list of devices in the console.
6. On the product's page, take note of the Amazon ID and Alexa Gadget Secret codes. You will need them later.

### 6. Code the Alexa Skill
(These steps are adapted from the [LEGO MINDSTORMS Voice Challenge Mission 3](https://www.hackster.io/alexagadgets/lego-mindstorms-voice-challenge-mission-3-4ed812#toc-create-your-alexa-skill-2) example.)
1. Go to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask) and click the blue  "Create Skill" button on the right hand side of the page.
2. Name the skill "ALBERT" and use the default selected "Custom" model. At the bottom of the page, choose "Alexa-Hosted (Node.js)". Finish clicking through the skill creation pages.
3. Enable the custom interface controller by selecting "Interfaces" in the left-hand menu, and turning on "Custom Interface Controller." Save the updates using the button at the top of the page.
4. Next, setup the interaction model by clicking the "JSON Editor" item in the left-hand menu (under the "Interaction Model" heading) and drag and drop the `model.json` file from the `skill` folder in the ALBERT source code. Save and build the model using the buttons at the top of the page.
5. Click the "Code" tab at the very top of the screen. Create the following files and copy and paste the contents from the corresponding ALBERT source files in the `skill/lambda` directory.
   - `common.js` - Common intent handling, such as for help or cancel actions
   - `index.js` - Contains the main intent and event handlers
   - `package.json` - Package information
   - `util.js` - Utility code (from Mission 3)
6. Click "Save" and then "Deploy" to activate your skill!
7. Create a `albert_gadget.ini` file in the `gadget` directory with the following contents:
   ```ini
   [GadgetSettings]
   amazonId = YOUR_GADGET_AMAZON_ID
   alexaGadgetSecret = YOUR_GADGET_SECRET

   [GadgetCapabilities]
   Custom.Mindstorms.Gadget = 1.0
   ```
   The ID and secret are the values from step 5.

### 7. Downloading and Running
Almost there! In the VS Code Explorer panel (`Ctrl+Shift+E`) find the ev3dev device at the bottom of the screen. Click the download button near the left edge of the ev3dev Device Browser header.
> If you don't see this button, make sure you are connected to your EV3 brick

Once your files have been copied over, find the `albert/gadget/albert_gadget.py` file, right-click it, and select "Run."

If this is your first time running, you will need to pair the EV3 with your Alexa device over Bluetooth. You can do this through the Alexa app. Make sure that Bluetooth is turned on for the EV3. 

If you run into issues with Bluetooth being unavailable on the EV3, see [this Github issue](https://github.com/ev3dev/ev3dev/issues/1314). TL;DR: Run these lines on your EV3 terminal (same terminal from which you installed `nxt-python`)

```bash
sudo systemctl mask systemd-rfkill.service
sudo systemctl mask systemd-rfkill.socket 
```

and then restart your EV3.

## About Me
<img src="https://mruss.dev/static/814a18529ab944c8d9c9f59c6e6c30b8/5b62b/profile.jpg" style="width: 75px; height 75px; border-radius:100%">

Hey! I'm Matthew, and I'm studying machine learning for my Ph.D. at the University of Kentucky and first worked with LEGO MINDSTORMS through the NXT over 10 years ago. Get to know me more on my blog, [mruss.dev](https://mruss.dev).

---
These instructions are current as of 2019-12-24.