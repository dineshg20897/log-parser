import csv
import socket
import logging
from collections import defaultdict
from os import path

# Set up logging to record important information and errors
logging.basicConfig(filename='process_flow_logs.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_lookup_table(lookup_file):
    """
    Load the lookup table from a CSV file into a dictionary where
    the key is a tuple (dstport, protocol) and the value is the tag.
    """
    if not path.exists(lookup_file):
        logging.error(f"Lookup table file '{lookup_file}' not found.")
        raise FileNotFoundError(f"Lookup table file '{lookup_file}' not found.")
    
    lookup_table = {}
    
    with open(lookup_file, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # Skip the header
        if not header:
            logging.error(f"Lookup table file '{lookup_file}' is empty or has an invalid format.")
            raise ValueError(f"Lookup table file '{lookup_file}' is empty or has an invalid format.")
        
        for row in reader:
            # Skip empty or invalid rows silently
            if not row or len(row) < 3 or all(not item.strip() for item in row):
                continue  # Skip empty or invalid rows
            
            dstport = row[0].strip()
            protocol = row[1].strip().lower()  # Case insensitive for protocol
            tag = row[2].strip()
            lookup_table[(dstport, protocol)] = tag
    
    logging.info(f"Loaded {len(lookup_table)} mappings from the lookup table.")
    return lookup_table


def process_flow_logs(flow_log_file, lookup_table):
    """
    Process the flow log entries and tag them based on the lookup table.
    """
    if not path.exists(flow_log_file):
        logging.error(f"Flow log file '{flow_log_file}' not found.")
        raise FileNotFoundError(f"Flow log file '{flow_log_file}' not found.")
    
    tag_counts = defaultdict(int)
    port_protocol_counts = defaultdict(int)
    
    with open(flow_log_file, mode='r') as file:
        for line in file:
            fields = line.split()
            
            # Validate that the line has the required number of fields
            if len(fields) < 14:
                continue  # Skip malformed lines
            
            # Parse fields into variables
            version, account_id, interface_id, srcaddr, dstaddr, \
            srcport, dstport, protocol_number, packets, bytes_transferred, \
            start_time, end_time, action, log_status = fields
            
            # Resolve the protocol name dynamically using the protocol number
            protocol_name = get_protocol_name(protocol_number)
            
            # Check if the dstport/protocol exists in the lookup table
            tag = lookup_table.get((dstport, protocol_name), "Untagged")
            tag_counts[tag] += 1
            
            # Count port/protocol combinations
            port_protocol_counts[(dstport, protocol_name)] += 1
    
    logging.info("Finished processing flow logs.")
    return tag_counts, port_protocol_counts


def get_protocol_name(protocol_number):
    """
    Convert protocol number to protocol name dynamically using the socket library.
    If not found, return 'unknown'.
    """
    try:
        for name, number in vars(socket).items():
            if name.startswith('IPPROTO_') and number == int(protocol_number):
                return name.lower().split('_')[-1]
    except (OSError, ValueError):
        logging.warning(f"Unknown protocol number: {protocol_number}")
        return 'unknown'
    

def write_output(tag_counts, port_protocol_counts, output_file):
    """
    Write the counts of tags and port/protocol combinations to an output file.
    """
    try:
        with open(output_file, mode='w') as file:
            file.write("Tag Counts:\n")
            file.write("Tag,Count\n")
            sorted_counts = sorted(tag_counts.items(), key=lambda x: x[1])
            for tag, count in sorted_counts:
                file.write(f"{tag},{count}\n")
            
            file.write("\nPort/Protocol Combination Counts:\n")
            file.write("Port,Protocol,Count\n")
            sorted_protocols = sorted(port_protocol_counts.items(), key=lambda x: (x[1], int(x[0][0])))
            for (port, protocol), count in sorted_protocols:
                file.write(f"{port},{protocol},{count}\n")
        
        logging.info(f"Output successfully written to '{output_file}'.")
    
    except Exception as e:
        logging.error(f"Error writing to output file '{output_file}': {e}")
        raise


def log_parser(lookup_file, flow_log_file, output_file):
    """
    Driver Function, 
    """
    try:
        # Load lookup table
        lookup_table = load_lookup_table(lookup_file)
        
        # Process flow logs
        tag_counts, port_protocol_counts = process_flow_logs(flow_log_file, lookup_table)
        
        # Write the output to a file
        write_output(tag_counts, port_protocol_counts, output_file)
    
    except FileNotFoundError as fnfe:
        logging.error(fnfe)
    except ValueError as ve:
        logging.error(ve)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


log_parser(lookup_file = 'lookup_table.csv', flow_log_file = 'flow_log.log', output_file = 'output.txt')