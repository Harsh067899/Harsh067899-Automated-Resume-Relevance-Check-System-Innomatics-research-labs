# 🎯 Streamlit Cloud Deployment Guide

Complete deployment guide for the **Automated Resume Relevance Check System** - an AI-powered placement dashboard for efficient candidate screening.

## 🚀 Quick Deployment Overview

Your app will be deployed at: `https://your-custom-url.streamlit.app`

**Estimated deployment time**: 5-10 minutes

## 📋 Prerequisites

1. **GitHub Account** - For repository hosting
2. **Streamlit Cloud Account** - Free at [share.streamlit.io](https://share.streamlit.io)
3. **OpenRouter API Key** - Available at [OpenRouter.ai](https://openrouter.ai/)

## 🛠️ Step-by-Step Deployment

### 1. **Repository Setup**

Your repository is already optimized for Streamlit Cloud with:
- ✅ `requirements.txt` - Python dependencies (cloud-optimized)
- ✅ `app.py` - Main Streamlit application
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml` - Environment variables template
- ✅ `packages.txt` - System dependencies for PDF processing

### 2. **Push to GitHub** (if not already done)

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Streamlit Cloud deployment ready"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/Harsh067899/your-repository.git

# Push to GitHub
git push -u origin main
```

### 3. **Deploy on Streamlit Cloud**

#### Step 3.1: Create New App
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**

#### Step 3.2: Configuration
- **Repository**: Select your GitHub repository
- **Branch**: `main`
- **Main file path**: `app.py`
- **App URL**: Choose custom URL (e.g., `resume-relevance-system`)

#### Step 3.3: Advanced Settings
Click **"Advanced settings"**:

**Secrets** (Copy exactly):
```toml
OPENROUTER_API_KEY = "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"
```

**Python Version**: `3.11`

#### Step 3.4: Deploy
1. Click **"Deploy!"**
2. Monitor deployment logs
3. Wait 5-10 minutes for completion

## 📊 System Features Overview

### 🎯 **Placement Dashboard**
- Job Description parsing from PDF/DOCX/Text
- Batch resume processing and analysis
- 0-100 relevance scoring with High/Medium/Low verdicts
- Skill gap analysis and missing qualifications detection
- CSV export for results

### ⌖ **Resume Radar**
- Three-pass AI analysis (Global, Sectional, Granular)
- PDF annotation with color-coded feedback
- Detailed constructive suggestions

### 🔍 **Additional Tools**
- Resume analyzer with ATS compatibility
- Resume builder with templates
- Job search functionality

## 🔧 Technical Configuration Files

### `requirements.txt` (Cloud-Optimized)
```txt
streamlit==1.28.1
openai==1.3.0
PyMuPDF==1.23.8
python-docx==0.8.11
pdfplumber==0.9.0
python-dotenv==1.0.0
pandas==1.5.3
plotly==5.17.0
```

### `packages.txt` (System Dependencies)
```txt
libgl1-mesa-glx
libglib2.0-0
libfontconfig1
libxrender1
libsm6
```

### `.streamlit/config.toml`
```toml
[theme]
base = "light"
primaryColor = "#FF6B35"

[server]
maxUploadSize = 200
```

## Server Deployment (Linux)

### Installing Chrome on Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Chrome dependencies
sudo apt install -y wget unzip fontconfig fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils

# Download and install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# Verify installation
google-chrome --version
```

### Installing Chrome on CentOS/RHEL
```bash
# Add Chrome repository
sudo tee /etc/yum.repos.d/google-chrome.repo <<EOF
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF

# Install Chrome
sudo yum install -y google-chrome-stable

# Verify installation
google-chrome --version
```

### Running the Application on Server
After installing Chrome, deploy the application:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make the startup script executable and run it:
   ```
   chmod +x startup.sh
   ./startup.sh
   ```

## Windows Server Deployment

### Prerequisites
- Python 3.7 or higher
- Chrome browser installed
- pip for installing dependencies

### Steps
1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application using the Python script:
   ```
   python run_app.py
   ```
   
   This script will automatically set up chromedriver and start the application.

## Streamlit Cloud Deployment

## 🚨 Troubleshooting

### Common Deployment Issues

**1. Import/Dependency Errors**
```
ModuleNotFoundError: No module named 'xyz'
```
- Solution: Check `requirements.txt` has correct package versions
- Verify all imports in code are available in cloud environment

**2. PDF Processing Failures**
```
Error processing PDF file
```
- Solution: System packages in `packages.txt` handle PDF dependencies
- Ensure uploaded PDFs are text-searchable (not scanned images)

**3. API Connection Issues**
```
OpenAI API error: Unauthorized
```
- Solution: Verify `OPENROUTER_API_KEY` is correctly set in secrets
- Check API key has sufficient credits
- Ensure no extra spaces in secret key value

**4. File Upload Issues**
```
File size exceeds maximum
```
- Solution: Maximum file size is 200MB (configured in config.toml)
- Supported formats: PDF, DOCX, TXT

### Debugging Steps

1. **Check Streamlit Cloud Logs**:
   - Go to your app dashboard on Streamlit Cloud
   - Click "Manage app"
   - Review logs for specific error messages

2. **Test Locally First**:
   ```bash
   # Set environment variable
   export OPENROUTER_API_KEY="your-api-key"
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run locally
   streamlit run app.py
   ```

3. **Verify Secrets Configuration**:
   - Secrets are case-sensitive
   - No trailing spaces allowed
   - Must match exact format shown above

## 🔒 Security & Best Practices

### Environment Variables
- ✅ API keys stored in Streamlit Cloud secrets (encrypted)
- ✅ No hardcoded credentials in source code
- ✅ Secrets not committed to repository

### Data Privacy
- ✅ No permanent data storage
- ✅ Temporary processing only
- ✅ Files automatically deleted after analysis

### Performance Optimization
- ✅ Streamlined dependencies for cloud deployment
- ✅ Efficient PDF processing libraries
- ✅ Optimized file handling and caching

## 📱 Device Compatibility

The application is fully responsive and works on:
- 📱 Mobile phones
- 💻 Tablets  
- 🖥️ Desktop computers
- 🌐 All modern web browsers

## 🎯 Post-Deployment Verification

After successful deployment, test these features:

### Critical Functions
- [ ] Homepage loads correctly
- [ ] Navigation menu works
- [ ] Job description upload and parsing
- [ ] Multiple resume file processing
- [ ] Relevance scoring calculation
- [ ] CSV export functionality

### Advanced Features
- [ ] PDF annotation in Resume Radar
- [ ] Batch processing multiple candidates
- [ ] Missing skills analysis
- [ ] High/Medium/Low verdict assignment

## 🌐 Usage Guidelines

### For Placement Teams
1. Navigate to **🎯 PLACEMENT DASHBOARD**
2. Upload job description (PDF/DOCX/Text)
3. Upload multiple candidate resumes
4. Review relevance scores and verdicts
5. Export results for team analysis

### For HR Professionals  
1. Use batch processing for large candidate pools
2. Prioritize High relevance candidates
3. Use missing skills data for candidate feedback

### For Individual Users
1. Use **⌖ RESUME RADAR** for detailed AI feedback
2. Use **🔍 RESUME ANALYZER** for quick ATS checks
3. Use **📝 RESUME BUILDER** to create optimized resumes

## 📞 Support & Maintenance

**Developer**: Harsh Sahu  
**GitHub**: [@Harsh067899](https://github.com/Harsh067899)  
**LinkedIn**: [Harsh Sahu](https://www.linkedin.com/in/zharsh-sahu/)

**For Technical Issues**:
1. Check troubleshooting section above
2. Review Streamlit Cloud deployment logs  
3. Create issue on GitHub repository
4. Contact developer for complex problems

---

**🎉 Congratulations! Your Automated Resume Relevance Check System is now live and ready to streamline placement processes for Innomatics Research Labs!**

**Next Steps**: Share the deployed URL with your placement team and start analyzing candidates efficiently.

### Sample Dockerfile
```dockerfile
FROM python:3.9-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x startup.sh setup_chromedriver.py

# Expose port for Streamlit
EXPOSE 8501

# Run the startup script
CMD ["python", "run_app.py"]
```

## Troubleshooting Common Issues

### Error: "Service unexpectedly exited"
This usually indicates that Chrome cannot be started. Ensure:
- Chrome is installed
- You have the correct permissions
- You're using the `--no-sandbox` option in headless environments

### Error: "Chrome version must be between X and Y"
This indicates a version mismatch between Chrome and chromedriver:
- Run the `setup_chromedriver.py` script to install the matching chromedriver version
- The script automatically detects your Chrome version and downloads the compatible chromedriver

### Error: "Permission denied" when installing chromedriver
This is a permission issue:
- Try running the application with administrator privileges
- Ensure the user has write permissions to the installation directory
- Use the `setup_chromedriver.py` script which installs chromedriver in the user's home directory

### Error: "unknown error: DevToolsActivePort file doesn't exist"
This is common in containerized environments:
- Add `--disable-dev-shm-usage` to Chrome options (already included in our setup)
- Ensure you're using `--no-sandbox` in Docker/container environments

### Windows-specific issues
If you encounter issues on Windows:
- Make sure Chrome is installed in the standard location
- Try running the application as administrator
- Use the `run_app.py` script which handles setup automatically
- Check Windows Defender or antivirus software that might be blocking chromedriver

## Additional Resources
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Chrome for Testing](https://developer.chrome.com/docs/chromium/chrome-for-testing)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app) 