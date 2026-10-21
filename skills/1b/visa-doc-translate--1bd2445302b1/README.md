# Visaツール Translation Tool

Automatically translate visa application documents from images to professional English PDFs.

# Capabilities

* Auto OCR**: Try multiple OCR methods (macOS Vision, EasyOCR, Tesseract)
* Bilingual PDF**: Original image + Professional English translation
* Multilingual**: Chinese and other languages
*Professional Format**: Fits Official Visa Application
* Fully automated**: no intervention

## Supported file type

* Bank Deposit Certificate
* Job certificate
* Re ement certificate
* Certificate of income
* Real Estate Certificate
* Business license
* ID and passport

# Use method

```bash
/visa-doc-translate <image-file>
```

Examples

```bash
/visa-doc-translate RetirementCertificate.PNG
/visa-doc-translate BankStatement.HEIC
/visa-doc-translate EmploymentLetter.jpg
```

Come on

Create `<filename>_Translated.pdf` and include:

* 1st page**: Original document image (center position, A4 size)
* **Page 2**: Professional English Translation

# Elements

### Python Library

```bash
pip install pillow reportlab
```

### OCR (you need one of the following)

**macOS**

```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

Cross Platform

```bash
pip install easyocr
```

**Tesseract**：

```bash
brew install tesseract tesseract-lang
pip install pytesseract
```

## How it works

1. Convert HEIC to PNG as needed
2. Check the EXIF rotation
3. Extract text in the available OCR method
4. Professional English translation
5.を生成するrate Bilingual PDF

## Ideal Applications

* Australia Visa Application
* US Visa Application
* Canada Visa Application
* UK Visa Application
* EU Visa Application

## License

MIT
