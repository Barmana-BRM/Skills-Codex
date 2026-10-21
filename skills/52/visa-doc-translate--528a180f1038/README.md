# Visa Document Translator

Automatically translate visa application documents from images to professional English PDFs.

## Features

- **Automatic OCR**: Tries multiple OCR methods (macOS Vision, EasyOCR, Tesseract)
- **Bilingual PDF**: Original image + professional English translation
- **Multi-language**: Supports Chinese, and other languages
- **Professional Format**: Suitable for official visa applications
- **Fully Automated**: No manual intervention required

## Supported Documents

- Bank deposit certificates
- Employment certificates
- Remission certificates
- Income certificates
- Property certificates
- Business licences.
- ID cards and passes

## Usage

```bash
/visa-doc-translate <image-file>
```

### Examples

```bash
/visa-doc-translate RetirementCertificate.PNG
/visa-doc-translate BankStatement.HEIC
/visa-doc-translate EmploymentLetter.jpg
```

## Output

Creates `<filename>_Translated.pdf` with:
- **Page 1**: Original document image (centered, A4 size)
- **Page 2**: Professional English translation

## Requirements

### Python Libraries
```bash
pip install pillow reportlab
```

### OCR (one of the following)

**macOS (recommended)**:
```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

**Cross-platform**:
```bash
pip install easyocr
```

**Tesseract**:
```bash
brew install tesseract tesseract-lang
pip install pytesseract
```

## How It Works

1. Converts HEIC to PNG if needed
2. Checks and applies EXIF rotation
3. Extracts text using available OCR method
4. Translates to professional English
5. Generates bilingual PDF

## Perfect For

- Australia visa applications
- USA visa applications
- Canada visa applications
- UK visa applications
- EU visa applications

## License

MIT
