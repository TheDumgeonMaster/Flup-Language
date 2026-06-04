import os
import re
import subprocess  # Added to execute the generated Python files

# Global state tracker for our multi-line variable allocation
c_var_mem = "emptyVariable"
indents = 0

def transpile_flup_line(line: str) -> str:
    global c_var_mem
    global indents

    trimmed = line.strip()

    if not trimmed:
        return ""

    def fix_function_calls(text: str) -> str:
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*):\s*([^,:\n]+(?:,\s*[^,:\n]+)*)'
        return re.sub(pattern, lambda m: f"{m.group(1)}({m.group(2).strip()})", text)

    if trimmed.startswith("outln:"):
        message = trimmed[len("outln:"):].strip()
        message = fix_function_calls(message)
        return ("  " * indents) + f"print({message})"
    
    if trimmed.startswith("nval:"):
        message = trimmed[len("nval:"):].strip()
        c_var_mem = message
        return ("  " * indents) + f"{message} = None"
    
    if trimmed.startswith("svald:"):
        message = trimmed[len("svald:"):].strip()
        message = fix_function_calls(message)
        return ("  " * indents) + f"{c_var_mem} = {message}"
    
    if trimmed.startswith("cn:"):
        message = trimmed[len("cn:"):].strip()
        message = fix_function_calls(message)
        indents += 1
        return ("  " * (indents - 1)) + f"if {message}:"
    
    if trimmed.startswith("cne:"):
        return ("  " * (indents - 1)) + "else:"
    
    if trimmed.startswith("cnie:"):
        message = trimmed[len("cnie:"):].strip()
        message = fix_function_calls(message)
        return ("  " * (indents - 1)) + f"elif {message}:"
    
    if trimmed.startswith("fn:"):
        indents -= 1
        return ("  " * indents)
    
    if trimmed.startswith("lp:"):
        message = trimmed[len("lp:"):].strip()
        indents += 1
        return ("  " * (indents - 1)) + f"for i{indents} in range({message}):"
    
    if trimmed.startswith("wlp:"):
        message = trimmed[len("wlp:"):].strip()
        message = fix_function_calls(message)
        indents += 1
        return ("  " * (indents - 1)) + f"while {message}:"
    
    if trimmed.startswith("in:"):
        message = trimmed[len("in:"):].strip()
        return ("  " * indents) + f"{c_var_mem} = input({message})"
    
    if trimmed.startswith("ini:"):
        message = trimmed[len("ini:"):].strip()
        return ("  " * indents) + f"{c_var_mem} = int(input({message}))"
    
    if trimmed.startswith("fnc:"):
        content = trimmed[len("fnc:"):].strip()
        func_name, params = content.split(":", 1)
        func_name = func_name.strip()
        params = params.strip()
        tf = f"def {func_name}({params}):"
        result = ("  " * indents) + tf
        indents += 1
        return result
    
    if trimmed.startswith("rtn:"):
        message = trimmed[len("rtn:"):].strip()
        message = fix_function_calls(message)
        return ("  " * indents) + f"return {message}"
    
    if trimmed.startswith("rnd:"):
        message = trimmed[len("rnd:"):].strip()
        return ("  " * indents) + f"{c_var_mem} = random.randint({message})"
    
    if trimmed.startswith("wt:"):
        message = trimmed[len("wt:"):].strip()
        return ("  " * indents) + f"time.sleep({int(message) * 0.001})"

    return line


def compile_flup_to_python(input_file: str, output_file: str) -> bool:
    global indents
    indents = 0 # Reset indent tracking on fresh compiles
    
    if not input_file:
        print("\n[Error] Source path not set! Use: fpath [filename.flup]")
        return False
    if not output_file:
        print("\n[Error] Destination path not set! Use: opath [filename.py]")
        return False

    if not os.path.exists(input_file):
        print(f"\n[Error] The file '{input_file}' does not exist.")
        return False

    with open(input_file, "r") as f:
        flup_lines = f.readlines()

    python_lines = [
        "import random",
        "import math",
        "import time"
    ]
    for line in flup_lines:
        python_lines.append(transpile_flup_line(line))

    with open(output_file, "w") as f:
        f.write("\n".join(python_lines))

    print(f"[Success] Transpiled '{input_file}' into '{output_file}'!")
    return True

def run_python_script(output_file: str):
    if not output_file:
        print("\n[Error] Output script path not specified.")
        return
    if not os.path.exists(output_file):
        print(f"\n[Error] Compiled file '{output_file}' not found. Transpile it first using 'tp'.")
        return
        
    print(f"\n--- Running {output_file} ---")
    try:
        # Executes the generated script in your current terminal workspace
        subprocess.run(["python", output_file], check=True)
    except subprocess.CalledProcessError:
        print("\n[Runtime Error] The Python script crashed during execution.")
    except Exception as e:
        print(f"\n[Error] Could not invoke Python execution environment: {e}")
    print("----------------------------")


if __name__ == "__main__":
    print("====================================")
    print("      FLUP INTERACTIVE WORKSPACE    ")
    print("====================================")
    print("Commands:")
    print("  fpath [file.flup] -> Set source code path")
    print("  opath [file.py]   -> Set compilation target path")
    print("  tp                -> Transpile Flup to Python")
    print("  run               -> Execute compiled Python script")
    print("  frun              -> Transpile and instantly execute")
    print("  exit              -> Terminate workspace environment\n")

    input_path = ""
    output_path = ""

    while True:
        # Prompt tracks current path configuration settings dynamically
        f_status = input_path if input_path else "Not Set"
        o_status = output_path if output_path else "Not Set"
        
        cmd_entry = input(f"Flup-CLI [In: {f_status} | Out: {o_status}]> ").strip()
        
        if not cmd_entry:
            continue
            
        if cmd_entry.lower() == "exit":
            print("Closing Flup interactive environment. Goodbye!")
            break
            
        elif cmd_entry.startswith("fpath "):
            input_path = cmd_entry[len("fpath "):].strip()
            print(f"Source file target configured: {input_path}")
            
        elif cmd_entry.startswith("opath "):
            output_path = cmd_entry[len("opath "):].strip()
            print(f"Destination output file configured: {output_path}")
            
        elif cmd_entry == "tp":
            compile_flup_to_python(input_path, output_path)
            
        elif cmd_entry == "run":
            run_python_script(output_path)
            
        elif cmd_entry == "frun":
            # Only runs if compilation returns True (success)
            if compile_flup_to_python(input_path, output_path):
                run_python_script(output_path)
                
        else:
            print(f"Unknown instruction: '{cmd_entry}'. Check your command syntax.")