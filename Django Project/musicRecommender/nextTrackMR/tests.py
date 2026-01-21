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
        
        self.artist1 = Artist.objects.create(
            artist_id = '6sCbFbEjbYepqswM1vWjjs',
            artist_name = 'Zendaya',
        )
        self.artist2 = Artist.objects.create(
            artist_id = '7bp2lSdh12wcA8LyB1srfJ',
            artist_name = 'Sofia Carson'
        )
        self.artist3 = Artist.objects.create(
            artist_id = '3dctbbXhrRgigX1icexnws',
            artist_name = 'Adam Hicks'            
        )
        self.artist4 = Artist.objects.create(
            artist_id = '45af7IeC0N5gQ9cyoIFyS6',
            artist_name = 'Rowan Blanchard'            
        )
        
        # real track data
        self.track1 = TrackFactory.create(
            track_id='744ZuzjXQmoJmOdk2I1ym9',
            track_name='"Keep It Undercover - Theme Song From ""K.C. Undercover"""', 
            fixed_track_name = 'Keep It Undercover',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track5 = TrackFactory.create(
            track_id="4qEoqyPbLYnLOii6mKlIjI",
            track_name = "Determinate - From ""Lemonade Mouth""",
            fixed_track_name = "Determinate",
            finalized_vector="[0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]"
        )
        self.track6 = TrackFactory.create(
            track_id="5lz0NiPw32Gq4kMIUJvuw2",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            finalized_vector="[0.6841002328417786, 0.9981296726927211, 0.9354108025670682, 0.0013314044032724744, 0.4549565910412271, 0.0002909456740442656, 1.0051254112272907]"
        )
        self.track7 = TrackFactory.create(
            track_id="1rM0CnyUiiw6A9CHJRXjZA",
            track_name = "Chillin' Like a Villain",
            fixed_track_name = "Chillin' Like a Villain",
            finalized_vector="[0.756059430092028, 1.0849448653514364, 1.100407373668103, 0.041574344961911015, 0.44000287433286084, 0.0, 1.0003729857720596]"
        )

        # fake data (mostly for random model testing)
        self.track2 = TrackFactory.create(
            track_id='abcdefghijklmnopqrstuv',
            track_name='random song by Zendaya', 
            fixed_track_name = 'random song 1 by Zendaya',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track3 = TrackFactory.create(
            track_id='klmnopqrstuvabcdefghij',
            track_name='random song 2 by Zendaya', 
            fixed_track_name = 'random song 2 by Zendaya',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track4 = TrackFactory.create(
            track_id='pqrstuvabcklmnodefghij',
            track_name='random song 1 by Sofia Carson', 
            fixed_track_name = 'random song 1 by Sofia Carson',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.trackCollab = TrackFactory.create(
            track_id='uvabcklmnopqrstdefghij',
            track_name='random song 1 by Sofia Carson & Zendaya', 
            fixed_track_name = 'random song 1 by Sofia Carson & Zendaya',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.trackNoLink = TrackFactory.create(
            track_id='uvabcklefghijmnopqrstd',
            track_name='this track has no link table, so no artist linked to this track', 
            fixed_track_name = 'this track has no link table, so no artist linked to this track',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )

        self.link1 = TrackArtistLink.objects.create(
            track= self.track1, 
            artist= self.artist1
        )
        self.link2 = TrackArtistLink.objects.create(
            track= self.track2, 
            artist= self.artist1
        )
        self.link3 = TrackArtistLink.objects.create(
            track= self.track3, 
            artist= self.artist1
        )
        self.link4 = TrackArtistLink.objects.create(
            track = self.track4,
            artist = self.artist2
        )
        # collab links (one song , two singers)
        self.link5 = TrackArtistLink.objects.create(
            track = self.trackCollab,
            artist = self.artist1
        )
        self.link6 = TrackArtistLink.objects.create(
            track = self.trackCollab,
            artist = self.artist2
        )
        # end of collab links
        self.link7 = TrackArtistLink.objects.create(
            track = self.track5,
            artist = self.artist3
        )
        self.link8 = TrackArtistLink.objects.create(
            track = self.track6,
            artist = self.artist4
        )
        self.link9 = TrackArtistLink.objects.create(
            track = self.track7,
            artist = self.artist2
        )
        




    # test if getting track vectors from database works
    def test_get_track_vectors_returns_valid_vectors(self):
        vectors = get_track_vectors_from_database(["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"])
        
        self.assertEqual(len(vectors), 2)
        # self.assertEqual(vectors[0],np.array([0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]))
        
    # test if getting track vectors from database raise error for invalid input
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
        self.assertGreater(high_energy[1], normal[1])
        self.assertNotEqual(normal[4], low_tempo[4]) 
        self.assertLess(low_tempo[4], normal[4])

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

    # test if minimum distance index is returned correctly
    def test_get_track_with_minimum_distance_returns_correct_index(self):
        distances = [0.1, 0.3, 0.0, 0.9]
        min_index = get_track_index_with_minimum_distance(distances)
        
        self.assertEqual(min_index,2)

    # test if the Euclidean recommender output is Track obj
    def test_recommenderLogicReturnsTrack(self):
        input_tracks = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_weight" : 1.0,
            "tempo_weight" : 1.2
        }
        result = recommend_Euclidean(input_tracks, input_preferences)

        self.assertIsInstance(result, Track)


    ############### baseline model testing ###############

    ###### cosine similarity testing ######

    # test if cosine similarity returns correct value
    def test_cosine_equation_is_correct(self):
        vector1 = np.array([1,1,1])
        vector2 = np.array([1,2,3])
        result = calculate_Cosine(vector1, vector2)

        # dot = 1 * 1 + 1 * 2 + 1 * 3 = 6
        # vector1 mag = sqrt(3)
        # vector2 mag = sqrt(14)
        expectedResult = 6 / (np.sqrt(3) * np.sqrt(14))
        self.assertAlmostEqual(result, expectedResult)

    # test if the closest to 1 index is returned and 
    # distances less than -1 are considered invalid and raise error
    def test_get_closest_to_one_index_returns_correct_index(self):
        distances = [-1.1, -1.0, 0, 0.1, 0.12]
        result = get_closest_to_one_index(distances)
       
        self.assertEqual(result, 4)


        wrong_distances = [-1.1, -1.5]
        with self.assertRaises(ValueError):
            result1 = get_closest_to_one_index(wrong_distances)

    # test if the cosine recommender logic returns track instance
    def test_recommend_Cosine_returns_track(self):
        input_tracks = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_weight" : 1.0,
            "tempo_weight" : 1.2
        }
        result = recommend_Cosine(input_tracks, input_preferences)

        self.assertIsInstance(result, Track)



    ###### random by artist testing ######
    # test if get_artist_ids_list returns list of related artist ids to input tracks
    def test_get_artist_ids_list_returns_correct_artist_ids(self):
        # two 1-artist songs, one 2-artists song , so 4 artist ids should be returned
        artist_ids_list = get_artist_ids_list(['744ZuzjXQmoJmOdk2I1ym9', '5lz0NiPw32Gq4kMIUJvuw2','uvabcklmnopqrstdefghij'])
        
        # check if returned list is length of 4 
        self.assertEqual(len(artist_ids_list), 4)
        # check if correct artist ids contain in returned list
        self.assertIn('6sCbFbEjbYepqswM1vWjjs', artist_ids_list)
        self.assertIn('45af7IeC0N5gQ9cyoIFyS6', artist_ids_list)
        self.assertIn('7bp2lSdh12wcA8LyB1srfJ', artist_ids_list)

        # check if incorrect artist id does not contain in returned list
        self.assertNotIn('3dctbbXhrRgigX1icexnws', artist_ids_list)

        # check if returned list is of correct artist ids
        self.assertEqual(artist_ids_list, ['6sCbFbEjbYepqswM1vWjjs', '45af7IeC0N5gQ9cyoIFyS6', '6sCbFbEjbYepqswM1vWjjs', '7bp2lSdh12wcA8LyB1srfJ'])

    # test if get_artist_ids_list raises error if invalid inputs are entered
    def test_get_artist_ids_list_raises_error_for_invalid_input(self):
        # check if not-in-db track id returns error
        with self.assertRaises(ValueError):
            get_artist_ids_list(["abcdefghijklmn11234567"])         # track id not in database

        # check if invalid track id returns error
        with self.assertRaises(ValueError):
            get_artist_ids_list(["abcdefghijkl"])

        # check if track without artist returns error
        with self.assertRaises(ValueError):
            get_artist_ids_list(["3dctbbXhrRgigX1icexnws", "uvabcklefghijmnopqrstd"])       # good input and track id with no related artist 

    # test if artist and their frequency are correct
    def test_get_artist_id_freq_returns_correct_data(self):
        artist_freq = get_artist_id_freq(['abc', 'abc', 'def', 'abc'])
        self.assertEqual(artist_freq, {'abc' : 3, 'def': 1})

    # test if the correct maximum value is returned 
    def test_get_max_freq_of_artist_returns_correct_max(self):
        artist_freq = get_artist_id_freq(['abc', 'abc', 'def', 'abc'])      
        max_freq = get_max_freq_of_artist(artist_freq)

        artist_freq1 = get_artist_id_freq(['abc', 'abc', 'def', 'def'])     # two same freq
        max_freq1 = get_max_freq_of_artist(artist_freq1)

        artist_freq2 = get_artist_id_freq(['abc'])     # only one input artist id
        max_freq2 = get_max_freq_of_artist(artist_freq2)
        
        artist_freq3 = get_artist_id_freq([])     # no input artist id
        max_freq3 = get_max_freq_of_artist(artist_freq3)

        self.assertEqual(max_freq, 3)
        self.assertEqual(max_freq1, 2)
        self.assertEqual(max_freq2, 1)
        self.assertEqual(max_freq3, 0)

    # test if the correct list of most frequent artist ids is returned
    def test_get_most_frequent_artists_returns_correct(self):
        artist_ids = ['abc', 'abc', 'def', 'def']
        artist_freq = get_artist_id_freq(artist_ids)     
        max_freq = get_max_freq_of_artist(artist_freq)

        artist_ids1 = ['abc', 'abc', 'abc', 'def']
        artist_freq1 = get_artist_id_freq(artist_ids1)     
        max_freq1 = get_max_freq_of_artist(artist_freq1)

        artist_ids2 = ['abc']
        artist_freq2 = get_artist_id_freq(artist_ids2)     
        max_freq2 = get_max_freq_of_artist(artist_freq2)

        artist_ids3 = []
        artist_freq3 = get_artist_id_freq(artist_ids3)     
        max_freq3 = get_max_freq_of_artist(artist_freq3)

        top_artists = get_most_frequent_artists(artist_ids, artist_freq, max_freq)
        top_artists1 = get_most_frequent_artists(artist_ids1, artist_freq1, max_freq1)
        top_artists2 = get_most_frequent_artists(artist_ids2, artist_freq2, max_freq2)
        top_artists3 = get_most_frequent_artists(artist_ids3, artist_freq3, max_freq3)

        self.assertEqual(len(top_artists), 2)
        self.assertEqual(top_artists, ['abc','def'])
        self.assertEqual(len(top_artists1), 1)
        self.assertEqual(top_artists1, ['abc'])
        self.assertEqual(len(top_artists2), 1)
        self.assertEqual(top_artists2, ['abc'])
        self.assertEqual(top_artists3, None)
    
    # test if get_random_track_row_of_chosen_artist returns correct random track if input are valid 
    def test_get_random_track_row_of_chosen_artist_returns_correct(self):
        chosen_artists = '6sCbFbEjbYepqswM1vWjjs'
        input_tracks = ['1rM0CnyUiiw6A9CHJRXjZA', 'abcdefghijklmnopqrstuv']
        random_track = get_random_track_row_of_chosen_artist(chosen_artists, input_tracks)
        
        self.assertIn (random_track, [self.track1, self.track3, self.trackCollab])        # track 1,3, collab
        self.assertNotIn(random_track, [self.track2, self.track4, self.track5, self.track6, self.track7, self.trackNoLink])      # 2,4,5,6,7,notracklink
    
    #  test if get_random_track_row_of_chosen_artist returns None if input are invalid
    def test_get_random_track_row_of_chosen_artist_returns_none(self):
        chosen_artists = ''
        input_tracks = ['1rM0CnyUiiw6A9CHJRXjZA', 'abcdefghijklmnopqrstuv']
        
        
        with self.assertRaises(ValueError):
            get_random_track_row_of_chosen_artist(chosen_artists, input_tracks)
        
    # test if get_any_random_track returns a random track object (but not the tracks in input list of track ids)
    def test_get_any_random_track_returns_correct(self):
        # the list of all tracks in the temporary database without the only track id '744ZuzjXQmoJmOdk2I1ym9'
        input_tracks = ['4qEoqyPbLYnLOii6mKlIjI', '5lz0NiPw32Gq4kMIUJvuw2', '1rM0CnyUiiw6A9CHJRXjZA', 'abcdefghijklmnopqrstuv', 'pqrstuvabcklmnodefghij', 'klmnopqrstuvabcdefghij', 'uvabcklmnopqrstdefghij', 'uvabcklefghijmnopqrstd']
        expected_track = '744ZuzjXQmoJmOdk2I1ym9'       # the only track id not included in input_tracks list
        random_track = get_any_random_track(input_tracks)
        
        self.assertIsInstance(random_track, Track)
        self.assertEqual(random_track.track_id, expected_track)

        with self.assertRaises(ValueError):     # for None case (no more tracks to be selected from the database)
            get_any_random_track(input_tracks + [expected_track])

    # test if random by artist model returns a track object
    def test_recommend_random_by_artist_returns_track(self):
        input_tracks = ['744ZuzjXQmoJmOdk2I1ym9', 'uvabcklmnopqrstdefghij', '1rM0CnyUiiw6A9CHJRXjZA']
        
        result = recommend_random_by_artist(input_tracks)
        # self.assertIsInstance(result, Track)


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








        

