## Forced modes, ice maker operation and removal procedures

**Original manual:** *Fast Track Troubleshooting*. **Source file:** `repair-guide.pdf`.

### SFT-FORCE-001 — Forced operation and forced defrost modes

**Knowledge ID:** `SFT-FORCE-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 1.  
**Customer phrasing:** What does FD mean?; How do I exit forced defrost?.  

**Technician procedure:** Hold **Freezer + Flex Zone** for **6 seconds**, until the screen goes blank and a beep is heard. Press Flex Zone again to enter mode 1; successive mode selections are shown on the printed panel drawing on page 1. After mode 5 the screen becomes blank; leaving it alone for **1 minute** returns to normal operation.

The diagram explicitly identifies **FD** as defrost with **all heaters on**. The force-operation table gives 24-hour operating time for the displayed FF, FF/r, FF/F and FF/C configurations; valve states depend on the selected configuration. These are deliberate technician operating states, not ordinary temperature recommendations.

**Original PDF visual reference:** See the **unlabeled illustration** under “Force Mode / Defrost” on printed page 1 of *Fast Track Troubleshooting*, which shows the five mode-display states and operating table.

**Exceptions and limits:** The extracted illustration uses display segments to distinguish modes; do not infer an undocumented sequence or valve combination from text alone. Qualified-service boundary applies.

### SFT-ICE-001 — Heat-release ice maker harvest operation and test mode

**Knowledge ID:** `SFT-ICE-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 2.  
**Customer phrasing:** Why does freezer switch to minus fourteen?; Ice maker test button; Why is the ice maker waiting three hours?.  

**Documented harvest logic:** The board checks the eject thermistor on the ice maker head after water filling. When its reading is below **18.5 degrees** for more than **5 seconds**, ice production is treated as completed. Harvest runs when the bucket is not sensed full. If an ice-maker fault mode is detected, operation stops for **3 hours** and rechecks at that interval.

**Technician ICE TEST:** Hold **ICE TEST S/W** for at least **1.5 seconds**. Below **0 degrees**, the heater turns on for about **2 minutes**; above 0 degrees, for **30 seconds**. After the stated 30-second heater stage, the heater switches off and the harvest motor runs in the right direction for about **3 minutes**; the water valve then operates and the test completes. Failure to complete within **6 minutes** causes a fault mode.

**Freezer and ice production:** The sheet states the freezer uses **−14°F** while the ice bucket is not full, returns to its original setting when full, and returns to −14°F as ice is used. Selecting **Ice Off** allows the normal selected freezer temperature to control; if no water is connected and Ice Off is not selected, it stays at −14°F.

**Scope caution:** The first two thermistor temperatures are printed without an explicit unit in this paragraph; do not silently reinterpret them as °F or °C.

### SFT-ICE-REMOVAL-001 — Ice bucket and ice maker removal sequence

**Knowledge ID:** `SFT-ICE-REMOVAL-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 9.  
**Customer phrasing:** How to remove the ice maker?; Ice bucket removal; Where is the duct locking tab?.  

**Scope and safety:** The page contains illustrated technician removal instructions, including a red warning not to damage the tray grommets or refrigerant tube.

**Documented sequence:**
1. Wait **5 minutes** after manual defrost of the freezer and fresh-food compartments, referring to the forced-defrost method in the sheet.
2. Lift and pull out the ice bucket.
3. Remove the wire-housing-cover screw.
4. Remove that cover.
5. Disconnect the ice-maker housing connector.
6. Remove the duct-tray-ice screw.
7. With a flat-blade screwdriver, push the duct right to release the locking tab.
8. Push the refrigerant pipe down slightly and completely separate it from the ice-maker assembly.
9. While pressing the hook, withdraw the ice maker.
10. While pressing down the duct-tray-ice, carefully withdraw and remove the ice maker.

**Original PDF visual reference:** The **unlabeled numbered removal photographs** under “Removal of Ice Bucket and Ice Maker” on printed page 9 of *Fast Track Troubleshooting* show the locking tabs, hook and red-marked areas. The sheet warns that grommets and refrigerant tube can be damaged; do not perform without the technician competence it specifies.

### SFT-AUGER-REMOVAL-001 — Auger fan/motor assembly removal

**Knowledge ID:** `SFT-AUGER-REMOVAL-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 9.  
**Customer phrasing:** How to remove the auger motor?; Fan auger assembly connector.  

**Documented illustrated procedure:** Disconnect the **FAN-AUGER-ASSY connector**. Hold the hook on the bottom of the **FAN-AUGER ASSY** and lift to free it from the locking tab. Continue lifting and remove the assembly from the ice-maker compartment.

**Original PDF visual reference:** The **unlabeled three-step photographs** under “Removal of the Auger Motor Assy” on printed page 9 of *Fast Track Troubleshooting* show the connector, hook, tab and assembly withdrawal. The page's general repair safety restrictions apply.
