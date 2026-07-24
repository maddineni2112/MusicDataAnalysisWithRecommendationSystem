# Music Data Analysis and Song Recommendation System

This project analyzes Spotify track data and builds a recommendation workflow using PySpark, machine learning, dimensionality reduction, and clustering. The goal is to understand which audio features relate to song popularity and recommend similar tracks based on musical characteristics.

## Project Highlights

- Analyzed Spotify audio features such as danceability, energy, acousticness, tempo, valence, loudness, and popularity.
- Cleaned and transformed the dataset using Pandas and PySpark.
- Built exploratory visualizations for popularity distribution, yearly trends, feature relationships, and correlations.
- Compared Linear Regression and Random Forest Regression for popularity prediction.
- Used PCA to reduce audio-feature dimensions while preserving most of the variance.
- Built a content-based recommendation function that finds similar songs using distance between PCA vectors.
- Applied K-Means clustering to group songs with similar audio profiles.

## Methods Used

| Area | Techniques |
| --- | --- |
| Data processing | Pandas, PySpark DataFrames |
| Exploration | Correlation analysis, distribution plots, pair plots, trend analysis |
| Prediction | Linear Regression, Random Forest Regression |
| Evaluation | MSE, RMSE |
| Recommendation | PCA feature vectors, L2 distance |
| Clustering | K-Means, silhouette score |

## Key Results

- Random Forest Regression performed slightly better than Linear Regression for predicting popularity.
- PCA was used to create compact song representations for similarity matching.
- K-Means clustering identified groups of songs with similar audio characteristics.
- The recommendation workflow can return the nearest songs for a given input track based on PCA feature distance.

## Repository Structure

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── MusicDataAnalysisNRecommendationSystem_report.pdf
│   └── Music_Data_Analysis_Song_Recommendation.pptx
├── notebooks/
│   └── MusicDataAnalysisNRecommendationSystem_code.ipynb
└── src/
    └── recommender.py
```

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add the Spotify dataset locally.

The notebook expects a CSV file similar to `Spotify_data.csv`. The dataset is not included in this repository, so update the file path in the notebook before running it.

3. Open and run the notebook:

```bash
jupyter notebook notebooks/MusicDataAnalysisNRecommendationSystem_code.ipynb
```

## Notes

This project is a content-based recommendation system. It recommends songs using audio-feature similarity rather than user listening behavior. Production recommendation systems usually combine content-based methods with collaborative filtering, user-item interaction data, ranking models, and feedback loops.

## Future Improvements

- Add a reproducible dataset download or data sample.
- Convert the notebook workflow into a full Python pipeline.
- Add user interaction data for collaborative filtering.
- Build a small Streamlit app for interactive song recommendations.
- Track experiments and model metrics in a structured format.
