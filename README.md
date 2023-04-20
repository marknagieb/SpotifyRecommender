# SpotifyRecommender
## Spotify Music Recommender
This is a Python project that uses machine learning and the Spotify API to provide personalized music recommendations. The system analyzes a user's listening habits and identifies patterns in their music preferences to provide music suggestions that match their unique tastes.

The project uses the K-Nearest Neighbors algorithm (KNN) to predict which songs a user is most likely to enjoy. The algorithm is trained using the user's top tracks, which are retrieved from the Spotify API. The data is preprocessed and fed into the algorithm using the Surprise library, which provides a clean and easy-to-use API for collaborative filtering and recommendation algorithms.

The Spotify API is used to retrieve additional information about the recommended songs, such as artist names, album titles, and track popularity. This information is displayed in a themed tkinter window with Spotify colors, which also includes a hyperlink to the song's page on Spotify's website and the predicted rating.

![image](https://user-images.githubusercontent.com/64073594/233243404-c39775f8-f2c7-4d28-ad68-f44df66bade8.png)


# Installation
Before running the project, you need to install the required packages. You can do this using pip:

``` pip install -r requirements.txt ```

You also need to set up your Spotify API credentials. You can do this by creating a .env file in the project directory with the following content:

``` client_id=<your_client_id> ```
``` client_secret=<your_client_secret> ```

Replace <your_client_id> and <your_client_secret> with your own credentials. You can obtain them from the Spotify Developer Dashboard.

# Usage
To run the project, simply run the spot.py file:

```python spot.py```

The program will prompt you to authenticate with Spotify using the Spotify Authorization flow. After authentication, it will display a list of the user's top tracks and their metadata. You can then use the KNNBasic algorithm from the Surprise library to train and test the model and get a list of recommended songs. The recommended songs are presented in a themed tkinter window with Spotify colors and include a hyperlink to the song's page on Spotify's website and the predicted rating.

# Contributing

Contributions to this project are welcome. If you find a bug or have a feature request, please open an issue. If you want to contribute code, please fork the repository and submit a pull request.

# License

This project is licensed under the MIT License. See the LICENSE file for more information.




