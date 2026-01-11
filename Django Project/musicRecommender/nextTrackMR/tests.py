from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .recommenderLogic import *
from .models import *
from .serializers import *
from .model_factories import *


# logic test
class recommenderLogicTest(TestCase):
    def setUp(self):
        Track.objects.create(
            track_id="4qEoqyPbLYnLOii6mKlIjI",
            track_name = "Determinate - From ""Lemonade Mouth""",
            fixed_track_name = "Determinate",
            danceability = 0.562,
            energy = 0.768,
            valence = 0.218,
            acousticness = 0.00361,
            tempo = 139.968,
            instrumentalness = 0.0,
            loudness = -5.006,
            normalized_vector = "[0.5376427541856083, 0.7679593928937565, 0.22312408520046265, 0.003619762009199307, 0.5703852259290954, 0.0, 0.8683863126794208]",
            finalized_vector="[0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]"
        )

        Track.objects.create(
            track_id="5lz0NiPw32Gq4kMIUJvuw2",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            danceability = 0.638,
            energy = 0.713,
            valence = 0.703,
            acousticness = 0.00103,
            tempo = 115.967,
            instrumentalness = 0.000241,
            loudness = -6.475,
            normalized_vector = "[0.621909302583435, 0.7129497662090866, 0.7195467712054371, 0.0010241572332865187, 0.41359690094657003, 0.0002424547283702213, 0.8376045093560757]",
            finalized_vector="[0.6841002328417786, 0.9981296726927211, 0.9354108025670682, 0.0013314044032724744, 0.4549565910412271, 0.0002909456740442656, 1.0051254112272907]"
        )

        Track.objects.create(
            track_id="1rM0CnyUiiw6A9CHJRXjZA",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            danceability = 0.638,
            energy = 0.713,
            valence = 0.703,
            acousticness = 0.00103,
            tempo = 115.967,
            instrumentalness = 0.000241,
            loudness = -6.475,
            normalized_vector = "[0.621909302583435, 0.7129497662090866, 0.7195467712054371, 0.0010241572332865187, 0.41359690094657003, 0.0002424547283702213, 0.8376045093560757]",
            finalized_vector="[0.756059430092028, 1.0849448653514364, 1.100407373668103, 0.041574344961911015, 0.44000287433286084, 0.0, 1.0003729857720596]"
        )

    # test if getting track vectors from database works
    def test_get_track_vectors_returns_valid_vectors(self):
        vectors = get_track_vectors_from_database(["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"])
        
        self.assertEqual(len(vectors), 2)
        # self.assertEqual(vectors[0],np.array([0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]))
        
    # test if getting track vectors from database works
    def test_get_track_vectors_returns_invalid(self):
        with self.assertRaises(ValueError):
            get_track_vectors_from_database(["abcdefg11234567"])

    # test if weighting is applied correctly
    def test_weight_vector_changes_energy_and_tempo(self):
        avg_vector = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

        normal = weight_vector(avg_vector.copy(), energy_weight=1.0, tempo_weight=1.0)
        high_energy = weight_vector(avg_vector.copy(), energy_weight=2.0, tempo_weight=1.0)
        low_tempo = weight_vector(avg_vector.copy(), energy_weight=1.0, tempo_weight=0.7)
        
        self.assertNotEqual(normal[1], high_energy[1]) 
        self.assertNotEqual(normal[4], low_tempo[4]) 

    # testing if euclidean equation gives correct answer
    def test_Euclidean_equation_is_correct(self):
        result = calculate_Euclidean(np.array([1,2]), np.array([1,1]))
        self.assertEqual(result, np.sqrt(1))

        result = calculate_Euclidean(np.array([1,2,3]), np.array([1,1,1]))
        self.assertEqual(result, np.sqrt(5))

    # # test if euclidean distances are stored correctly
    # def test_Euclidean_distance_data_are_correct(self):
    #     tracks = Track.objects.all()
    #     target = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

    #     distances = get_Euclidean_distance(tracks, target)
    #     self.assertEqual(len(distances), tracks.count()) 

    # test if minimum distance index is returned
    def test_get_track_with_minimum_distance_returns_correct_index(self):
        distances = [0.1, 0.3, 0.0, 0.9]
        min_index = get_track_index_with_minimum_distance(distances)
        
        self.assertEqual(min_index,2)

    # test if the recommender output is Track obj
    def test_recommenderLogicReturnsTrack(self):
        input_tracks = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_weight" : 1.0,
            "tempo_weight" : 1.2
        }
        result = recommend_Euclidean(input_tracks, input_preferences)

        self.assertIsInstance(result, Track)

