# Log Parser - README

## Project Overview

This Python script processes flow log data and assigns tags based on a lookup table provided in CSV format. The destination port and protocol from each flow log entry are used to match tags, which are defined in the lookup table. The script generates two sections of outputs written in a single file:
1. A count of matches for each tag.
2. A count of matches for each port and protocol combination.

This tool is designed to work with AWS VPC Flow Logs **version 2**. It can handle large flow log files and lookup tables with up to 10,000 mappings, providing a scalable solution for log analysis.

### Key Features:
- **No additional python libraries needed** so the code works on basic python installation.
- **Tagging of flow log entries** based on destination port and protocol.
- **Dynamic protocol resolution**, avoiding hardcoded values for protocols.
- **Efficient handling** of large flow log files (can be realistically **up to or more than 10 MB** in size) and lookup tables (can have up to **10,000 mappings**, but the program can handle larger files without performance issues).
- **Logging system** to track the process and flag any issues during execution.
- **Protocol Matching**: is done dynamically so it supports multiple protocols and not just (TCP = 6, UDP = 17, ICMP = 1). If the protocol is not recognized, the entry will be tagged as `Untagged`.

---

## Assumptions

- **Flow Log Format**: The script only supports **AWS VPC Flow Logs version 2**. Any other formats (e.g., custom formats or versions) are not supported.
- **Plain Text Files**: The input flow log and lookup table must be in **plain text format** (ASCII). Any other file encodings or formats will not be processed.
- **Flow Log Data**: It is assumed that the flow log contains valid entries with the following structure:
  ```
  version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
  ```
  For example:
  ```
  2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
  ```
  - **Version**: Only version 2 is supported.
  
---

## Python Installation and Dependencies

This script is written in **Python 3.x** and requires **no external libraries** beyond Python's standard library. This ensures that the script can be run on any system with Python 3.x installed without needing to install additional dependencies.

### Libraries Used (Standard):
- **csv**: For parsing the CSV lookup table.
- **socket**: For protocol number resolution.
- **logging**: For logging warnings, errors, and process information.
- **collections**: For counting occurrences of tags and port/protocol combinations.

---

## Running the Program

### Step-by-Step Instructions

1. **Ensure Python 3.x is installed**:
   - You can check your Python version using the command:
     ```bash
     python --version
     ```

2. **Prepare Input Files**:
   - Ensure the **flow log file** has valid entries and multiple entries are **seperated by a new line**.
   - Ensure the **lookup table** is formatted as follows:
     ```
     dstport,protocol,tag
     25,tcp,sv_P1
     443,tcp,sv_P2
     110,tcp,email
     993,tcp,email
     ```
   - The files should be placed in the same directory as the script.

3. **Run the Script**:
   - Download the `Log_Parser.py` file.
   - Ensure the lookup table (CSV format) and flow log (plain text format) are available in the same directory as the script.
   - Open a terminal or command prompt in the directory containing the script.
   - Run the following command:
   ```bash
   python Log_Parser.py
   ```

4. **View the Output**:
   - The script will generate two output files:
     - `output.txt`: Contains the counts for tags and port/protocol combinations.
     - `process_flow_logs.log`: Captures the logs and process details.

5. You can customize the inputs by modifying the call in the script:
```python
log_parser(lookup_file='lookup_table.csv', flow_log_file='flow_log.log', output_file='output.txt')
```

### Output File Details:

- **output.txt** will have the following sections:
  - **Tag Counts**:
    ```
    Tag Counts:
    Tag,Count
    sv_P1,2
    email,3
    Untagged,5
    ```
  - **Port/Protocol Combination Counts**:
    ```
    Port/Protocol Combination Counts:
    Port,Protocol,Count
    25,tcp,1
    443,tcp,1
    110,tcp,1
    993,tcp,1
    ```
---

## Tests Performed

To ensure the robustness of the script, the following tests were conducted:

1. **Basic Functionality Test**:
   - Provided a small sample of flow log entries and lookup table mappings to verify that the script correctly tags entries and counts tags and port/protocol combinations.

2. **Large File Test**:
   - Simulated a large flow log file (10+ MB) and a lookup table with more than 10,000 entries. The script performed efficiently without memory issues, and outputs were generated as expected.

3. **Invalid Data Test**:
   - Tested with invalid entries (e.g., missing fields, invalid protocols) to verify the script's error-handling mechanism. The logging system appropriately flagged issues.

4. **Edge Cases**:
   - Tested uncommon protocols and entries with unknown ports or protocols to ensure that these are tagged as `Untagged` and handled gracefully.

---

## Other Analysis

- **Scalability**: The script was designed with scalability in mind, capable of processing large log files and lookup tables without significant performance degradation.
- **Error Handling**: Through the use of a logging system, the script ensures that errors such as file-not-found or invalid data formats are caught and logged without crashing the program.
- **Dynamic Protocol Support**: Instead of hardcoding protocols, the script dynamically resolves protocol numbers, making it flexible for future protocols.
- **Modularity**: Each major step (loading lookup table, processing flow logs, and writing output) is encapsulated in separate functions for easier debugging and maintenance.

---

## Logging and Error Handling

- **Logging**:
  - The script uses Python's `logging` module to log key events such as file loading, processing flow logs, and any errors encountered.
  - Logs are written to `process_flow_logs.log`.

- **Error Handling**:
  - The script checks for the existence of input files and logs an error if any required files are missing.
  - Invalid or malformed rows in the lookup table are skipped, and warnings are logged.
  - If a protocol number cannot be resolved, it is logged as a warning, and the protocol is treated as `unknown`.

---

## Code Structure

1. **`load_lookup_table(lookup_file)`**:
   - Reads the lookup table from the CSV file and stores port/protocol-to-tag mappings in a dictionary.
   
2. **`process_flow_logs(flow_log_file, lookup_table)`**:
   - Processes each flow log entry, extracts relevant fields (destination port, protocol), and applies the appropriate tag using the lookup table.

3. **`get_protocol_name(protocol_number)`**:
   - Resolves protocol numbers (TCP, UDP, ICMP) to their names dynamically. Returns "unknown" for unrecognized protocols.

4. **`write_output(tag_counts, port_protocol_counts, output_file)`**:
   - Writes the results, including tag counts and port/protocol combination counts, to the output file.

5. **`log_parser(lookup_file, flow_log_file, output_file)`**:
   - Is the main driver function. Call this function to get the whole function running, with the flexibility to provide custom file names as arguments.

---

## Known Limitations

- **Flow Log Version**: The program supports only **AWS VPC Flow Logs version 2**. It will not work with custom or other versions.

---

## Future Improvements

- **Multi-threading for Larger Files**: For extremely large files, multi-threading could be implemented to speed up processing.
- **Containerizing the Project**: For ease of portability, code security, isolation from hardware and consistency across hosts.

---

## Conclusion

This program efficiently processes AWS VPC flow logs, applies tags based on destination port and protocol, and outputs both tag counts and port/protocol combination counts. With robust error handling, logging, and support for large files, it provides a scalable solution for flow log analysis.
