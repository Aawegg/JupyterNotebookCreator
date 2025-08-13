import streamlit as st
import re
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Jupyter Notebook Creator",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header"><h1>📓 Jupyter Notebook Creator</h1><p>Transform your CHAIN/THOUGHT/RESPONSE text into organized Jupyter notebooks</p></div>', unsafe_allow_html=True)

# Sidebar for settings and options
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Formatting options
    st.markdown("#### 🎨 Formatting Options")
    add_timestamps = st.checkbox("📅 Add timestamps to blocks", value=False, help="Adds creation timestamp to each block")
    add_separators = st.checkbox("➖ Add visual separators", value=True, help="Adds horizontal lines between sections")
    
    # File options
    st.markdown("#### 📁 File Options")
    filename = st.text_input("📝 Output File Name", value="chains_and_thoughts.ipynb", help="Name for your notebook file")
    
    # Validation indicator
    if filename.endswith('.ipynb'):
        st.success("✅ Valid notebook filename")
    else:
        st.warning("⚠️ Filename should end with .ipynb")
    
    st.markdown("---")
    
    # Help section
    st.markdown("### 💡 Format Guide")
    with st.expander("📖 Expected Format"):
        st.code("""**[CHAIN_1]**
Your chain content here...

**[THOUGHT_1_1]**
Your thought content here...

**[RESPONSE]**
Your response content here...""")
    
    with st.expander("🔍 Tips"):
        st.markdown("""
        - Use consistent marker formatting
        - Each section will become a separate cell
        - RESPONSE section is automatically separated
        - Preview your content before creating
        """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-header"><h3>📝 Input Content</h3></div>', unsafe_allow_html=True)
    
    # Input options
    input_method = st.radio("Choose input method:", ["📝 Text Input", "📁 File Upload"], horizontal=True)
    
    text_input = ""
    if input_method == "📝 Text Input":
        text_input = st.text_area(
            "Enter your CHAIN/THOUGHT/RESPONSE text:",
            height=400,
            placeholder="Paste your formatted text here...\n\n**[CHAIN_1]**\nYour content...",
            help="Enter your text with proper CHAIN/THOUGHT/RESPONSE markers"
        )
    else:
        uploaded_file = st.file_uploader("Choose a text file", type=['txt', 'md'])
        if uploaded_file is not None:
            text_input = str(uploaded_file.read(), "utf-8")
            st.text_area("File Content Preview:", value=text_input[:500] + "..." if len(text_input) > 500 else text_input, height=200, disabled=True)

with col2:
    st.markdown('<div class="section-header"><h3>📊 Content Analysis</h3></div>', unsafe_allow_html=True)
    
    if text_input.strip():
        # Analysis metrics
        chain_count = len(re.findall(r'\*\*\[CHAIN_\d+\]\*\*', text_input))
        thought_count = len(re.findall(r'\*\*\[THOUGHT_\d+_\d+\]\*\*', text_input))
        response_count = len(re.findall(r'\*\*\[RESPONSE\]\*\*', text_input))
        word_count = len(text_input.split())
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("🔗 Chains", chain_count)
            st.metric("💭 Thoughts", thought_count)
        with col_b:
            st.metric("📋 Responses", response_count)
            st.metric("📄 Words", word_count)
        
        # Validation status
        st.markdown("#### ✅ Validation")
        if chain_count > 0:
            st.success("✅ CHAIN blocks found")
        else:
            st.warning("⚠️ No CHAIN blocks detected")
        
        if thought_count > 0:
            st.success("✅ THOUGHT blocks found")
        else:
            st.info("ℹ️ No THOUGHT blocks found")
        
        if response_count > 0:
            st.success("✅ RESPONSE block found")
        else:
            st.warning("⚠️ No RESPONSE block found")
    else:
        st.info("📝 Enter content to see analysis")

# Action buttons section
st.markdown('<div class="section-header"><h3>🚀 Actions</h3></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    create_button = st.button("🔧 Create Notebook", type="primary", use_container_width=True)

with col2:
    clear_button = st.button("🗑️ Clear Input", use_container_width=True)

with col3:
    if text_input.strip():
        preview_button = st.button("👀 Preview", use_container_width=True)

with col4:
    st.button("📋 Copy Text", use_container_width=True, disabled=not text_input.strip())

# Status and results area
status_container = st.container()

def create_notebook(text, filename, add_timestamps):
    try:
        if not text.strip():
            return None, "Please enter some CHAIN/THOUGHT/RESPONSE text"

        # Split into initial blocks with CHAIN/THOUGHT markers
        blocks = re.split(r"(?=\*\*\[CHAIN_\d+\]|\*\*\[THOUGHT_\d+_\d+\])", text.strip())
        blocks = [b.strip() for b in blocks if b.strip()]

        # Initialize cells list with a separator before the first CHAIN
        cells = []
        if blocks and any("**[CHAIN_" in b for b in blocks):
            if add_separators:
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
            if re.match(r"\*\*\[CHAIN_\d+\]", block) and add_separators:
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
                if add_separators:
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
        return buffer.getvalue(), None

    except Exception as e:
        return None, f"Failed to create notebook: {str(e)}"

# Handle button actions
if create_button:
    if not filename.endswith('.ipynb'):
        filename += '.ipynb'
    
    with st.spinner('🔄 Creating notebook...'):
        result, error = create_notebook(text_input, filename, add_timestamps)
        
        if result:
            st.markdown('<div class="success-box">✅ <strong>Notebook created successfully!</strong></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.download_button(
                    label="⬇️ Download Notebook",
                    data=result,
                    file_name=filename,
                    mime="application/json",
                    type="primary",
                    use_container_width=True
                )
            with col2:
                st.success(f"Ready to download as **{filename}**")
        else:
            st.error(f"❌ {error}")

if clear_button:
    st.rerun()

# Preview functionality
if text_input.strip() and 'preview_button' in locals() and preview_button:
    st.markdown('<div class="section-header"><h3>👀 Preview</h3></div>', unsafe_allow_html=True)
    
    with st.expander("📖 Notebook Preview", expanded=True):
        blocks = re.split(r"(?=\*\*\[CHAIN_\d+\]|\*\*\[THOUGHT_\d+_\d+\])", text_input.strip())
        blocks = [b.strip() for b in blocks if b.strip()]
        
        for i, block in enumerate(blocks):
            if block:
                st.markdown(f"**Cell {i+1}:**")
                st.markdown(block)
                st.markdown("---")
        
        # Show RESPONSE if exists
        response_match = re.search(r"\*\*\[RESPONSE\]\*\*", text_input, re.MULTILINE)
        if response_match:
            response_start = response_match.end()
            response_text = text_input[response_start:].strip()
            if response_text:
                st.markdown(f"**Cell {len(blocks)+1} (RESPONSE):**")
                st.markdown(f"**[RESPONSE]**\n{response_text}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2rem;'>
    📓 Jupyter Notebook Creator | Transform your structured text into organized notebooks
</div>
""", unsafe_allow_html=True)
