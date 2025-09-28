import random
import os

# List of categories and their corresponding filenames
categories = [
    "Subject",
    "FacialExpression",
    "Clothing",
    "Situation",
    "Medium",
    "Style",
    "AdditionalDetails",
    "Color",
    "Lighting",
    "Remarks"
]

# Prompt template (order of parts)
def build_prompt(parts):
    # Filter out empty parts and join with ", "
    return ", ".join(part for part in parts if part)

def find_case_insensitive_file(base_name):
    """Find a file with case-insensitive matching"""
    directory = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(directory):
        if file.lower() == base_name.lower():
            return file
    return None

def load_options(filename):
    """Load lines from a txt file, stripping whitespace and ignoring empty lines"""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_unique_filename(base_name):
    """Return filename that does not clash with existing files."""
    if not os.path.exists(base_name):
        return base_name

    name, ext = os.path.splitext(base_name)
    counter = 2
    while True:
        candidate = f"{name}{counter}{ext}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1

def main():
    num_prompts = 100
    output_file = get_unique_filename("generated_prompts.txt")
    
    # Load all category options
    options = {}
    for cat in categories:
        base_filename = f"{cat}.txt"
        actual_filename = find_case_insensitive_file(base_filename)
        
        if not actual_filename:
            print(f"Error: Could not find {base_filename} (case-insensitive match)")
            options[cat] = []
            continue
            
        try:
            options[cat] = load_options(actual_filename)
            print(f"Loaded {len(options[cat])} options from {actual_filename}")
        except Exception as e:
            print(f"Error loading {actual_filename}: {str(e)}")
            options[cat] = []
    
    # Ensure we have at least one option for each category
    for cat in categories:
        if not options[cat]:
            print(f"Error: No options found for {cat}. Please check {cat}.txt")
            return
    
    with open(output_file, "w", encoding="utf-8") as f:
        for _ in range(num_prompts):
            parts = []
            for cat in categories:
                choice = random.choice(options[cat])
                parts.append(choice)
            
            # Build prompt
            prompt_text = build_prompt(parts)
            
            # A1111 format
            line = (
                f'--prompt "{prompt_text}" \
--negative_prompt "deformed, ugly, creepy, mutation" \
--steps 20 --cfg_scale 9.5 \
--sampler_name "DPM++ 2M Karras" --seed -1 \
--width 1024 --height 1024\n'
            )
            f.write(line)
    
    print(f"\nGenerated {num_prompts} prompts saved to {output_file}")
    print("Example prompt:")
    print(line.strip())

if __name__ == "__main__":
    main()
