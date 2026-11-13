## Diagnostic mode and error-code troubleshooting

**Original manual:** *Fast Track Troubleshooting*. **Source file:** `repair-guide.pdf`.

### SFT-CONTROL-001 — Demo mode, load mode and diagnostic mode buttons

**Knowledge ID:** `SFT-CONTROL-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 1.  
**Customer phrasing:** Why does my fridge show 0 FF?; How to enter diagnostic mode?; Which buttons show load status?.  

**Demo / cooling-off mode:** Hold **Freezer + Fridge + Door Alarm** for **6 seconds** until the display shows **0–FF**. Repeat to exit.

**Load mode:** Hold **Freezer + Fridge + Flex Zone** for **6 seconds**. The on/off LEDs blink. Release the buttons to see load status, then use the load-display mapping in `SFT-LOAD-001` (printed page 3).

**Diagnostic mode:** Hold **Freezer + Fridge** for **6 seconds**; the screen blinks. Continue holding until the screen becomes blank or errors appear. The sheet states the mode exits after **1 minute**. Match displayed errors to `SFT-ERROR-*` entries from printed pages 4–6.

**Customer phrasing:** Refrigerator says 0–FF; no cooling with lights active; checking error display; LED status symbols. Distinguish this specific panel layout from other controls.

### SFT-DIAGNOSTIC-001 — Reading a service diagnostic error

**Knowledge ID:** `SFT-DIAGNOSTIC-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4, 5, 6.  
**Customer phrasing:** How to interpret Samsung error numbers?; Service code appears on the display.  

**Procedure:** Hold Freezer + Fridge for **6 seconds**; continue to hold through the blinking stage until the panel is blank or displays error segments. The sheet exits diagnostic mode after **1 minute**. Identify the error number from its page-4–6 table and consult that exact `SFT-ERROR-*` record. Many recommended checks involve live voltages, connectors and main/inverter PCB servicing and require qualified service.

**Do not generalize:** An error name is not proof that its named component has failed. Follow the specific “Diagnostic method” from the matching printed table and honor qualification/safety warnings.

**Original PDF visual reference:** See the **unlabeled illustration** under “Diagnostic mode” on printed page 1, and the three “Diagnostic mode” tables on printed pages 4–6 of *Fast Track Troubleshooting*.

### SFT-ERROR-001 — Error 1: Freezer sensor error

