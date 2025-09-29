# A1111 Prompt Generator

This tool generates random prompts for Stable Diffusion's Automatic1111 WebUI by combining elements from different categories.

## Features

- Reads prompt components from text files
- Customizable negative prompts
- Configurable generation settings
- Case-insensitive file handling
- Generates multiple prompts at once
- Saves output to a text file
- Cross-platform compatible

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your settings in `config/settings.txt` (optional)
   - Adjust generation parameters like steps, CFG scale, etc.
   - Default values will be used if not specified

3. Add your prompt options to the text files in the `config/data` directory:
   - Each line should contain one option
   - Empty lines are ignored
   - Files are case-insensitive
   - Edit `NegativePrompt.txt` to customize negative prompts

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

### Prompt Components
Edit the text files in `config/data` to customize the prompt components. The script will automatically detect any changes the next time it runs.

### Negative Prompts
Customize negative prompts by editing `config/data/NegativePrompt.txt`. This file contains terms that guide the AI to avoid certain features in the generated images.

### Generation Settings
Modify `config/settings.txt` to adjust generation parameters:
- `STEPS`: Number of sampling steps (default: 20)
- `CFG_SCALE`: Classifier-free guidance scale (default: 9.5)
- `SAMPLER`: Sampling method (default: "DPM++ 2M Karras")
- `WIDTH`/`HEIGHT`: Output image dimensions (default: 1024x1024)
- `SEED`: Random seed (-1 for random)

Example `settings.txt`:
```
# A1111 WebUI Generation Settings
STEPS=20
CFG_SCALE=9.5
SAMPLER=DPM++ 2M Karras
WIDTH=1024
HEIGHT=1024
SEED=-1
```

## Output Format

The generated prompts follow the A1111 WebUI format and include:
- Randomly selected prompt components
- A standard negative prompt
- Recommended generation settings

## License

This project is open source and available under the [MIT License](LICENSE).
