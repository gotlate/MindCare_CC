# MindCare: Mental Health Prediction Platform (https://mindcare-ojasev.onrender.com)

## Project Overview

MindCare is a comprehensive web application designed to assess the risk of depression in both students and working professionals. Utilizing machine learning models trained on relevant datasets, the platform provides personalized risk assessments and offers actionable insights, along with curated mental health resources and the latest research papers.

The goal of MindCare is to promote mental health awareness, encourage proactive support-seeking behavior, and provide easily accessible information to empower individuals in managing their well-being.

## Features

*   **Personalized Risk Assessment:** Users can fill out a form specific to their demographic (Student or Working Professional) to receive a personalized depression risk score.
*   **Actionable Risk Factor Breakdown:** The application provides a breakdown of factors contributing to the predicted risk, focusing on modifiable and interpretable aspects (e.g., sleep duration, financial stress, academic/work pressure). Demographic factors like age and gender are intentionally excluded from this breakdown to provide more meaningful guidance.
*   **Curated Mental Health Resources:** Access to a dedicated "Resources" section, meticulously organized into three key subsections:
    *   **Suggestions:** Practical tips and advice for maintaining mental well-being, often with a shuffling option for variety.
    *   **Support & Awareness Platforms:** Links to reputable organizations and platforms offering mental health support and awareness initiatives.
    *   **Research & Studies:** The latest academic papers and research findings related to mental health.
    **Crucially, students and working professionals have separate, tailored sets of resources** to ensure relevance to their unique challenges.
*   **Automated Research Paper Updates:** The platform automatically scrapes and updates the latest relevant research papers monthly, ensuring users have access to current academic insights.
*   **Intuitive User Interface:** A clean and responsive design built with Flask and styled with CSS, ensuring a smooth user experience.

## Technologies Used

*   **Backend:** Flask
*   **Machine Learning:**
    *   `scikit-learn`: For building and training Random Forest Classifiers.
    *   `joblib`: For saving and loading trained models and scalers.
    *   `pandas`: For data manipulation and preprocessing.
    *   `numpy`: For numerical operations.
    *   `SHAP` (SHapley Additive exPlanations): For model interpretability and generating feature contributions.
*   **Frontend:** HTML, CSS, JavaScript
*   **Data Storage:** JSON files (`.json`) for resources and `.pkl` files for trained models.
*   **Web Scraping:** The `research_scraper.py` script performs direct API calls to the **Semantic Scholar API** using the `requests` library. It retrieves academic papers based on predefined queries, processes the JSON responses, and updates the local resource files. 
*   **Deployment:** Render (for hosting the web service).
*   **Automation:** GitHub Actions (for scheduling and automating the monthly research paper updates).

### Automated Research Paper Updates (GitHub Actions)

The research paper section is automatically updated monthly using GitHub Actions, pushing fresh data directly to your repository, which then triggers a Render redeploy.

**How it works:**
*   A GitHub Actions workflow is scheduled to run at `00:00 UTC` on the `1st day of every month`.
*   It executes `research_scraper.py`, which fetches the latest papers from Semantic Scholar.
*   If new or updated papers are found, the workflow automatically commits these changes to your `data/*.json` files and pushes them back to your GitHub repository.
*   Due to Render's auto-deploy feature, this new commit will automatically trigger a redeployment of the web service, ensuring the live application displays the most current research.

