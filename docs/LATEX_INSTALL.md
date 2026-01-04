# LaTeX Installation Guide for ATS CV Maker

## Why Do I Need LaTeX?

LaTeX is required to generate the professional PDF from your improved CV. It provides:
- Professional typesetting
- ATS-friendly formatting
- Consistent layout
- Clean, parseable output

## Quick Installation

### macOS

**Option 1: BasicTeX (Recommended - Smaller)**
```bash
# Install BasicTeX (smaller, faster)
brew install --cask basictex

# Update package manager
sudo /Library/TeX/texbin/tlmgr update --self

# Install moderncv package
sudo /Library/TeX/texbin/tlmgr install moderncv

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="/Library/TeX/texbin:$PATH"
```

**Option 2: MacTeX (Full Installation)**
```bash
# Install full MacTeX (larger but complete)
brew install --cask mactex-no-gui

# Install moderncv
sudo tlmgr install moderncv
```

**Verification:**
```bash
pdflatex --version
# Should show: pdfTeX 3.x...
```

### Ubuntu/Debian

```bash
# Install LaTeX distribution
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra

# Verify installation
pdflatex --version
```

**Note**: texlive-latex-extra includes moderncv and other useful packages.

### Windows

**Option 1: MiKTeX (Recommended)**

1. Download MiKTeX from: https://miktex.org/download
2. Run the installer
3. During installation, choose:
   - Install missing packages: **On-the-fly**
   - Paper size: **A4**
4. After installation, open **MiKTeX Console**
5. Go to **Packages** tab
6. Search for "moderncv"
7. Click **Install**

**Option 2: TeX Live (Full)**

1. Download TeX Live from: https://tug.org/texlive/
2. Run install-tl-windows.exe
3. Follow installation wizard
4. Add to PATH if not automatic:
   ```
   C:\texlive\2023\bin\win32
   ```

**Verification (Command Prompt):**
```cmd
pdflatex --version
```

### Linux (Other Distros)

**Fedora/RHEL:**
```bash
sudo dnf install texlive-scheme-basic texlive-moderncv
```

**Arch Linux:**
```bash
sudo pacman -S texlive-core texlive-latexextra
```

**openSUSE:**
```bash
sudo zypper install texlive-latex texlive-moderncv
```

## Installing moderncv Package

The moderncv package is required for the CV template.

### TeX Live (macOS/Linux)

```bash
# Update package manager
sudo tlmgr update --self

# Install moderncv
sudo tlmgr install moderncv

# Verify installation
kpsewhich moderncv.cls
# Should show path to moderncv.cls
```

### MiKTeX (Windows)

1. Open **MiKTeX Console**
2. Go to **Updates** tab
3. Click **Check for updates**
4. Go to **Packages** tab
5. Search for "moderncv"
6. Select and click **Install**

Alternatively, moderncv will auto-install when you first compile if you enabled "Install packages on-the-fly".

## Troubleshooting

### "moderncv.cls not found"

**Solution 1: Manual Install (TeX Live)**
```bash
sudo tlmgr install moderncv
```

**Solution 2: Manual Install (MiKTeX)**
- Open MiKTeX Console
- Packages → Search "moderncv" → Install

**Solution 3: Verify PATH**
```bash
# macOS/Linux
which pdflatex

# Should show: /Library/TeX/texbin/pdflatex or similar
```

### "pdflatex: command not found"

**macOS:**
```bash
# Add to ~/.zshrc or ~/.bash_profile
export PATH="/Library/TeX/texbin:$PATH"

# Reload
source ~/.zshrc
```

**Linux:**
```bash
# Verify installation
dpkg -l | grep texlive

# Reinstall if missing
sudo apt-get install --reinstall texlive-latex-base
```

**Windows:**
- Check PATH includes LaTeX bin directory
- Restart terminal/IDE after installation

### Compilation Errors

**Error: "! LaTeX Error: File `moderncv.cls' not found"**
```bash
# Install moderncv
sudo tlmgr install moderncv  # macOS/Linux
# Or use MiKTeX Console on Windows
```

