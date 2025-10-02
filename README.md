# A1111 Prompt Generator

This tool generates random prompts for Stable Diffusion's Automatic1111 WebUI by combining elements from different categories, with support for multiple profiles and an intuitive GUI.

## Features

- **Profile Management**: Create, save, and load different prompt generation profiles
- **Interactive GUI**: Intuitive interface for managing prompts and settings
- **Category Management**: Easily add, remove, and reorder prompt categories
- **Direct Editing**: Open and edit prompt files directly from the application
- **Customizable Settings**: Configure generation parameters like steps, CFG scale, and more
- **Case-insensitive File Handling**: Works with any file naming convention
- **Cross-platform**: Runs on Windows, macOS, and Linux

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. The application will automatically create a default profile if none exists.

## Building the Application

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Building on Windows/macOS/Linux

1. Install the build dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python build.py
   ```

3. The built application will be in the `dist` directory:
   - **Windows**: `dist/A1111-Prompt-Generator.exe`
   - **macOS**: `dist/A1111-Prompt-Generator.app`
   - **Linux**: `dist/A1111-Prompt-Generator`

### Customizing the Build

- **Icon**: Place an `.ico` file named `icon.ico` in the project root to use it as the application icon.
- **Version**: Edit `version.txt` to update the application version and metadata.
- **Included Files**: The build script automatically includes the `data` and `profiles` directories. Modify `build.py` if you need to include additional files.

### Distribution

To distribute your application:
1. Zip the contents of the `dist` directory
2. Include a `README.txt` with instructions for your users
3. (Optional) Create an installer using tools like Inno Setup (Windows) or Packages (macOS)

## Profiles

The application supports multiple profiles, each with its own set of categories and prompt files. Profiles are stored in the `config/profiles/` directory.

### Creating a New Profile
1. Click on `File > New Profile`
2. A new empty profile will be created
3. Add categories using the `+` button
4. Save your profile with `File > Save Profile`

### Managing Profiles
- **Save Profile**: Saves changes to the current profile
- **Save Profile As...**: Saves the current profile with a new name
- **Open Profile**: Load an existing profile
- **Delete Profile**: Remove a profile (cannot be undone)

### Profile Structure
Each profile is stored in its own directory with the following structure:
```
ProfileName/
  ├── data/          # Directory for category text files
  └── profile.json   # Contains the list of categories
```

## Categories

Each profile contains a set of categories. Each category is linked to a text file in the profile's `data` directory.

### Adding Categories
1. Click the `+` button
2. Enter a name for the category
3. Choose to create a new file or link an existing one
4. Click OK

### Editing Categories
- Click the pencil icon (✏️) next to a category to edit its content in your default text editor
- Use the up/down arrows to reorder categories
- Use the `-` button to remove selected categories

## Usage

### Generating Prompts
1. Select the number of prompts to generate (default is 100)
2. Adjust generation settings if needed:
   - Steps: Number of diffusion steps
   - CFG Scale: Classifier-free guidance scale
   - Sampler: Sampling method
   - Width/Height: Output dimensions
   - Seed: Random seed (-1 for random)
3. Click the `Generate` button
4. Generated prompts will be saved to the `output` directory with a timestamp

### Settings
Access settings by clicking the gear icon (⚙️) in the top-right corner. This opens the settings file in your default text editor.

### File Management
- **Open Data Folder**: Click the folder icon to open the current profile's data directory
- **Open Output Folder**: Click the output folder icon to view generated prompts

## Customization

### Prompt Components
Each category is linked to a text file in the profile's `data` directory. Edit these files to customize the prompt components:
- Each line should contain one option
- Empty lines are ignored
- Files are case-insensitive
- Changes are detected automatically

### Negative Prompts
Each profile can have its own negative prompts. Edit the `NegativePrompt.txt` file in the profile's `data` directory to customize negative prompts for that profile.

### Settings
You can customize generation settings in two ways:
1. Through the UI (recommended)
2. By manually editing `config/settings.txt`

## Tips

- **Organization**: Create different profiles for different types of generations (e.g., portraits, landscapes, characters)
- **Backup**: The `config/profiles` directory is not tracked by git by default. Make sure to back up your profiles
- **Sharing**: To share a profile, simply copy the profile directory from `config/profiles`

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
