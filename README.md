# Edge ML Club materials

This repository provides several Python modules that are required
for the Edge ML Club projects, including starter script files for those projects.

**TODO: Update the RPI image URL and git clone URL below with final version.**

## Get started

1. [Download this Raspberry Pi image](https://drive.google.com/file/d/1QxMG5YdLhnJtENGiqO3gBtYRWH-cHcj6/view?usp=sharing&resourcekey=0-8uTVzxpS600tzY0jmTumOw)
    and flash it onto your SD card. If you're not familiar with flashing, follow these steps:

    1.  Plug in a microSD card to a desktop/laptop computer (you might need an SD card adapter).

    1.  On the same computer, install the [Raspberry Pi Imager](https://www.raspberrypi.org/software/).

    1.  Open the Raspberry Pi Imager, click **Choose OS**, then scroll down and click
    **Use custom**.

    1.  In the window that appears, select the ZIP file you downloaded in the first step above
    (the filename starts with "codenext").

    1.  Back in the Raspberry Pi Imager, click **Choose SD Card**, and select your microSD card.

    1.  Now click **Write** to begin flashing the card.

1.  When flashing is complete, insert the SD card into your Raspberry Pi and power it on.

1.  Connect a USB camera and [Coral USB Accelerator](https://coral.ai/products/accelerator)
    to the blue USB ports on your Raspberry Pi. (The blue ports are USB 3.0, the others are 2.0.)

1.  On the Raspberry Pi, download this Git repository by opening the Terminal application
    and running this command:

    ```
    git clone https://coral.googlesource.com/codenext-raspimon
    ```

1.  Enter the directory and download some required files:

    ```
    cd codenext-raspimon

    make download
    ```

1.  Now run the `test.py` script to be sure the camera and accelerator are working:

    ```
    python3 test.py
    ```