# serializer test
class recommendTrackIdSerializerTest(APITestCase):

    def setUp(self):

        # full input is allowed 
        self.input_data1 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy_weight": 1.2,
                "tempo_weight": 0.5
            }
        }


        # optional preference input is allowed 
        self.input_data2 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"]
        }

        # invalid track input is not allowed 
        self.invalid_input_data1 = {
            "track_ids": ["", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy_weight": 1.2,
                "tempo_weight": 1.0
            }
        }

        # invalid track input is not allowed
        self.invalid_input_data2 = {
            "track_ids": ["abcdefg"],
            "preferences": {
                "energy_weight": 1.2,
                "tempo_weight": 0.4
            }
        }

        # no track input is not allowed
        self.invalid_input_data3 = {
            "preferences": {
                "energy_weight": 1.2,
                "tempo_weight": 0.5
            }
        }


        # invalid preferences is not allowed (0.5-1.5 is an appropriate range in my opinion)
        self.invalid_input_data4 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI"],
            "preferences": {
                "energy_weight": 1.6,
                "tempo_weight": 0.4
            }
        }

        # track input (not a list) is not allowed
        self.invalid_input_data5 = {
            "track_ids": "4qEoqyPbLYnLOii6mKlIjI",
            "preferences": {
                "energy_weight": 1.0,
                "tempo_weight": 1.0
            }
        }

    # valid data testing
    def test_recommenderInputSerializerValidData(self):
        serializer = RecommenderInputSerializer(data = self.input_data1)
        self.assertTrue(serializer.is_valid())

        serializer = RecommenderInputSerializer(data = self.input_data2)
        self.assertTrue(serializer.is_valid())

    # invalid data testing
    def test_recommenderInputSerializerInvalidData(self):
        serializer = RecommenderInputSerializer(data = self.invalid_input_data1)
        self.assertFalse(serializer.is_valid())

        serializer = RecommenderInputSerializer(data = self.invalid_input_data2)
        self.assertFalse(serializer.is_valid())

        serializer = RecommenderInputSerializer(data = self.invalid_input_data3)
        self.assertFalse(serializer.is_valid())

        serializer = RecommenderInputSerializer(data = self.invalid_input_data4)
        self.assertFalse(serializer.is_valid())
        
        serializer = RecommenderInputSerializer(data = self.invalid_input_data5)
        self.assertFalse(serializer.is_valid())

