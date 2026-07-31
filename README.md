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

## Big Data Concepts Demonstrated

- Uses a Spark session to load and process the full Spotify dataset.
- Uses Spark DataFrames for filtering, null checks, feature preparation, model input, PCA, and clustering.
- Uses Spark ML pipelines with `VectorAssembler`, `StandardScaler`, `PCA`, Linear Regression, Random Forest, and K-Means.
- Caches reused Spark DataFrames to reduce repeated computation during modeling and recommendation steps.
- Keeps Pandas conversion limited to local plots, summary tables, and final recommendation display.

## Repository Structure

```text
.
|-- README.md
|-- requirements.txt
|-- code/
|   |-- MusicDataAnalysisNRecommendationSystem_code.ipynb
|   `-- src/
|       `-- recommender.py
|-- data/
|   `-- Spotify_data.csv
`-- resources/
    |-- MusicDataAnalysisNRecommendationSystem_report.pdf
    `-- Music_Data_Analysis_Song_Recommendation.pptx
```

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Confirm the Spotify dataset exists at:

```text
data/Spotify_data.csv
```

3. Open and run the notebook:

```bash
jupyter notebook code/MusicDataAnalysisNRecommendationSystem_code.ipynb
```

## Expected Outputs

- Dataset loaded with Spark: `169,909` rows and `19` columns.
- Dataset year range: `1921` to `2020`.
- Main modeling mode: full dataset by default.
- Recent-years comparison slice: songs from `2015` to `2020`.
- Recommendation lookup supports `track_id`, `song_name`, and optional `artist_name`.
- Ambiguous song names return candidate tracks instead of silently choosing the wrong seed.
- Missing songs return a clear not-found result.

## Notes

This project is a content-based recommendation system. It recommends songs using audio-feature similarity rather than user listening behavior. Production recommendation systems usually combine content-based methods with collaborative filtering, user-item interaction data, ranking models, and feedback loops.

## Future Improvements

- Convert the notebook workflow into a full Python pipeline.
- Add user interaction data for collaborative filtering.
- Build a small Streamlit app for interactive song recommendations.
- Track experiments and model metrics in a structured format.
