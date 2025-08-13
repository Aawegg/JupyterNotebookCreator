 
import streamlit as st
import re
import json
from datetime import datetime

st.title("Jupyter Notebook Creator")

# Input text area
st.subheader("Enter CHAIN/THOUGHT/RESPONSE text:")
text_input = st.text_area("Input", height=300)

# Formatting options
add_timestamps = st.checkbox("Add timestamps to blocks", value=False)

# Output file name
filename = st.text_input("Output File Name", value="chains_and_thoughts.ipynb")

# Status message
status = st.empty()

def create_notebook(text, filename, add_timestamps):
    try:
        if not text.strip():
            status.error("Please enter some CHAIN/THOUGHT/RESPONSE text")
            return None

        # Split into initial blocks with CHAIN/THOUGHT markers
        blocks = re.split(r"(?=\*\*\[CHAIN_\d+\]|\*\*\[THOUGHT_\d+_\d+\])", text.strip())
        blocks = [b.strip() for b in blocks if b.strip()]

        # Initialize cells list with a separator before the first CHAIN
        cells = []
        if blocks and any("**[CHAIN_" in b for b in blocks):
            cells.append({"cell_type": "markdown", "metadata": {}, "source": ["---\n"]})

        # Process each block
        for block in blocks:
            if add_timestamps:
                lines = block.splitlines()
                if lines:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    lines.insert(1, f"*Created: {timestamp}*")
                block = "\n".join(lines)

            # Add separator before CHAIN blocks
            if re.match(r"\*\*\[CHAIN_\d+\]", block):
                cells.append({"cell_type": "markdown", "metadata": {}, "source": ["---\n"]})

            cells.append({"cell_type": "markdown", "metadata": {}, "source": block.splitlines(keepends=True)})

        # Extract and add RESPONSE section in a separate cell
        response_match = re.search(r"\*\*\[RESPONSE\]\*\*", text, re.MULTILINE)
        if response_match:
            response_start = response_match.end()
            response_text = text[response_start:].strip()
            if response_text:
                # Remove RESPONSE from the last block if included
                if cells and "[RESPONSE]" in cells[-1]["source"][0]:
                    cells[-1]["source"] = [s for s in cells[-1]["source"] if "[RESPONSE]" not in s]
                # Add separator and RESPONSE section
                cells.append({"cell_type": "markdown", "metadata": {}, "source": ["---\n"]})
                cells.append({"cell_type": "markdown", "metadata": {}, "source": [f"**[RESPONSE]**\n{response_text}\n"]})

        # Notebook structure
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "file_extension": ".py",
                    "name": "python"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }

        # Save to a file-like object for download
        import io
        buffer = io.StringIO()
        json.dump(notebook, buffer, ensure_ascii=False, indent=2)
        buffer.seek(0)
        return buffer.getvalue(), filename

    except Exception as e:
        status.error(f"Failed to create notebook: {str(e)}")
        return None

# Create Notebook button
if st.button("Create Notebook"):
    result = create_notebook(text_input, filename, add_timestamps)
    if result:
        notebook_content, filename = result
        st.download_button(
            label="Download Notebook",
            data=notebook_content,
            file_name=filename,
            mime="application/json"
        )
        status.success(f"✅ Notebook ready for download as {filename}")

# Clear Input button
if st.button("Clear Input"):
    st.session_state.text_input = ""
    status.empty()
