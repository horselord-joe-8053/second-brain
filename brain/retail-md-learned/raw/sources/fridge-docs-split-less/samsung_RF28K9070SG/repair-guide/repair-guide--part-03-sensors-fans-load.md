## Load mode, DC fans and sensor measurements

**Original manual:** *Fast Track Troubleshooting*. **Source file:** `repair-guide.pdf`.

### SFT-LOAD-001 — Load-mode LED segment map, all 26 records

**Knowledge ID:** `SFT-LOAD-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 3.  
**Customer phrasing:** Load mode segments; What does the compressor LED mean?; Fan status LEDs.  

**Procedure:** Hold **Freezer + Fridge + Flex Zone** for **6 seconds** and release after on/off LEDs blink. Match the illuminated LED segment in the table; the letters refer to segments in the printed panel diagram, not letters entered by the user.

| No. | Part / status | Display LED | Manufacturer description |
|---:|---|---|---|
| 1 | R-FAN HIGHEST | "a" and "b" at the lowest order digit of the R compartment | In the case of the R-FAN HIGHEST operation, the corresponding LED is turned on. |
| 2 | R-FAN HIGH | "a" at the lowest order digit of the R compartment | In the case of the R-FAN HIGH operation, the corresponding LED is turned on. |
| 3 | R-FAN LOW | "b" at the lowest order digit of the R compartment | In the case of the R-FAN LOW operation, the corresponding LED is turned on. |
| 4 | Overload | "e" at the lowest order digit of the R compartment | If the external air temperature is 34℃ or higher, the corresponding LED is turned on. |
| 5 | Low Temperature | "f" at the lowest order digit of the R compartment | If the external air temperature is 21℃ or less, the corresponding LED is turned on. |
| 6 | Demo Mode | "g" at the lowest order digit of the R compartment | The LED is turned on in Demo Mode. |
| 7 | COMP | "a" at the lowest order digit of the F compartment | In the case of the F COMP operation, the corresponding LED is turned on. |
| 8 | F-FAN HIGHEST | "b" and "c" at the lowest order digit of the F compartment | In the case of the F-FAN HIGHEST operation, the corresponding LED is turned on. |
| 9 | F-FAN HIGH | "b" at the lowest order digit of the F compartment | In the case of the F-FAN HIGH operation, the corresponding LED is turned on. |
| 10 | F-FAN LOW | "c" at the lowest order digit of the F compartment | In the case of the F-FAN LOW operation, the corresponding LED is turned on. |
| 11 | F compartment defrost heater | "d" at the lowest order digit of the F compartment | The LED is turned on when the freezer defrosting heater operates. |
| 12 | C-FAN HIGHEST | "e" and "f" at the lowest order digit of the F compartment | In the case of the C-FAN HIGHEST operation, the corresponding LED is turned on. |
| 13 | C-FAN HIGH | "e" at the lowest order digit of the F compartment | In the case of the C-FAN HIGH operation, the corresponding LED is turned on. |
| 14 | C-FAN LOW | "f" at the lowest order digit of the F compartment | In the case of the C-FAN LOW operation, the corresponding LED is turned on. |
| 15 | F Valve | "b" at the second lowest order digit of the F compartment | In the case of the F valve open, the LED is turned on. |
| 16 | CV Valve | "c" at the second lowest order digit of the F compartment | If the CV valve opens, the LED is turned on. |
| 17 | R Valve | "f" at the second lowest order digit of the F compartment | If the R valve opens, the LED is turned on. |
| 18 | French Heater | "g" at the second lowest order digit of the F compartment | In the case of the French Heater operation, the corresponding LED is turned on. |
| 19 | CV-FAN HIGHEST | “Freezer” or “Thin Ice” for the CV compartment | In the case of the CV-FAN HIGHEST operation, the corresponding LED is turned on. |
| 20 | CV-FAN HIGH | “Freezer” for the CV compartment | In the case of the CV-FAN HIGH operation, the corresponding LED is turned on. |
| 21 | CV-FAN LOW | “Thin Ice” for the CV compartment | In the case of the CV-FAN LOW operation, the corresponding LED is turned on. |
| 22 | CV compartment defrosting heater | “Fridge” for the CV compartment | When the CV compartment defrosting heater operates, the LED is turned on. |
| 23 | Normal | "e" and "f" in the lowest order digits of the R compartment, and the LEDs are all turned off. | When the external temperature is within the range of 22℃~ 33℃. |
| 24 | Ice Room-FAN | "d" at the second lowest order digit of the F compartment | When Ice Room-FAN operates, applicable LED ON. |
| 25 | Ice maker full | “e" at the second lowest order digit of the R compartment | When the Ice Maker's Bucket is full, applicable LED ON |
| 26 |  | WiFi Status | Not connected to the IP sharer (AP) or the Internet: Off Router(AP) connected: Blink Internet connected: On |

**Original PDF visual reference:** The **unlabeled illustration** headed “Load Mode” on printed page 3 of *Fast Track Troubleshooting* shows how the display segments are positioned.

### SFT-DC-FAN-001 — DC fan behavior, voltage checks and frozen airflow

**Knowledge ID:** `SFT-DC-FAN-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Fan starts for three seconds then stops; How to check fan voltage?; Evaporator fan blocked with ice.  

