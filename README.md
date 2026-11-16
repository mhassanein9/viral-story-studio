##### \# 🎬 Story Reel Studio

##### 

##### An AI-powered workflow automation tool designed to streamline the creation of high-retention, vertical short-form videos (YouTube Shorts, TikTok, and Instagram Reels). 

##### 

##### Built with \*\*Python\*\* and \*\*Streamlit\*\*, this studio transforms raw concepts into structured, second-by-second video production pipelines—covering scriptwriting, AI voiceover preparation, and visual asset sourcing.

##### 

##### \---

##### 

##### \## 📸 Dashboard Preview

##### 

##### !\[Dashboard Preview](screenshots/dashboard.png)

##### 

##### \---

##### 

##### \## ✨ Key Features

##### 

##### \* \*\*📊 End-to-End Project Dashboard:\*\* Track video ideas from initial concept (`Idea`) through `Script`, `Voiceover`, `Visuals`, `Editing`, and `Exported` stages.

##### \* \*\*✍️ AI Script Generation:\*\* Input a raw headline or concept, select a niche and target duration, and generate dramatic, high-retention hooks and narratives.

##### \* \*\*🎙️ Voiceover Block Builder:\*\* Automatically segments scripts into clean, pacing-optimized blocks ready for AI voice generators like \*\*ElevenLabs\*\*.

##### \* \*\*🎥 Visual \& Stock Sourcing Plan:\*\* Generates scene-by-scene visual cues and search keywords for stock footage platforms (Pexels, Pixabay) or AI video generators.

##### \* \*\*🔌 Offline \& Live API Modes:\*\* Works out-of-the-box using built-in offline templates for testing, with seamless integration for \*\*Anthropic's Claude API\*\* for dynamic AI generation.

##### 

##### \---

##### 

##### \## 🛠️ Tech Stack

##### 

##### \* \*\*Frontend \& UI:\*\* Streamlit

##### \* \*\*Backend:\*\* Python 3.10+

##### \* \*\*AI Integration:\*\* Anthropic Claude API (`anthropic`)

##### \* \*\*Environment Management:\*\* `python-dotenv`

##### 

##### \---

##### 

##### \## 🚀 Getting Started

##### 

##### Follow these steps to set up and run the project locally on your machine.

##### 

##### \### 1. Clone the Repository

##### ```bash

##### git clone \[https://github.com/mhassanein9/viral-story-studio.git](https://github.com/mhassanein9/viral-story-studio.git)

##### cd viral-story-studio

##### 

##### 2\. Create \& Activate a Virtual Environment

##### Windows (PowerShell):

##### 

##### PowerShell

##### python -m venv .venv

##### .\\.venv\\Scripts\\Activate.ps1

##### macOS / Linux:

##### 

##### Bash

##### python3 -m venv .venv

##### source .venv/bin/activate

##### 3\. Install Dependencies

##### Bash

##### pip install -r requirements.txt

##### 4\. Configure Environment Variables (Optional)

##### To enable live AI generation with Claude, copy the example environment file and add your API key:

##### 

##### Bash

##### cp .env.example .env

##### Open .env and add your key:

##### 

##### env

##### ANTHROPIC\_API\_KEY=your\_api\_key\_here

##### (Note: You can skip this step to test and run the studio using built-in offline templates.)

##### 

##### 5\. Run the Application

##### Bash

##### streamlit run app.py

##### The app will automatically open in your browser at http://localhost:8501.

##### 

##### 🗺️ Roadmap \& Future Improvements

##### \[ ] Direct API integration with ElevenLabs for one-click audio generation.

##### 

##### \[ ] Direct Pexels API integration to fetch and preview stock clips inside the app.

##### 

##### \[ ] Multi-language script generation support (including Arabic and German).

##### 

##### \[ ] Export production plans to PDF/Notion.

##### 

##### 📄 License

##### This project is open-source and available under the MIT License.

