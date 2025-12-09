# Command Structure Definition

The following structure defines the format of a command message:

```c
struct md_command {
    uint8_t  command;   // Command identifier
    uint8_t  length;    // Length of the data payload
    uint16_t data[15];  // Data buffer (up to 15 elements)
};
```

Field Descriptions • command: 8‑bit value representing the specific command type. • length: 8‑bit value indicating how many data elements are valid. • data[15]: Array of 16‑bit values containing the payload data.

## Command Constants
```c
#define Detection                 0x0A
#define Calibration               0xA0
#define Raw_Data                  0xAA
#define Threshold                 0xF0
#define Threshold_Adjusted        0x0B
#define Reset_to_Factory          0xB0
#define Reset_Factory_Calibration 0x0C
#define Reset_To_Bootloader       0xFA
#define Get_Firmware_Version      0xFB
#define Bypass                    0x0F
#define Voltage                   0x0D
#define CalButt                   0xD0
```

## Error Codes
```c
#define CalibrationError   0xC0
#define CalSequenceFailed  0x01
#define CalSignalFailed    0x02
```

## Usage Examples

### Example 1: Sending a Calibration Command
```c
struct md_command command;
command.command = Calibration;   // 0xA0
command.length  = 7;            
command.data[0]=detector->posThreshold1;
command.data[1]=detector->negThreshold1;
command.data[2]=detector->posThreshold2;
command.data[3]=detector->negThreshold2;
command.data[4]=detector->midCH1;
command.data[5]=detector->midCH2;
command.data[6]=detector->areaThreshold;
```

### Example 2: Requesting Raw Data
```c
struct md_command command;
command.command = Raw_Data;      // 0xAA
command.length=6;
command.data[0]=detector->ch1Raw;
command.data[1]=detector->ch2Raw;
command.data[2]=detector->ch1AreaP;
command.data[3]=detector->ch1AreaN;
command.data[4]=detector->ch2AreaP;
command.data[5]=detector->ch2AreaN;

// Device will respond with raw sensor data
```
### Example 3: Setting a Threshold
```c
struct md_command command;
command.command = Threshold;     // 0xF0
command.length  = 1;             // One threshold value
command.data[0] = 500;           // Threshold set to 500 units
```

### Example 4: Resetting to Factory Defaults
```c
struct md_command command;
command.command = Reset_to_Factory; // 0xB0
command.length  = 0;                // No payload required
```
### Example 5: Bypass
```c
struct md_command command;
command.command = Bypass;         // 0x0F
command.length  = 1;             // One threshold value
command.data[0] = 1;           // Set Bypass on
```
### Example 6: Calibration Error
```c
struct md_command command;
command.command = CalibrationError;      // 0xC0
command.length  = 1;                     // One threshold value
command.data[0] = CalSequenceFailed;     // Failure Reason
```
### Example 7: Voltage
```c
struct md_command command;
command.command = Votlage;      // 0x0D
command.length  = 1;             // One threshold value
command.data[0] = 500;           // Voltage (uint16_t)
``` 
### Example 7: Calibration Button
```c
struct md_command command;
command.command = CalButt;      // 0xD0
command.length  = 1;             // One threshold value
command.data[0] = 1;           // Button Pressed
```
### Example 5: Getting Firmware Version
```c
struct md_command command;
command.command = Get_Firmware_Version; // 0xFB
command.length  = 3;                    
command.data[0]= major;
command.data[1]= minor;
command.data[2]= bugFix;
``` 
### Example 5: Getting Hardware Version
```c
struct md_command command;
command.command = Get_Hardware_Version; // 0xFC
command.length  = 3;                    
command.data[0]= major;
command.data[1]= minor;
command.data[2]= bugFix;
```