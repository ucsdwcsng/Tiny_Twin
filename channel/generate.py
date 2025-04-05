def generate_data_file(filename="data_600000.txt", num_lines=600000):
    """
    Generates a file with 600,000 lines of "1 0.1 0.01 0.02".

    Args:
        filename (str): The name of the file to create.
        num_lines (int): The number of lines to generate.
    """
    try:
        with open(filename, "w") as file:
            for _ in range(num_lines):
                file.write("1 0.01 0.01 0.02 0.03 0.01 0.005 0.006 0.003 0.001 0.001 0.002 0.003 0.004 0.002 0.001 0.002 0.003 0.002 0.0001\n")
        print(f"File '{filename}' generated successfully with {num_lines} lines.")
    except IOError as e:
        print(f"Error generating file: {e}")

# Generate the file
generate_data_file("channel_clean.txt",500000)