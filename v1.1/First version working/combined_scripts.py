import os

def is_text_file(filename):
    """Check if the file is a text file based on its extension."""
    text_extensions = ['.txt']
    _, ext = os.path.splitext(filename)
    return ext.lower() in text_extensions

def combine_scripts(output_filename='combined_scripts.txt'):
    """Combine all non-text script files in the current directory into one text file."""
    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    
    # Filter out text files and directories
    script_files = [
        file for file in files
        if os.path.isfile(os.path.join(current_dir, file)) and not is_text_file(file)
    ]
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for script in script_files:
            outfile.write(f'"{script}":\n\n')
            try:
                with open(script, 'r', encoding='utf-8') as infile:
                    code = infile.read()
                outfile.write(code)
            except Exception as e:
                outfile.write(f"# Error reading {script}: {e}\n")
            outfile.write('\n\n\n')  # Three blank lines between scripts
    
    print(f"All scripts have been combined into '{output_filename}'.")

if __name__ == "__main__":
    combine_scripts()