**What it means:** The sheet describes brushless DC fan motors with two speeds and feedback to the main PCB. If reported speed exceeds **600 RPM** or is too low/stopped, fan drive is disabled. The circuit retries with **3 seconds** of DC voltage after **10 seconds**; after **five** such cycles it disables fan drive for **10 minutes**.

**Documented voltage-check sequence, qualified service only:** Power off and back on. Wait **10–60 seconds** for fan voltage to be applied; the sheet gives an **average reading of 9 VDC**. Three seconds of voltage every 10 seconds for five power-up cycles is described as indicating that the main PCB is good. Forced Freeze may be required to activate fans/compressor. Door switches control evaporator fans; the switches must be closed for the motor test.

**Documented blockage branches:** If ice blocks the fan blade, defrost, remove power and check the motor again. If an iced evaporator blocks airflow, remove ice and check again. If the fan blade area is clear, the sheet attributes the problem to the motor.

**Do not overlook:** These are service diagnostics, not homeowner instructions.

### SFT-SENSOR-002 — Resistance fault boundaries and correct DC measurement ground

**Knowledge ID:** `SFT-SENSOR-002`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Where do I put the meter ground probe?; Sensor resistance open or shorted?.  

**Documented sensor checks:** The printed board notes classify sensor resistance **over 100 kΩ** as **open** and **under 2 kΩ** as **shorted**. A sensor can still be out of tolerance even when neither boundary applies. The preceding chart supplies individual temperature/resistance/voltage readings.

**Measurement reference:** When measuring voltage on any DC component, use a location marked **GND** on the main PCB as circuit ground. The sheet warns that chassis ground gives incorrect readings.

**Visual reference:** The **unlabeled illustration** next to the yellow circuit-ground warning at the bottom of printed page 2 of *Fast Track Troubleshooting* shows the board GND point. These are qualified-technician measurements.

### SFT-SENSOR-CHART-01 — Sensor resistance/voltage chart, printed block 1 of 4

**Knowledge ID:** `SFT-SENSOR-CHART-01`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Sensor temperature resistance voltage chart; Samsung thermistor values.  

**How to use:** The original printed sensor chart supplies temperature in °F, resistance in Ω and voltage. Locate the temperature row and read across; do not interpolate an unprinted threshold as if manufacturer supplied it.

| Temperature (°F) | Resistance (Ω) | Voltage (V) |
|---:|---:|---:|
| -29.2 | 64227 | 4.326 |
| -27.4 | 61012 | 4.296 |
| -25.6 | 57977 | 4.264 |
| -23.8 | 55112 | 4.232 |
| -22.0 | 52406 | 4.199 |
| -20.2 | 49848 | 4.165 |
| -18.4 | 47431 | 4.129 |
| -16.6 | 45146 | 4.093 |
| -14.8 | 42984 | 4.056 |
| -13.0 | 40938 | 4.018 |
| -11.2 | 39002 | 3.98 |
| -9.4 | 37169 | 3.94 |
| -7.6 | 35433 | 3.899 |
| -5.8 | 33788 | 3.858 |
| -4.0 | 32230 | 3.816 |
| -2.2 | 30752 | 3.773 |
| -0.4 | 29350 | 3.729 |