**Error: Permission denied**
```bash
# macOS/Linux: Use sudo
sudo tlmgr install moderncv

# Windows: Run as Administrator
```

**Error: "! Undefined control sequence"**
- Check .tex file for special characters
- Review latex_error.log for details
- Special chars like & % $ # _ need escaping

## Testing Your Installation

### Quick Test

```bash
# Create test.tex
cat > test.tex << 'EOF'
\documentclass{article}
\begin{document}
Hello, LaTeX!
\end{document}
EOF

# Compile
pdflatex test.tex

# Check output
ls test.pdf
```

### Test with moderncv

```bash
# Create cv_test.tex
cat > cv_test.tex << 'EOF'
\documentclass[11pt,a4paper]{moderncv}
\moderncvstyle{banking}
\moderncvcolor{blue}
\name{First}{Last}
\begin{document}
\makecvtitle
\section{Education}
\cventry{2020}{Degree}{Institution}{City}{}{}
\end{document}
EOF

# Compile
pdflatex cv_test.tex

# Check output
ls cv_test.pdf
```

If both tests work, you're ready to use ATS CV Maker!

## Alternative: Online LaTeX Compilation

If you can't install LaTeX locally, you can:

1. Run improvement workflow to generate .tex file:
   ```bash
   python improve_cv.py cv.pdf jd.txt
   # This creates optimized_cv.tex
   ```

2. Upload to Overleaf:
   - Go to https://www.overleaf.com/
   - Create free account
   - New Project → Upload Project
   - Upload the .tex file
   - Click "Recompile"
   - Download PDF

## Minimal vs Full Installation

### Minimal (Recommended for ATS CV Maker)
**Size**: ~200-500 MB
```bash
# macOS
brew install --cask basictex
sudo tlmgr install moderncv

# Ubuntu
sudo apt-get install texlive-latex-base texlive-latex-extra
```

### Full Installation
**Size**: ~4-6 GB
```bash
# macOS
brew install --cask mactex

# Ubuntu
sudo apt-get install texlive-full
```

**Recommendation**: Start with minimal. Install full only if you need additional packages.

## Disk Space Requirements

- **BasicTeX/texlive-latex-base**: ~200-300 MB
- **texlive-latex-extra**: ~400-500 MB  
- **Full TeX Live**: ~4-6 GB
- **MiKTeX Basic**: ~300 MB
- **MiKTeX Full**: ~3-4 GB

## Updating LaTeX

### TeX Live
```bash
# Update package manager
sudo tlmgr update --self

# Update all packages
sudo tlmgr update --all
```

### MiKTeX
1. Open MiKTeX Console
2. Click **Updates** tab
3. Click **Check for updates**
4. Click **Update now**

## Getting Help

### Check Logs
```bash
# After failed compilation
cat latex_error.log
# Or
cat optimized_cv.log
```

### Common Commands
```bash
# Check LaTeX version
pdflatex --version

# Find package
kpsewhich moderncv.cls

# List installed packages (TeX Live)
tlmgr list --only-installed

# LaTeX help
texdoc moderncv
```

## Pro Tips

1. **Use BasicTeX on macOS**: Smaller, faster, sufficient for ATS CV Maker
2. **Enable auto-install (MiKTeX)**: Automatically installs missing packages
3. **Keep PATH updated**: Ensure LaTeX binaries are in PATH
4. **Test after install**: Run test compilation before using with real CV
5. **Use Overleaf as backup**: When local LaTeX issues arise

## Ready to Generate Your CV?

After LaTeX is installed:

```bash
# Test the PDF generator
python pdf_generator.py

# Run full workflow
python improve_cv.py your_cv.pdf job_description.txt
```

You should see:
```
🔨 Compiling LaTeX to PDF...
   Run 1/2...
   Run 2/2...
✅ PDF generated successfully: /path/to/optimized_cv.pdf
```

Success! 🎉
