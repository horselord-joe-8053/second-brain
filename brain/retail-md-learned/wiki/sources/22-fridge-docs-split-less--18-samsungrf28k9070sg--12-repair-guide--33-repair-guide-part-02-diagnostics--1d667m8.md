---
type: source
title: Diagnostic mode and error-code troubleshooting
authors: []
year: 2026
url: ""
venue: ""
tags: [diagnostics, troubleshooting, Samsung, RF28K9070SG]
related: [samsung, rf28k9070, rf22k9381, rf28k9380, fast-track-troubleshooting]
created: 2026-10-19
updated: 2026-10-19
sources: ["fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md"]
---

# Samsung RF28K9070SG Repair Guide: Part 02 - Diagnostics

This document provides detailed diagnostic procedures for the Samsung RF28K9070SG refrigerator, including how to enter diagnostic mode and interpret error codes. It is based on the *Fast Track Troubleshooting* manual.

## Diagnostic Mode

### Entering Diagnostic Mode
To enter diagnostic mode, hold the **Freezer + Fridge** buttons for **6 seconds**. The screen will blink, and you should continue holding until the screen becomes blank or displays errors. The mode will exit after **1 minute**.

### Error Codes
Error codes are displayed during diagnostic mode and correspond to specific issues within the refrigerator. Each error code is documented in the *Fast Track Troubleshooting* manual.

## Error Codes and Diagnostic Procedures

| Error Code | Description | Diagnostic Method |
|------------|-------------|-------------------|
| **Error 1** | Freezer sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 1 and 3 should be within 4.5V~1.0V. |
| **Error 2** | Fridge sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 1 and 5 should be within 4.5V~1.0V. |
| **Error 4** | Freezer defrost sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 1 and 4 should be within 4.5V~1.0V. |
| **Error 5** | Fridge defrost sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 1 and 6 should be within 4.5V~1.0V. |
| **Error 6** | Ambient sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 1 and 2 should be within 4.5V~1.0V. |
| **Error 9** | Convertible zone sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 11 and 12 should be within 4.1V~0.8V. |
| **Error 11** | Convertible zone defrost sensor error | Check if the sensor is open or shorted. Voltage between Main PCB CN30 pins 11 and 13 should be within 4.1V~0.8V. |
| **Error 13** | Humidity sensor error | Voltage between Main PCB CN30 pins 7 and 9 should be within 4.1V~0.8V. |
| **Error 14** | Fridge Ice maker sensor error | Voltage between MAIN PCB CN90 3↔ 8 should be within 4.5V~1.0V. |
| **Error 15** | Ice room sensor error | Voltage between MAIN PCB CN30 10↔ 11 should be within 4.5V~1.0V. |
| **Error 29** | Convertible zone defrost error | Resistance value between CN70_1-7 ↔ 1 should be 63(230) ohm ± 7%. |
| **Error 31** | Convertible zone fan error | Voltage of MAIN PCB CN74 1↔5 should be between 7V~12V. |
| **Error 35** | Freezer low regist | Follow printed checks. |
| **Error 39** | Ice maker function error | Check operation after changing the Ice Maker. |
| **Error 40** | Ice maker fan error | Voltage of MAIN PCB CN52-1↔ 6 should be between 7V~12V. |
| **Error 41** | MAIN < - > Panel Comm error | Replace Main and Panel PCB if necessary. |
| **Error 44** | MAIN < - > INV Comm error | Replace Main and Inverter PCB if necessary. |
| **Error 46** | I/O Expander Comm error | Replace Main PCB if necessary. |
| **Error 61** | Ice duct heater error | Resistance value between CN51 4↔6 should be 135 ohm ± 7%. |
| **Error 65** | Ice bucket heater error | Resistance value between CN51 4↔7 should be 135 ohm ± 7%. |
| **Error 66** | Door handle heater error | Resistance value between CN51 1↔2 should be 135 ohm ± 7%. |
| **Error 71** | Freezer abnormal temp. error | Check if the door has been open for a long time or if hot food has been stored. |
| **Error 72** | Fridge abnormal temp. error | Check if the door has been open for a long time or if hot food has been stored. |
| **Error 73** | Convertible zone chill error | Check if the door has been open for a long time or if hot food has been stored. |
| **Error 81** | COMP run error | Check soldering status of inverter PCB. |
| **Error 82** | COMP IPM fault | Check soldering status of inverter PCB. |
| **Error 83** | COMP current error | Check compressor wire connections. |
| **Error 84** | COMP Motor stall | Check compressor and Cycle status. |
| **Error 85** | COMP low voltage | Check input voltage. |

## Conclusion

The diagnostic procedures outlined in this document are essential for troubleshooting the Samsung RF28K9070SG refrigerator. Following these procedures will help technicians accurately identify and resolve issues.