### SFT-SENSOR-CHART-02 — Sensor resistance/voltage chart, printed block 2 of 4

**Knowledge ID:** `SFT-SENSOR-CHART-02`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Sensor temperature resistance voltage chart; Samsung thermistor values.  

**How to use:** The original printed sensor chart supplies temperature in °F, resistance in Ω and voltage. Locate the temperature row and read across; do not interpolate an unprinted threshold as if manufacturer supplied it.

| Temperature (°F) | Resistance (Ω) | Voltage (V) |
|---:|---:|---:|
| 1.4 | 28021 | 3.685 |
| 3.2 | 26760 | 3.64 |
| 5.0 | 25562 | 3.594 |
| 6.8 | 24425 | 3.548 |
| 8.6 | 23345 | 3.501 |
| 10.4 | 22320 | 3.453 |
| 12.2 | 21345 | 3.405 |
| 14.0 | 20418 | 3.356 |
| 15.8 | 19537 | 3.307 |
| 17.6 | 18698 | 3.258 |
| 19.4 | 17901 | 3.208 |
| 21.2 | 17142 | 3.158 |
| 23.0 | 16419 | 3.107 |
| 24.8 | 15731 | 3.057 |
| 26.6 | 15076 | 3.006 |
| 28.4 | 14452 | 2.955 |
| 30.2 | 13857 | 2.904 |

### SFT-SENSOR-CHART-03 — Sensor resistance/voltage chart, printed block 3 of 4

**Knowledge ID:** `SFT-SENSOR-CHART-03`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Sensor temperature resistance voltage chart; Samsung thermistor values.  

**How to use:** The original printed sensor chart supplies temperature in °F, resistance in Ω and voltage. Locate the temperature row and read across; do not interpolate an unprinted threshold as if manufacturer supplied it.

| Temperature (°F) | Resistance (Ω) | Voltage (V) |
|---:|---:|---:|
| 32.0 | 13290 | 2.853 |
| 33.8 | 12749 | 2.802 |
| 35.6 | 12233 | 2.751 |
| 37.4 | 11741 | 2.7 |
| 39.2 | 11271 | 2.649 |
| 41.0 | 10823 | 2.599 |
| 42.8 | 10395 | 2.548 |
| 44.6 | 9986 | 2.498 |
| 46.4 | 9596 | 2.449 |
| 48.2 | 9223 | 2.399 |
| 50.0 | 8867 | 2.35 |
| 51.8 | 8526 | 2.301 |
| 53.6 | 8200 | 2.253 |
| 55.4 | 7888 | 2.205 |
| 57.2 | 7590 | 2.158 |
| 59.0 | 7305 | 2.111 |
| 60.8 | 7032 | 2.064 |

### SFT-SENSOR-CHART-04 — Sensor resistance/voltage chart, printed block 4 of 4

**Knowledge ID:** `SFT-SENSOR-CHART-04`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Sensor temperature resistance voltage chart; Samsung thermistor values.  

**How to use:** The original printed sensor chart supplies temperature in °F, resistance in Ω and voltage. Locate the temperature row and read across; do not interpolate an unprinted threshold as if manufacturer supplied it.

| Temperature (°F) | Resistance (Ω) | Voltage (V) |
|---:|---:|---:|
| 62.6 | 6771 | 2.019 |
| 64.4 | 6521 | 1.974 |
| 66.2 | 6281 | 1.929 |
| 68.0 | 6052 | 1.885 |
| 69.8 | 5832 | 1.842 |
| 71.6 | 5621 | 1.799 |
| 75.2 | 5225 | 1.716 |
| 77.0 | 5000 | 1.675 |
| 78.8 | 4861 | 1.636 |
| 80.6 | 4690 | 1.596 |
| 86.0 | 4218 | 1.483 |
| 87.8 | 4072 | 1.447 |
| 89.6 | 3933 | 1.412 |
| 91.4 | 3799 | 1.377 |
| 95.0 | 3547 | 1.309 |
| 96.8 | 3428 | 1.277 |
| 100.4 | 3204 | 1.213 |
