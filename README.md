# CleanClip

CleanClip is a small desktop utility that sanitizes text copied to the clipboard. It replaces
sensitive information such as credit card numbers and e-mail addresses with configurable
placeholders so that you can safely paste data in public places.

## Features

- One-click clipboard scrubbing using a compact ttkbootstrap interface.
- Regex based detection of sensitive information with sensible defaults.
- Built-in editor (gear icon) to adjust patterns and placeholders.
- Persistent configuration stored in `~/.cleanclip/patterns.json`.

## Installation

1. Create and activate a Python 3.9+ virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application from the repository root:

```bash
python main.py
```

1. Copy any text to your clipboard.
2. Press **Clean Clipboard** to sanitize the clipboard contents.
3. Use the gear button to adjust the regex patterns. Each line follows the format
   `pattern -> placeholder`. Lines beginning with `#` are ignored. The configuration is
   saved for future sessions when you press **Save** in the editor dialog.

## Testing

The repository includes a small test suite that verifies the sanitization helpers. Execute it with:

```bash
pytest
```

## Configuration File

The configuration is stored as JSON at `~/.cleanclip/patterns.json`. The editor dialog manages this
file for you, but you can also edit it manually if necessary.

## License

CleanClip is distributed under the terms of the MIT License. See [LICENSE](LICENSE) for details.