# api test
class recommendTrackIDTest(APITestCase):

    def setUp(self):
        self.good_url = reverse('recommend_track_api')

        # full valid input
        self.good_input1 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
                            "preferences": {
                                "energy_weight": 1.2,
                                "tempo_weight": 1.0
                            }}
        
        # no preferences
        self.good_input2 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"]}
        
        # only one track input
        self.good_input3 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI"]}

        # invalid track id (string)
        self.bad_input1 = {"track_ids" : "a",
                          "preferences": {
                                "energy_weight": 1.2,
                                "tempo_weight": 1.0
                            }}
        
        # invalid preferences range
        self.bad_input2 = {"track_ids" : ["4qEoqyPbLYnLOii6mKlIjI"],
                          "preferences": {
                                "energy_weight": 0.2,
                                "tempo_weight": 1.0
                            }}
        
        # invalid track_ids
        self.bad_input3 = {"track_ids" : ["abcdefg"],
                          "preferences": {
                                "energy_weight": 1.1,
                                "tempo_weight": 1.0
                            }}
        
        # no track_ids
        self.bad_input4 = {"preferences": {
                                "energy_weight": 1.1,
                                "tempo_weight": 1.0
                            }}
        
        # no track (empty list)
        self.bad_input5 = {"track_ids" : [],
                          "preferences": {
                                "energy_weight": 1.1,
                                "tempo_weight": 1.0
                            }}
        
        # invalid preferences
        self.bad_input6 = {"track_ids" : ["4qEoqyPbLYnLOii6mKlIjI"],
                          "preferences": {
                                "energy_weight": "high",
                                "tempo_weight": "low"
                            }}
        
        
        
        Track.objects.create(
            track_id="4qEoqyPbLYnLOii6mKlIjI",
            track_name = "Determinate - From ""Lemonade Mouth""",
            fixed_track_name = "Determinate",
            danceability = 0.562,
            energy = 0.768,
            valence = 0.218,
            acousticness = 0.00361,
            tempo = 139.968,
            instrumentalness = 0.0,
            loudness = -5.006,
            normalized_vector = "[0.5376427541856083, 0.7679593928937565, 0.22312408520046265, 0.003619762009199307, 0.5703852259290954, 0.0, 0.8683863126794208]",
            finalized_vector="[0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]"
        )

        Track.objects.create(
            track_id="5lz0NiPw32Gq4kMIUJvuw2",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            danceability = 0.638,
            energy = 0.713,
            valence = 0.703,
            acousticness = 0.00103,
            tempo = 115.967,
            instrumentalness = 0.000241,
            loudness = -6.475,
            normalized_vector = "[0.621909302583435, 0.7129497662090866, 0.7195467712054371, 0.0010241572332865187, 0.41359690094657003, 0.0002424547283702213, 0.8376045093560757]",
            finalized_vector="[0.6841002328417786, 0.9981296726927211, 0.9354108025670682, 0.0013314044032724744, 0.4549565910412271, 0.0002909456740442656, 1.0051254112272907]"
        )

        Track.objects.create(
            track_id="1rM0CnyUiiw6A9CHJRXjZA",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            danceability = 0.638,
            energy = 0.713,
            valence = 0.703,
            acousticness = 0.00103,
            tempo = 115.967,
            instrumentalness = 0.000241,
            loudness = -6.475,
            normalized_vector = "[0.621909302583435, 0.7129497662090866, 0.7195467712054371, 0.0010241572332865187, 0.41359690094657003, 0.0002424547283702213, 0.8376045093560757]",
            finalized_vector="[0.756059430092028, 1.0849448653514364, 1.100407373668103, 0.041574344961911015, 0.44000287433286084, 0.0, 1.0003729857720596]"
        )

       
    # good url and input returns valid
    def test_recommendTrackIdReturnsSuccess(self):
        response = self.client.post(self.good_url, 
                                    self.good_input1,
                                    format= 'json')
        self.assertEqual(response.status_code,200) 

        response = self.client.post(self.good_url, 
                                    self.good_input2,
                                    format= 'json')
        self.assertEqual(response.status_code,200)   

        response = self.client.post(self.good_url, 
                                    self.good_input3,
                                    format= 'json')
        self.assertEqual(response.status_code,200) 

    def test_recommendTrackIdReturnsError(self):
        response = self.client.post(self.good_url,
                                    self.bad_input1,
                                    format = 'json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.good_url,
                                    self.bad_input2,
                                    format = 'json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.good_url,
                                    self.bad_input3,
                                    format = 'json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.good_url,
                                    self.bad_input4,
                                    format = 'json')
        self.assertEqual(response.status_code, 400)

        # response = self.client.post(self.good_url,
        #                             self.bad_input5,
        #                             format = 'json')
        # self.assertEqual(response.status_code, 400)

        response = self.client.post(self.good_url,
                                    self.bad_input6,
                                    format = 'json')
        self.assertEqual(response.status_code, 400)








        

