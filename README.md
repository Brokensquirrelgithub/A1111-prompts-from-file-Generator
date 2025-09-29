# A1111 Prompt Generator

This tool generates random prompts for Stable Diffusion's Automatic1111 WebUI by combining elements from different categories.

## Features

- Reads prompt components from text files
- Case-insensitive file handling
- Generates multiple prompts at once
- Saves output to a text file
- Cross-platform compatible

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your prompt options to the text files in the `config/data` directory.
   - Each line should contain one option
   - Empty lines are ignored
   - Files are case-insensitive

## Usage

Run the script:
```bash
python main.py
```

This will:
1. Read all the text files from the `config/data` directory
2. Generate 100 random prompts
3. Save them to `output/generated_prompts.txt` (or with an incremented number if the file exists)

## Customization

Edit the text files in `config/data` to customize the prompt components. The script will automatically detect any changes the next time it runs.

## Output Format

The generated prompts follow the A1111 WebUI format and include:
- Randomly selected prompt components
- A standard negative prompt
- Recommended generation settings

## License

This project is open source and available under the [MIT License](LICENSE).
