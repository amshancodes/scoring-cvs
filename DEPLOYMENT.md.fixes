# Resume Evaluation System - Deployment Guide

This guide will help you deploy the Resume Evaluation System Streamlit app to different platforms.

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for MVP)

The easiest way to deploy the MVP is using Streamlit Cloud, which offers free hosting for public GitHub repositories.

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with GitHub
4. Deploy your app by connecting to your repository
5. Set the main file path to `app.py`
6. Add your OpenAI API key as a secret called `OPENAI_API_KEY` 

Your app will be available at a URL like `https://username-app-name.streamlit.app`.

### Option 2: Local Deployment

To run the app locally:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

3. Access the app at `http://localhost:8501`

### Option 3: Heroku Deployment

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

4. Set the OpenAI API key:
   ```bash
   heroku config:set OPENAI_API_KEY=your-api-key
   ```

5. Deploy the app:
   ```bash
   git push heroku deployment-exploration:main
   ```

## Security Considerations

- The app uses a simple password authentication (set to `demo123` by default)
- Change this password in the `app.py` file for your deployment
- OpenAI API keys are only stored in the user's session and not saved permanently
- For production, implement more robust authentication and API key handling

## Customizing the Appearance

- Edit `.streamlit/config.toml` to change the app's theme
- Modify CSS styles in `utils/ui_components.py` to change component styling

## Adding Additional Templates

To add more evaluation templates:

1. Create new prompt files in the `configure` directory 
2. Update the `get_available_templates()` function in `utils/resume_processor.py`

## Limitations of the MVP

- No persistent storage of evaluations
- User authentication is basic
- API keys need to be entered each session
- Custom prompts aren't saved between sessions

These limitations can be addressed in future versions with proper backend storage and user management. 