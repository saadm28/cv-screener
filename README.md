# 🎯 KSEYE CV Screener

**AI-Powered CV Screening & Analysis Platform**

A modern, intelligent CV screening application built with Streamlit and OpenAI GPT-4. KSEYE CV Screener helps recruiters and hiring managers efficiently analyze and rank candidates based on job requirements.

## ✨ Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-4o-mini for intelligent CV analysis
- 📊 **Smart Scoring**: Comprehensive candidate scoring based on experience and skills
- 🎨 **Modern UI**: Clean, professional interface with KSEYE branding
- 📁 **Multi-Format Support**: Supports PDF, DOCX, and ZIP file uploads
- 🔍 **Detailed Insights**: Candidate summaries, experience highlights, and skill matching
- 📋 **Integrated Details**: Expandable candidate details within each card
- 🏷️ **Skills Categorization**: Identifies required vs. additional skills
- 💼 **Experience Analysis**: Detailed work history and highlights extraction

## 🚀 Live Demo

[**Try KSEYE CV Screener →**](your-streamlit-app-url-here)

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-4o-mini
- **Document Processing**: pdfplumber, docx2txt
- **Styling**: Custom CSS with KSEYE branding
- **Deployment**: Streamlit Cloud

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/kseye-cv-screener.git
   cd kseye-cv-screener
   ```

2. **Create virtual environment**

   ```bash
   python -m venv cv-screener
   source cv-screener/bin/activate  # On Windows: cv-screener\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🔑 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file or Streamlit secrets

## 📋 Usage

1. **Navigate to the application** in your browser
2. **Upload CV files** (PDF, DOCX, or ZIP containing multiple files)
3. **Enter job title** and detailed job description
4. **Click "Analyze CVs"** to start the AI analysis
5. **Review results** with ranked candidates and detailed insights
6. **Expand "View Details"** for comprehensive candidate analysis

## 🏗️ Project Structure

```
kseye-cv-screener/
├── app.py                 # Main Streamlit application
├── cv_analyzer.py         # Core CV analysis functions
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── assets/               # Static assets (logos, themes)
├── parsing/              # CV parsing utilities
│   ├── __init__.py
│   └── extractor.py      # File extraction functions
└── utils/                # Utility functions
    └── text.py           # Text processing utilities
```

## 🎨 Features Overview

### Clean Modern Interface

- Professional KSEYE branding with signature red color scheme
- Responsive design that works on desktop and mobile
- Integrated candidate cards with expandable details
- No emoji clutter - clean, modern typography

### AI-Powered Analysis

- Intelligent candidate name extraction
- Experience parsing and relevance scoring
- Skills matching and categorization
- Professional summary generation
- AI assessment notes and insights

### Smart Scoring System

- Experience-based scoring (total years + relevant years)
- Skills bonus calculation (required + nice-to-have)
- Normalized scoring (20-100 scale)
- Automatic candidate ranking

### Multi-Format Support

- PDF document processing
- Microsoft Word (.docx) support
- ZIP file extraction for bulk uploads
- Text file support (.txt)

## 🚀 Deployment on Streamlit Cloud

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Add your OpenAI API key to Streamlit secrets
   - Deploy!

### Streamlit Secrets Configuration

In your Streamlit Cloud dashboard, add:

```toml
[secrets]
OPENAI_API_KEY = "your_openai_api_key_here"
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About KSEYE

KSEYE is committed to revolutionizing the hiring process through AI-powered solutions that help companies find the best talent efficiently and effectively.

## 🐛 Issues & Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/kseye-cv-screener/issues) page
2. Create a new issue with detailed information
3. Contact support at support@kseye.com

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- Streamlit for the excellent web framework
- Contributors and testers who helped improve the application

---

**Made with ❤️ by the KSEYE Team**