**Knowledge ID:** `SFT-ERROR-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 1; Freezer sensor error; Freezer sensor error diagnostic.  

**Meaning:** Service error **1** is labeled **Freezer sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the Sensor is Open or Shorted The voltage between the Main PCB CN30 pins 1 and 3 should be within the 4.5V~1.0V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 1 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-002 — Error 2: Fridge sensor error

**Knowledge ID:** `SFT-ERROR-002`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 2; Fridge sensor error; Fridge sensor error diagnostic.  

**Meaning:** Service error **2** is labeled **Fridge sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 1 and 5 should be within the 4.5V~1.0V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 2 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-004 — Error 4: Freezer defrost sensor error

**Knowledge ID:** `SFT-ERROR-004`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 4; Freezer defrost sensor error; Freezer defrost sensor error diagnostic.  

**Meaning:** Service error **4** is labeled **Freezer defrost sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 1 and 4 should be within the 4.5V~1.0V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 4 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-005 — Error 5: Fridge defrost sensor error

**Knowledge ID:** `SFT-ERROR-005`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 5; Fridge defrost sensor error; Fridge defrost sensor error diagnostic.  

**Meaning:** Service error **5** is labeled **Fridge defrost sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 1 and 6 should be within the 4.5V~1.0V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 5 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-006 — Error 6: Ambient sensor error

**Knowledge ID:** `SFT-ERROR-006`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 6; Ambient sensor error; Ambient sensor error diagnostic.  

**Meaning:** Service error **6** is labeled **Ambient sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 1 and 2 should be within the 4.5V~1.0V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 6 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-009 — Error 9: Convertible zone sensor error

**Knowledge ID:** `SFT-ERROR-009`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 9; Convertible zone sensor error; Convertible zone sensor error diagnostic.  

**Meaning:** Service error **9** is labeled **Convertible zone sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 11 and 12 should be within the 4.1V~0.8V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 9 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-011 — Error 11: Convertible zone defrost sensor error

**Knowledge ID:** `SFT-ERROR-011`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 11; Convertible zone defrost sensor error; Convertible zone defrost sensor error diagnostic.  

**Meaning:** Service error **11** is labeled **Convertible zone defrost sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 11 and 13 should be within the 4.1V~0.8V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 11 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-013 — Error 13: Humidity sensor error

**Knowledge ID:** `SFT-ERROR-013`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 13; Humidity sensor error; Humidity sensor error diagnostic.  

**Meaning:** Service error **13** is labeled **Humidity sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The voltage between the Main PCB CN30 pins 7 and 9 should be within the 4.1V~0.8V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 13 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-014 — Error 14: Fridge Ice maker sensor error

**Knowledge ID:** `SFT-ERROR-014`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 14; Fridge Ice maker sensor error; Fridge Ice maker sensor error diagnostic.  

**Meaning:** Service error **14** is labeled **Fridge Ice maker sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between MAIN PCB CN90 3↔ 8 should be within 4.5V~1.0V.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 14 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-015 — Error 15: Ice room sensor error

**Knowledge ID:** `SFT-ERROR-015`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 15; Ice room sensor error; Ice room sensor error diagnostic.  

**Meaning:** Service error **15** is labeled **Ice room sensor error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between MAIN PCB CN30 10↔ 11should be within 4.5V~1.0V.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 15 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-016 — Error 16: 

**Knowledge ID:** `SFT-ERROR-016`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 16; ;  diagnostic.  

**Meaning:** Service error **16** is labeled **** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the sensor is open or shorted The voltage between the Main PCB CN30 pins 7 and 8 should be within the 4.1V~0.8V range.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 16 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-021 — Error 21: 

**Knowledge ID:** `SFT-ERROR-021`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 21; ;  diagnostic.  

**Meaning:** Service error **21** is labeled **** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The voltage of the MAIN PCB CN74 1↔4: should be between 7V~12V.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 21 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-022 — Error 22: 

**Knowledge ID:** `SFT-ERROR-022`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 22; ;  diagnostic.  

**Meaning:** Service error **22** is labeled **** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The voltage of the MAIN PCB CN74 1↔3: should be between 7V~12V.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 22 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-023 — Error 23: 

**Knowledge ID:** `SFT-ERROR-023`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 23; ;  diagnostic.  

**Meaning:** Service error **23** is labeled **** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The voltage of the MAIN PCB CN74 1↔6: should be between 7V~12V.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 23 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-024 — Error 24: 

**Knowledge ID:** `SFT-ERROR-024`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 4.  
**Customer phrasing:** Error 24; ;  diagnostic.  

**Meaning:** Service error **24** is labeled **** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** After separating MAIN PCB CN70_1 wire from PCB, resistance value between CN70_1-7 ↔ 3 shall be 63(230) ohm ± 7%. (Resistance value is varied by input power) 0 ohm : heater short, ∞ ohm : wire/ bimetal open (Must power off)

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 24 on printed page 4 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-029 — Error 29: Convertible zone defrost error

**Knowledge ID:** `SFT-ERROR-029`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 29; Convertible zone defrost error; Convertible zone defrost error diagnostic.  

**Meaning:** Service error **29** is labeled **Convertible zone defrost error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** After separating MAIN PCB CN70 wire from PCB, resistance value between CN70_1-7 ↔ 1 shall be 63(230) ohm ± 7%. (Resistance value is varied by input power) 0 ohm : heater short, ∞ ohm : wire/ bimetal open (Must power off)

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 29 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-031 — Error 31: Convertible zone fan error

**Knowledge ID:** `SFT-ERROR-031`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 31; Convertible zone fan error; Convertible zone fan error diagnostic.  

**Meaning:** Service error **31** is labeled **Convertible zone fan error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The voltage of the MAIN PCB CN74 1↔5: should be between 7V~12V.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 31 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-035 — Error 35: Freezer low regist

**Knowledge ID:** `SFT-ERROR-035`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 35; Freezer low regist; Freezer low regist diagnostic.  

**Meaning:** Service error **35** is labeled **Freezer low regist** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** ERROR_Freezer low regist

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 35 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-037 — Error 37: Convertible zone low regist

**Knowledge ID:** `SFT-ERROR-037`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 37; Convertible zone low regist; Convertible zone low regist diagnostic.  

**Meaning:** Service error **37** is labeled **Convertible zone low regist** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** ERROR_Convertible zone low regist

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 37 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-039 — Error 39: Ice maker function error

**Knowledge ID:** `SFT-ERROR-039`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 39; Ice maker function error; Ice maker function error diagnostic.  

**Meaning:** Service error **39** is labeled **Ice maker function error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** After changing the Ice Maker(R), plug the refrigerator power code again, and check the operation.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 39 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-040 — Error 40: Ice maker fan error

**Knowledge ID:** `SFT-ERROR-040`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 40; Ice maker fan error; Ice maker fan error diagnostic.  

**Meaning:** Service error **40** is labeled **Ice maker fan error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The voltage of MAIN PCB CN52-1↔ 6: shall be between 7V~12V

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 40 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-041 — Error 41: MAIN < - > Panel Comm error

**Knowledge ID:** `SFT-ERROR-041`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 41; MAIN < - > Panel Comm error; MAIN < - > Panel Comm error diagnostic.  

**Meaning:** Service error **41** is labeled **MAIN < - > Panel Comm error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Actually, If there is not a problem, it is desirable to replace Main and Panel PCB With the oscilloscope after a cable problem confirming.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 41 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-044 — Error 44: MAIN < - > INV Comm error

**Knowledge ID:** `SFT-ERROR-044`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 44; MAIN < - > INV Comm error; MAIN < - > INV Comm error diagnostic.  

**Meaning:** Service error **44** is labeled **MAIN < - > INV Comm error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Actually, If there is not a problem, it is desirable to replace Main and Inverter PCB With the oscilloscope after a cable problem confirming.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 44 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-046 — Error 46: I/O Expander Comm error

**Knowledge ID:** `SFT-ERROR-046`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 46; I/O Expander Comm error; I/O Expander Comm error diagnostic.  

**Meaning:** Service error **46** is labeled **I/O Expander Comm error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** It is desirable to replace Main PCB.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 46 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-061 — Error 61: Ice duct heater error

**Knowledge ID:** `SFT-ERROR-061`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 61; Ice duct heater error; Ice duct heater error diagnostic.  

**Meaning:** Service error **61** is labeled **Ice duct heater error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** After separating MAIN PCB CN51 wire from PCB, resistance value between CN51 4↔6 shall be 135 ohm ± 7%. (Resistance value is varied by input power) 0 ohm : heater short, ∞ ohm : (Must power off)

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 61 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-065 — Error 65: Ice bucket heater error

**Knowledge ID:** `SFT-ERROR-065`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 65; Ice bucket heater error; Ice bucket heater error diagnostic.  

**Meaning:** Service error **65** is labeled **Ice bucket heater error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** After separating MAIN PCB CN51 wire from PCB, resistance value between CN51 4↔7 wire shall be 135 ohm± 7%. 0 ohm : heater short, ∞ Ohm : wire.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 65 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-066 — Error 66: Door handle heater error

**Knowledge ID:** `SFT-ERROR-066`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 66; Door handle heater error; Door handle heater error diagnostic.  

**Meaning:** Service error **66** is labeled **Door handle heater error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** After separating MAIN PCB CN51 wire from PCB, resistance value between CN51 1↔2 wire shall be 135 ohm± 7%. 0 ohm : heater short, ∞ Ohm : wire.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 66 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-071 — Error 71: Freezer abnormal temp. error

**Knowledge ID:** `SFT-ERROR-071`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 71; Freezer abnormal temp. error; Freezer abnormal temp. error diagnostic.  

**Meaning:** Service error **71** is labeled **Freezer abnormal temp. error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** The temperature has been abnormally increased. Check if the door has been open for a long time or if hot food has been stored in the compartment. If the reason for the error is removed, the error code disappears after a pre-determined period of time.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 71 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-072 — Error 72: Fridge abnormal temp. error

**Knowledge ID:** `SFT-ERROR-072`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 72; Fridge abnormal temp. error; Fridge abnormal temp. error diagnostic.  

**Meaning:** Service error **72** is labeled **Fridge abnormal temp. error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the door has been open for a long time or if hot food has been stored in the compartment. If the reason for the error is removed, the error code disappears after a pre- determined period of time.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 72 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-073 — Error 73: Convertible zone chill error

**Knowledge ID:** `SFT-ERROR-073`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 5.  
**Customer phrasing:** Error 73; Convertible zone chill error; Convertible zone chill error diagnostic.  

**Meaning:** Service error **73** is labeled **Convertible zone chill error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the door has been open for a long time or if hot food has been stored in the compartment. If the reason for the error is removed, the error code disappears after a pre- determined period of time.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 73 on printed page 5 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-081 — Error 81: COMP run error

**Knowledge ID:** `SFT-ERROR-081`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 6.  
**Customer phrasing:** Error 81; COMP run error; COMP run error diagnostic.  

**Meaning:** Service error **81** is labeled **COMP run error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check the soldering status of the inverter PCB. (Check if any parts have short-circuited). Check if the DC 15V output is less than 13.5V. Check the Comp and Cycle.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 81 on printed page 6 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-082 — Error 82: COMP IPM fault

**Knowledge ID:** `SFT-ERROR-082`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 6.  
**Customer phrasing:** Error 82; COMP IPM fault; COMP IPM fault diagnostic.  

**Meaning:** Service error **82** is labeled **COMP IPM fault** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check the soldering status of the inverter PCB. (Check if any parts have short-circuited). Check if the DC 15V output is less than 13.5V. Check the Comp and Cycle.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 82 on printed page 6 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-083 — Error 83: COMP current error

**Knowledge ID:** `SFT-ERROR-083`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 6.  
**Customer phrasing:** Error 83; COMP current error; COMP current error diagnostic.  

**Meaning:** Service error **83** is labeled **COMP current error** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check the compressor wire connections. Check the soldering status of the inverter PCB. (Check if any parts have short-circuited). Check the Comp and Cycle.

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 83 on printed page 6 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-084 — Error 84: COMP Motor stall

**Knowledge ID:** `SFT-ERROR-084`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 6.  
**Customer phrasing:** Error 84; COMP Motor stall; COMP Motor stall diagnostic.  

**Meaning:** Service error **84** is labeled **COMP Motor stall** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check if the compressor and the Cycle is normal.Check the input voltage. Check the soldering of the inverter PCB. (Check if any parts have short- circuited.)

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 84 on printed page 6 of *Fast Track Troubleshooting* is the source for component location or connector views where present.

### SFT-ERROR-085 — Error 85: COMP low voltage

**Knowledge ID:** `SFT-ERROR-085`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 6.  
**Customer phrasing:** Error 85; COMP low voltage; COMP low voltage diagnostic.  

**Meaning:** Service error **85** is labeled **COMP low voltage** in the printed Samsung diagnostic table. It identifies the named diagnostic category; it does not establish a final part-failure diagnosis by itself.

**Documented diagnostic method, qualified technicians only:** Check the input voltage. (This error occurs when the input voltage is AC 106 V or lower.)

**Expected result and limits:** Follow only the printed checks and values above; the table does not independently certify the cause from the error name alone.

**Visual reference:** The **unlabeled illustration** in the “Location Image” column beside error 85 on printed page 6 of *Fast Track Troubleshooting* is the source for component location or connector views where present.
