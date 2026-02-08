# Document Summarizer Skill

> **Submitted by**: ETHPanda (GitHub: FrankFitzgeraldGu)
> **Category**: ai-productivity

## 📖 Introduction
The **Document Summarizer Skill** is a high-performance document analysis tool powered by Anthropic's **Claude 3.5 Sonnet**. It goes beyond simple summarization by extracting actionable insights, analyzing sentiment, and structuring output for easy integration into other workflows.

## ✨ Key Features

- **🧠 Advanced AI Integration**: Utilizes the latest `claude-3-5-sonnet` model for superior understanding.
- **🌐 Multi-Language**: Seamlessly handles documents in English, Chinese, Spanish, and more.
- **🎯 Focus Mode**: Tell the AI exactly what to look for (e.g., "legal risks", "action items").
- **📏 Flexible Output**: Control summary length (Short/Medium/Long) to suit your needs.
- **🛡️ Production Ready**: Includes robust error handling, exponential backoff retries, and logging.
- **🧪 Mock Mode**: Built-in mock response generation for testing and development without API costs.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Anthropic API Key

### Installation

1. Install dependencies:
   ```bash
   pip install anthropic
   ```

2. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY="your_api_key_here"
   ```

### Usage

**Command Line Interface:**

```bash
# Summarize a text file
python scripts/main.py --file path/to/document.txt

# Summarize specific text with options
python scripts/main.py --text "Your long text here..." --length short --language spanish

# Focus on specific topics
python scripts/main.py --file report.pdf --focus "revenue" "growth" --length long
```

**Python Import:**

```python
from scripts.main import DocumentSummarizer

summarizer = DocumentSummarizer()
result = summarizer.summarize(
    text="Your document text...",
    length="medium",
    focus_areas=["key risks"]
)
print(result)
```

## 📊 Output Format

The skill returns a structured JSON object:

```json
{
  "summary": "The document outlines...",
  "key_insights": [
    "Revenue grew by 20% YoY",
    "New market expansion planned for Q3"
  ],
  "sentiment": "positive",
  "language": "english",
  "metadata": {
    "word_count": 500,
    "topics": ["finance", "strategy"]
  }
}
```

## 🛠️ Configuration

| Flag | Description | Default |
|------|-------------|---------|
| `--file` | Path to input file | None |
| `--text` | Direct text input | None |
| `--length` | Summary length (short/medium/long) | medium |
| `--language` | Target language | english |
| `--focus` | Specific areas to focus on | None |
| `--mock` | Enable mock mode (no API usage) | False |

## 📝 License
MIT
