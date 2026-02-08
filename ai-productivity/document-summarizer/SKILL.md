---
name: document-summarizer
description: A powerful document summarization and insight extraction skill using Claude AI (claude-3-5-sonnet). Supports multi-language, custom summary lengths, and structured JSON output.
author: ETHPanda (FrankFitzgeraldGu)
version: 1.0.0
category: ai-productivity
---

# Document Summarizer

This skill analyzes documents to provide summaries, extract key insights, and focus on specific areas of interest. It is designed for productivity and uses the Claude 3.5 Sonnet model.

## Features
- **Multi-language Support**: Automatically detects and summarizes in English, Chinese, Spanish, etc.
- **Custom Lengths**: specific summary length (short, medium, long).
- **Key Insights**: Automatically extracts bullet points of key information.
- **Focus Areas**: Can be directed to focus on specific topics within the document.
- **Structured Output**: Returns results in JSON format for easy integration.

## Usage
Run the script `scripts/main.py` with the document content and configuration.

### CLI Example
```bash
python scripts/main.py --file my_doc.txt --length medium --language chinese
```

## Dependencies
- python 3.8+
- anthropic
