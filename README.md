# Genesis

A collection of useful command-line tools written in Python.

## Tools

### Emoji Hide Tool

`emoji_hide.py` provides a simple emoji steganography tool to hide and reveal text inside emoji strings using zero-width characters.

#### Features

- Encode text messages into emoji strings
- Decode hidden messages from emoji strings
- Web interface for easy use
- Command-line interface for scripting

#### Usage

**Command Line:**

```bash
# Encode a message
python3 emoji_hide.py encode "secret message"

# Encode with custom cover emoji
python3 emoji_hide.py encode "secret message" --cover "😀😃😄"

# Decode a message
python3 emoji_hide.py decode "<encoded emoji text>"

# Run self-test
python3 emoji_hide.py test
```

**Web Interface:**

```bash
python3 emoji_hide.py serve
```

Open the web interface at http://localhost:3000 and use the encode/decode forms. The default encoding uses a single emoji (`😀`) as the cover.

### Terminal Agent

A quick and effective command executor that runs in the terminal.

#### Usage

Run the agent:

```bash
python3 agent.py
```

Or make it executable and run:

```bash
chmod +x agent.py
./agent.py
```

The agent will read commands from stdin (one per line). You can pipe commands from chat or type them interactively.

Type 'exit' to quit.

The agent executes shell commands, handles errors, and attempts adjustments (e.g., retries with sudo if failed).

## Requirements

- Python 3.6+

## Installation

Clone the repository:

```bash
git clone https://github.com/soydoraeldroa-arch/Genesis.git
cd Genesis
```

No additional dependencies required - uses only Python standard library.

## License

[Add license information here]
