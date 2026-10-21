# CI/CD Integration for Accessibility Auditing

## GitHub Actions

```yaml
# .github/workflows/a11y-audit.yml
name: Accessibility Audit

on:
  pull_request:
    paths:
      - 'src/**/*.tsx'
      - 'src/**/*.vue'
      - 'src/**/*.html'
      - 'src/**/*.svelte'

jobs:
  a11y-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Run A11y Audit
        run: |
          npm ci
          npm run a11y:ci -- --json > a11y-results.json

      - name: Check for Critical Issues
        run: |
          node -e "
          const fs = require('fs');
          const data = JSON.parse(fs.readFileSync('a11y-results.json', 'utf8'));
          const critical = (data.violations || []).filter(v => v.severity === 'critical');
          if (critical.length) {
            console.error('FAILED: ' + critical.length + ' critical a11y violations found');
            process.exit(1);
          }
          console.log('PASSED: No critical a11y violations');
          "

      - name: Upload Audit Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: a11y-audit-report
          path: a11y-results.json

      - name: Comment on PR
        if: failure()
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: a11y-audit
          message: |
            ## Accessibility Audit Failed
            Critical WCAG 2.2 violations were found. See the uploaded artifact for details.
            Run the project accessibility audit command locally to view and fix issues.
```

## GitLab CI

```yaml
# .gitlab-ci.yml
a11y-audit:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm run a11y:ci -- --json > a11y-results.json
    - node -e "
      const fs = require('fs');
      const data = JSON.parse(fs.readFileSync('a11y-results.json', 'utf8'));
      const critical = (data.violations || []).filter(v => v.severity === 'critical');
      if (critical.length) process.exit(1);
      console.log('A11y audit passed');
      "
  artifacts:
    paths:
      - a11y-results.json
    when: always
  rules:
    - changes:
        - "src/**/*.{tsx,vue,html,svelte}"
```

## Azure DevOps

```yaml
# azure-pipelines.yml
- task: NodeTool@0
  inputs:
    versionSpec: '20.x'

- script: |
    npm ci
    npm run a11y:ci -- --json > $(Build.ArtifactStagingDirectory)/a11y-results.json
  displayName: 'Run A11y Audit'

- task: PublishBuildArtifacts@1
  condition: always()
  inputs:
    PathtoPublish: '$(Build.ArtifactStagingDirectory)/a11y-results.json'
    ArtifactName: 'a11y-audit-report'
```

## Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run a11y scan on staged files only
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(tsx|vue|html|svelte|jsx)$')

if [ -n "$STAGED_FILES" ]; then
  echo "Running accessibility audit on staged files..."
  npm run a11y:staged -- $STAGED_FILES
  if [ $? -ne 0 ]; then
    echo "A11y audit FAILED. Fix critical issues before committing."
    exit 1
  fi
  echo "A11y audit passed."
fi
```
