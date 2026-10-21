# Examples of brand style

This Catalogue is used to store examples of brand style files.

# File type

- PPT Example: Show complete brand style
- Picture: brand logo, product chart, palette
- Branding manual: Branding guide documents

# Use method

1. Placing brand sample files in this directory
2. Implementation of brand style learning:
   ```bash
   python scripts/style_learner.py \
     --examples-dir ./assets/styles/ \
     --output ./brand_style.json
   ```
3. The generated brand style.json will be later generated

# Example structure

```
assets/styles/
├── example_ppt.pptx
├── brand_logo.png
├── product_image.png
├── color_palette.png
└── brand_guideline.pdf
```
