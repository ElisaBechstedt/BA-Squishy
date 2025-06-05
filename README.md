# Squishy User Manual

**Squishy** is a tangible interface that allows physical interaction with ChatGPT. This repository contains everything needed to set it up and run it locally.

---

## Requirements

- **Squishy**
- **A PC or Laptop** (to run a local server)
- **The interaction script** (already on Squishy but must be updated if IP, Wi-Fi or PC changes)

---

## Setup Instructions

### 1. Adjust Wi-Fi and Server Info

If your Wi-Fi, password, PC or IP address changes, you must update the script. Therefore:



1. Download the repo from GitHub.
2. Open the files with **Thonny** or any other IDE.
3. Rename the **interactionScript.py** to **`main.py`** (important!).
4. Provide credentials for both scripts in one of two ways:
   - Adjust the `secret.py` file and upload it to Squishy
   - Or hardcode values directly into `main.py` and `integrationScript.py`, in this case delete or comment "import secret" in both scripts.
5. Upload `main.py` (and `secret.py`) to Squishy.


### 2. Run the Interaction Script to start the Local Server

1. On your PC, run the integration script provided in this repo. This script starts a local web server listening on the port you specified in `secret.py`.
2. Open your web browser and visit the url.
3. Now you should be able to see a white screen. Here you will later see the Squishy interactions.


## Prepare ChatGPT

1. Open ChatGPT in **fullscreen mode**.
2. Send at least one message so the input bar shifts to the bottom.

> Important: Squishy simulates clicks.
> If the input bar is not visible, Squishy will click in the wrong place.

## Power Squishy

You can power Squishy in two ways:

### Manual (for debugging)
- Connect Squishy to your PC via USB.
- Open and run `main.py` manually in Thonny.

### Autonomous Mode
- Power Squishy using a power bank.

> If you see a tiny red LED light in Squishy, it is powered on.
> After a few Seconds you should see a blue LED light, indicating that Squishy is connected to Wi-Fi.
> Now you can start interacting with Squishy, you will see interactions in your browser.


## Troubleshooting

- **PC and Squishy must be on the same Wi-Fi network.**
  If they aren’t, Squishy won’t reach your server.

- **Check IP address and port carefully.**
  The IP in `secret.py` must match your PC’s local IP. The port must be the same as used by the integration server.

- **If you don’t see interactions on the server page:**
  - Confirm the server script is running on your PC.
  - Make sure you are using a free port.
  - Restart Squishy and make sure it connects to the WI-FI.

- **If Squishy’s LEDs don’t light up:**
  - Check your power source or USB connection.
  - Make sure `main.py` (and `secret.py`) are correctly uploaded.
