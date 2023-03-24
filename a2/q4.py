from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("MovieLens RDD") \
    .getOrCreate()


# Task 1: Find the average rating for each user and movie
# Load the ratings.csv file
ratings_rdd = spark.read.csv("ml-latest-small/ratings.csv", header=True, inferSchema=True).rdd

# Calculate the average rating for each user
user_avg_ratings = ratings_rdd.map(lambda x: (x[0], (x[2], 1))) \
    .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1])) \
    .mapValues(lambda x: x[0] / x[1])

# Calculate the average rating for each movie
movie_avg_ratings = ratings_rdd.map(lambda x: (x[1], (x[2], 1))) \
    .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1])) \
    .mapValues(lambda x: x[0] / x[1])

# Find the average rating for each genre
# Load the movies.csv file
movies_rdd = spark.read.csv("ml-latest-small/movies.csv", header=True, inferSchema=True).rdd

# Create a movie ID to genre mapping
movie_genres = movies_rdd.flatMap(lambda x: [(x[0], genre) for genre in x[2].split("|")]).collectAsMap()

# Calculate the average rating for each genre
def map_genres_with_ratings(x):
    movie_id, rating = x[1], x[2]
    genres = movie_genres[movie_id]
    return [(genre, (rating, 1)) for genre in genres]

genre_avg_ratings = ratings_rdd.flatMap(map_genres_with_ratings) \
    .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1])) \
    .mapValues(lambda x: x[0] / x[1])

# Collect the results
user_avg_ratings_list = user_avg_ratings.collect()
movie_avg_ratings_list = movie_avg_ratings.collect()
genre_avg_ratings_list = genre_avg_ratings.collect()

# Print the results
print("User average ratings:")
print(user_avg_ratings_list)
print("Movie average ratings:")
print(movie_avg_ratings_list)
print("Genre average ratings:")
print(genre_avg_ratings_list)

# Stop the Spark session
spark.stop()
