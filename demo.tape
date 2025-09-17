# VHS documentation
#
# Output:
#   Output <path>.gif               Create a GIF output at the given <path>
#   Output <path>.mp4               Create an MP4 output at the given <path>
#   Output <path>.webm              Create a WebM output at the given <path>
#
# Require:
#   Require <string>                Ensure a program is on the $PATH to proceed
#
# Settings:
#   Set FontSize <number>           Set the font size of the terminal
#   Set FontFamily <string>         Set the font family of the terminal
#   Set Height <number>             Set the height of the terminal
#   Set Width <number>              Set the width of the terminal
#   Set LetterSpacing <float>       Set the font letter spacing (tracking)
#   Set LineHeight <float>          Set the font line height
#   Set LoopOffset <float>%         Set the starting frame offset for the GIF loop
#   Set Theme <json>                Set the theme of the terminal
#   Set Padding <number>            Set the padding of the terminal
#   Set Framerate <number>          Set the framerate of the recording
#   Set PlaybackSpeed <float>       Set the playback speed of the recording
#   Set MarginFill <hex-color>      Set the color of the margin
#   Set Margin <number>             Set the size of the margin
#   Set BorderRadius <number>       Set terminal border radius, in pixels
#   Set WindowBar <string>          Set window bar type (one of: Rings, RingsRight, Colorful, ColorfulRight)
#   Set WindowBarSize <number>      Set window bar size, in pixels. Default is 40.
#   Set TypingSpeed <time>          Set the typing speed of the terminal. Default is 50ms.
#
# Sleep:
#   Sleep <time>                    Sleep for a set amount of <time>
#
# Type:
#   Type[@<time>] "<characters>"    Type <characters> into the terminal with a
#                                   <time> delay between each character
#
# Keys:
#   Backspace[@<time>] [number]     Press the Backspace key
#   Down[@<time>] [number]          Press the Down key
#   Enter[@<time>] [number]         Press the Enter key
#   Space[@<time>] [number]         Press the Space key
#   Tab[@<time>] [number]           Press the Tab key
#   Left[@<time>] [number]          Press the Left key
#   Right[@<time>] [number]         Press the Right key
#   Up[@<time>] [number]            Press the Up key
#   Ctrl+<key>                      Press Ctrl+<key> (e.g. Ctrl+C)
#
# Display:
#   Hide                            Hide the subsequent commands from the output
#   Show                            Show the subsequent commands in the output

Output demo.gif

Require poetry

Set FontSize 16
Set Width 1200
Set Height 600
Set Theme "Dracula"
Set TypingSpeed 80ms
Set WindowBar Colorful

# Show the project
Type "clear"
Enter
Sleep 500ms

# Welcome message
Type "# 🚀 Foundry Pipeline Assistant Demo"
Enter
Sleep 1s

# Show project structure
Type "ls -la"
Enter
Sleep 1.5s

# Show Poetry configuration
Type "cat pyproject.toml | head -20"
Enter
Sleep 2s

# Install dependencies
Type "# First, let's install dependencies with Poetry"
Enter
Type "poetry install"
Enter
Sleep 3s

# Show available make commands
Type "# Let's see what make commands are available"
Enter
Type "make"
Enter
Sleep 2s

# Run the basic demo with example question
Type "# Run with the default example question"
Enter
Type "make run"
Enter
Sleep 5s

# Show custom question demo
Type "# Now let's try a custom question"
Enter
Type "make run-custom"
Enter
Sleep 1s
Type "Analyze the current CI/CD pipeline health and identify potential issues"
Enter
Sleep 8s

# Show JSON output format
Type "# Generate JSON output for integration"
Enter  
Type "make run-json"
Enter
Sleep 6s

# Show quiet mode
Type "# Run in quiet mode for clean output"
Enter
Type "make run-quiet"
Enter
Sleep 4s

# Final message
Type "# ✨ That's the Foundry Pipeline Assistant in action!"
Enter
Type "# Check out the full README for more examples and configuration options"
Enter
Sleep 2s

# End
Type "clear"
Enter