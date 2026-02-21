from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase

from .views import *
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

    #######################deleted code test #############################
    # # test if the closest to 1 index is returned and 
    # # distances less than -1 are considered invalid and raise error
    # def test_get_closest_to_one_index_returns_correct_index(self):
    #     distances = [-1.1, -1.0, 0, 0.1, 0.12]
    #     result = get_closest_to_one_index(distances)
       
    #     self.assertEqual(result, 4)


    #     wrong_distances = [-1.1, -1.5]
    #     with self.assertRaises(ValueError):
    #         result1 = get_closest_to_one_index(wrong_distances)

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
        self.assertEqual(type(artist_freq), Counter)        # returned type is Counter

    ############deleted code test##################
    # # test if the correct maximum value is returned 
    # def test_get_max_freq_of_artist_returns_correct_max(self):
    #     artist_freq = get_artist_id_freq(['abc', 'abc', 'def', 'abc'])      
    #     max_freq = get_max_freq_of_artist(artist_freq)

    #     artist_freq1 = get_artist_id_freq(['abc', 'abc', 'def', 'def'])     # two same freq
    #     max_freq1 = get_max_freq_of_artist(artist_freq1)

    #     artist_freq2 = get_artist_id_freq(['abc'])     # only one input artist id
    #     max_freq2 = get_max_freq_of_artist(artist_freq2)
        
    #     artist_freq3 = get_artist_id_freq([])     # no input artist id
    #     max_freq3 = get_max_freq_of_artist(artist_freq3)

    #     self.assertEqual(max_freq, 3)
    #     self.assertEqual(max_freq1, 2)
    #     self.assertEqual(max_freq2, 1)
    #     self.assertEqual(max_freq3, 0)

    ############deleted code test##################
    # # test if the correct list of most frequent artist ids is returned
    # def test_get_most_frequent_artists_returns_correct(self):
    #     artist_ids = ['abc', 'abc', 'def', 'def']
    #     artist_freq = get_artist_id_freq(artist_ids)     
    #     max_freq = get_max_freq_of_artist(artist_freq)

    #     artist_ids1 = ['abc', 'abc', 'abc', 'def']
    #     artist_freq1 = get_artist_id_freq(artist_ids1)     
    #     max_freq1 = get_max_freq_of_artist(artist_freq1)

    #     artist_ids2 = ['abc']
    #     artist_freq2 = get_artist_id_freq(artist_ids2)     
    #     max_freq2 = get_max_freq_of_artist(artist_freq2)

    #     artist_ids3 = []
    #     artist_freq3 = get_artist_id_freq(artist_ids3)     
    #     max_freq3 = get_max_freq_of_artist(artist_freq3)

    #     top_artists = get_most_frequent_artists(artist_ids, artist_freq, max_freq)
    #     top_artists1 = get_most_frequent_artists(artist_ids1, artist_freq1, max_freq1)
    #     top_artists2 = get_most_frequent_artists(artist_ids2, artist_freq2, max_freq2)
    #     top_artists3 = get_most_frequent_artists(artist_ids3, artist_freq3, max_freq3)

    #     self.assertEqual(len(top_artists), 2)
    #     self.assertEqual(top_artists, ['abc','def'])
    #     self.assertEqual(len(top_artists1), 1)
    #     self.assertEqual(top_artists1, ['abc'])
    #     self.assertEqual(len(top_artists2), 1)
    #     self.assertEqual(top_artists2, ['abc'])
    #     self.assertEqual(top_artists3, None)
    
    ############deleted code test##################
    # # test if get_random_track_row_of_chosen_artist returns correct random track if input are valid 
    # def test_get_random_track_row_of_chosen_artist_returns_correct(self):
    #     chosen_artists = '6sCbFbEjbYepqswM1vWjjs'
    #     input_tracks = ['1rM0CnyUiiw6A9CHJRXjZA', 'abcdefghijklmnopqrstuv']
    #     random_track = get_random_track_row_of_chosen_artist(chosen_artists, input_tracks)
        
    #     self.assertIn (random_track, [self.track1, self.track3, self.trackCollab])        # track 1,3, collab
    #     self.assertNotIn(random_track, [self.track2, self.track4, self.track5, self.track6, self.track7, self.trackNoLink])      # 2,4,5,6,7,notracklink
    
    ############deleted code test##################
    # #  test if get_random_track_row_of_chosen_artist returns None if input are invalid
    # def test_get_random_track_row_of_chosen_artist_returns_none(self):
    #     chosen_artists = ''
    #     input_tracks = ['1rM0CnyUiiw6A9CHJRXjZA', 'abcdefghijklmnopqrstuv']
        
        
    #     with self.assertRaises(ValueError):
    #         get_random_track_row_of_chosen_artist(chosen_artists, input_tracks)
    
    ############deleted code test##################
    # # test if get_any_random_track returns a random track object (but not the tracks in input list of track ids)
    # def test_get_any_random_track_returns_correct(self):
    #     # the list of all tracks in the temporary database without the only track id '744ZuzjXQmoJmOdk2I1ym9'
    #     input_tracks = ['4qEoqyPbLYnLOii6mKlIjI', '5lz0NiPw32Gq4kMIUJvuw2', '1rM0CnyUiiw6A9CHJRXjZA', 'abcdefghijklmnopqrstuv', 'pqrstuvabcklmnodefghij', 'klmnopqrstuvabcdefghij', 'uvabcklmnopqrstdefghij', 'uvabcklefghijmnopqrstd']
    #     expected_track = '744ZuzjXQmoJmOdk2I1ym9'       # the only track id not included in input_tracks list
    #     random_track = get_any_random_track(input_tracks)
        
    #     self.assertIsInstance(random_track, Track)
    #     self.assertEqual(random_track.track_id, expected_track)

    #     with self.assertRaises(ValueError):     # for None case (no more tracks to be selected from the database)
    #         get_any_random_track(input_tracks + [expected_track])

    ############deleted code test##################
    # # test if random by artist model returns a track object
    # def test_recommend_random_by_artist_returns_track(self):
    #     input_tracks = ['744ZuzjXQmoJmOdk2I1ym9', 'uvabcklmnopqrstdefghij', '1rM0CnyUiiw6A9CHJRXjZA']
        
    #     result = recommend_random_by_artist(input_tracks)

    ################top k - testing#################
    ###################Euclidean ###################

    # test if get_top_tracks returns correct data
    def test_get_top_tracks_return_correct(self):
        comparison_results = [(self.track1, 0.1),(self.track4, 0.4),(self.track7, 0.6),(self.track3, 0.3),
                              (self.track6, 0.5),(self.track2, 0.2),(self.track5, 0.4),(self.trackCollab, 0.7)]
        k = 5
        higher_Cosine = True # Cosine (higher to lower => highest results returned)
        higher_Euclidean = False # Euclidean (lower to higher => lowest results returned)

        output_Cosine = get_top_tracks(comparison_results, k, higher_Cosine)
        output_ids_Cosine = {t.track_id for t in output_Cosine}
        output_Euclidean = get_top_tracks(comparison_results, k, higher_Euclidean)
        output_ids_Euclidean = {t.track_id for t in output_Euclidean}


        expected_output_Cosine = [self.trackCollab, self.track7, self.track6, self.track5, self.track4]
        expected_output_Euclidean = [self.track1, self.track2, self.track3, self.track4, self.track5]
        expected_ids_Cosine = {t.track_id for t in expected_output_Cosine}
        expected_ids_Euclidean = {t.track_id for t in expected_output_Euclidean}

        self.assertEqual(len(output_Cosine), k)     # no: of elements in output is k
        self.assertTrue(expected_ids_Cosine.issubset(output_ids_Cosine))        # expected_ids are in output ids
        self.assertIsInstance(output_Cosine[0], Track)      # of Track instance

        self.assertTrue(expected_ids_Euclidean.issubset(output_ids_Euclidean))      # expected_ids are in output ids

    # test if recommend_euclidean_topk returns correct data
    def test_recommend_Euclidean_topk_returns_correct(self):
              
        input_track_ids = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_weight" : 1.0,
            "tempo_weight" : 1.2
        }
        k = 4

        recommended = recommend_Euclidean_topk(input_track_ids, input_preferences, k = k)       # k value is given
        recommended_ids = {t.track_id for t in recommended}

        self.assertIsInstance(recommended, list)        # the returned data is list
        self.assertEqual (len(recommended), k)  # len of returned list is k 

        self.assertEqual(len(set(recommended_ids)), len(recommended_ids)) # no duplicate
        
        # elements of the returned list are Track instance
        for t in recommended:
            self.assertIsInstance(t, Track)

        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids)

        recommended1 = recommend_Euclidean_topk(input_track_ids, input_preferences)     # no k value given
        self.assertIsInstance(recommended1, list)
        self.assertEqual(len(recommended1), 1)              

        
    ###################Cosine ######################

    # test if recommend_cosine_topk returns correct data
    def test_recommend_Cosine_topk_returns_correct(self):
              
        input_track_ids = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_weight" : 1.0,
            "tempo_weight" : 1.2
        }
        k = 4

        recommended = recommend_Cosine_topk(input_track_ids, input_preferences, k = k)       # k value is given
        recommended_ids = {t.track_id for t in recommended}

        self.assertIsInstance(recommended, list)        # the returned data is list
        self.assertEqual (len(recommended), k)  # len of returned list is k 

        self.assertEqual(len(set(recommended_ids)), len(recommended_ids)) # no duplicates

        # elements of the returned list are Track instance
        for t in recommended:
            self.assertIsInstance(t, Track)

        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids)

        # one track recommendation 
        recommended1 = recommend_Cosine_topk(input_track_ids, input_preferences)     # no k value given
        self.assertIsInstance(recommended1, list)
        self.assertEqual(len(recommended1), 1) 


    ###################random by artist ##############
    def test_get_artist_frequency_ranking_returns_correct(self):
        artist_freq = Counter({'a': 1, 'b': 2, 'c': 4, 'd': 2})
        ranking_list = get_artist_frequency_ranking(artist_freq)
        
        self.assertEqual(type(ranking_list), list)
        self.assertEqual(ranking_list, [('c',4),('b',2),('d',2),('a',1)])



    # test if get_list_of_random_track_rows_of_chosen_artist returns correct data
    def test_get_list_of_random_track_rows_of_chosen_artist_returns_correct(self):
        chosen_artist_id = '7bp2lSdh12wcA8LyB1srfJ'     #Sofia Carson # artist 2 > songs : track 4, 7, collab
        input_track_ids = ['pqrstuvabcklmnodefghij']        #track 4
        recommended_tracks = [self.track7]         #track 7
        list_of_tracks = get_list_of_random_track_rows_of_chosen_artist(chosen_artist_id, input_track_ids,recommended_tracks)
        expected_tracks = [self.trackCollab]       
        
        self.assertEqual(type(list_of_tracks), list)        # return type : list
        self.assertIsInstance(list_of_tracks[0], Track)     #list's element : Track
        self.assertEqual(len(list_of_tracks), 1)        # there are 3 tracks by the chosen_artist_id in the setup, so, the returned list should have 1 element (excluding the one input track and one recommended track)
        self.assertIn(expected_tracks[0], list_of_tracks)       # expected tracks are in the retured list of tracks
        self.assertNotIn(self.track4, list_of_tracks)       # input not in result
        self.assertNotIn(self.track7, list_of_tracks)       #track in recommended_tracks not in result

    # test if add_tracks_to_recommended_tracks_list returns correct
    def test_add_tracks_to_recommended_tracks_list_returns_correct(self):
        tracks = [self.track4, self.track7]
        recommended_tracks = [self.trackCollab, self.track1]
        k = 3
        self.assertEqual(len(recommended_tracks), 2)        # originally recommended_tracks has 2 tracks
        
        result = add_tracks_to_recommended_tracks_list(tracks, recommended_tracks, k)

        self.assertEqual(len(result), 3)        #output has 3 tracks
        self.assertIn(tracks[0], result)        # first element of tracks is in result now

    # test if get_non_repeating_random_tracks returns correct
    def test_get_non_repeating_random_tracks_returns_correct(self):
        # total track declared in this class => 1 to 7 tracks + 2 others (trackCollab, trackNoLink)
        input_tracks_id = [self.track1.track_id, self.track2.track_id, self.track3.track_id]        # 3 tracks
        recommended_tracks = [self.track4, self.track5, self.track6]        # 3 tracks
        result = get_non_repeating_random_tracks(input_tracks_id, recommended_tracks)          # should get 3 other tracks (7, trackCollab, trackNoLink)

        self.assertEqual(len(result), 3)        #3 tracks
        self.assertIsInstance(result[0], Track)     #elements are of Track
        #  3 tracks should be in result  
        self.assertIn(self.track7, result)
        self.assertIn(self.trackCollab, result)
        self.assertIn(self.trackNoLink, result)

    # test if recommend_random_by_artist works correctly
    def test_recommend_random_by_artist_topk(self):
        # artist1 has 4 songs, artist2  has 3 songs, artist3 and artist4 has 1 song each + 1 track has no artist. (artist1 and 2 have once common song.)
        input_track_ids = [self.track4.track_id, self.track1.track_id, self.track2.track_id]    # track 1 and 2 are of artist1, track 4 is of the artist2.
        # with input defined like this, artist1's other 2 songs, artist2's other 2 songs, should be in the output. Since they have 1 common song, it will be 3 songs eligible for recommendation. 
        # k will be set to 4. and therefore, 3 songs of artist1 and 2 and 1 song from any other tracks are included in the output.
        k = 4
        output = recommend_random_by_artist_topk(input_track_ids, k=k)

        self.assertEqual(len(output), k)        # length of output is equal to k 
        self.assertIsInstance(output[0], Track)     #element is Track instance

        # 3 tracks + 1 from the other 2 tracks should be in output
        self.assertIn(self.track3, output)
        self.assertIn(self.track7, output)
        self.assertIn(self.trackCollab, output)
        self.assertIn(output[3], [self.track5, self.track6, self.trackNoLink])

        # input not included in output
        self.assertNotIn(self.track4, output)
        self.assertNotIn(self.track1, output)
        self.assertNotIn(self.track2, output)

        # no duplicates
        track_ids = [t.track_id for t in output]
        self.assertEqual(len(track_ids), len(set(track_ids)))

        output1 = recommend_random_by_artist_topk(input_track_ids)
        self.assertEqual(len(output1), 1)
        expected_outputs = [self.track3, self.trackCollab]
        self.assertIn(output1[0], expected_outputs)
        self.assertIsInstance(output[0], Track)

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

# view (frontend) test
class frontendFunctionsTest(TestCase):
    
    def setUp(self):
        self.client = Client()  

        # artists
        self.artist1 = Artist.objects.create(
            artist_id = '6sCbFbEjbYepqswM1vWjjs',
            artist_name = 'Zendaya',
        )
        self.artist2 = Artist.objects.create(
            artist_id = '7bp2lSdh12wcA8LyB1srfJ',
            artist_name = 'Sofia Carson'
        )

        # tracks
        self.track1 = TrackFactory.create(
            track_id='744ZuzjXQmoJmOdk2I1ym9',
            track_name='"Keep It Undercover - Theme Song From ""K.C. Undercover"""', 
            fixed_track_name = 'Keep It Undercover',
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

        # links
        self.link1 = TrackArtistLink.objects.create(
            track= self.track1, 
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
    
    # index function testing
    # test if index function loads okay, use the right template
    def test_index_loads_correctly(self):
        response = self.client.get(reverse('index'))
        
        self.assertEqual(response.status_code, 200)     # check if the url is successful
        self.assertTemplateUsed(response, 'nextTrackMR/index.html')     # check if the correct template is rendered

    # test if session variables are true and passed to the html file correctly from the index function
    def test_session_vars_are_correct(self):
        sessionVar = self.client.session
        sessionVar['input_tracks'] = ['abcdefg']
        sessionVar['recommended_track'] = 'Photograph'
        sessionVar['preferences'] = {'energy_weight': "Medium", 'tempo_weight': "Medium"}

        sessionVar.save()

        response = self.client.get(reverse('index'))

        # test if the session variables and variables passed to HTML are the same (checking for all three sessioin variables)
        self.assertEqual(response.context['tracks'], sessionVar['input_tracks'])        
        self.assertEqual(response.context['recommended_track'], sessionVar['recommended_track'])
        self.assertEqual(response.context['preferences'], sessionVar['preferences'])

    # addTrack funtion testing
    # testing if the add_to_inputs url does correctly, session variable is created and stores a correct input
    def test_add_track_correct(self):
        add_track_url = '/add_to_inputs/'
        valid_input_id = '4TSxpQC5oY6XBkUSLPYM6G'

        response = self.client.post(add_track_url, {'input_track_id' : valid_input_id})

        sessionVar = self.client.session
        self.assertEqual(response.status_code, 302)     #redirected 
        self.assertIn('input_tracks',sessionVar)        #input_tracks session var is created
        self.assertEqual(len(sessionVar['input_tracks']), 1)        #input_tracks session var has one element in it
        self.assertEqual(sessionVar["input_tracks"][0]['id'], valid_input_id)       # the element in the input_tracks session var is track details related to the input id

    def test_add_track_invalid(self):
        response = self.client.post('/add_to_inputs/', {})

        self.assertEqual(response.status_code, 302)     # redirecting ok

        sessionVar = self.client.session
        self.assertIn('input_tracks',sessionVar)        # input_tracks session var is created
        self.assertEqual(len(sessionVar['input_tracks']), 0)            #input_tracks session var has nothing in it
        self.assertEqual(sessionVar["input_tracks"], [])            #input_tracks session var is empty list

    # test if conver_weight_input function convert correctly
    def test_convert_weight_input_correct(self):
        v1 = 'High'
        v2 = 'Medium'
        v3 = 'Low'
        converted1 = convert_weight_input(v1)
        converted2 = convert_weight_input(v2)
        converted3 = convert_weight_input(v3)
        self.assertEqual (converted1, 1.2)
        self.assertEqual (converted2, 1.0)
        self.assertEqual (converted3, 0.8)

    # testing if updatePreference function is correct?
    def test_update_preference_correct(self):
        update_preference_url = '/update_preference/'
        valid_input_preference = {'energy_weight': 'High', 'tempo_weight' : 'Low'}

        response = self.client.post(update_preference_url, valid_input_preference)

        sessionVar = self.client.session
        self.assertEqual(response.status_code, 302)     #redirected 
        self.assertIn('preferences',sessionVar)        #preferences session var is created
        self.assertEqual(sessionVar['preferences']['energy_weight'], 1.2)        # preferences session var has correct value 1.2 for High value
        self.assertEqual(sessionVar['preferences']['tempo_weight'], 0.8)       # preferences session var has correct value 0.8 for Low value

    # testing if removeTrack function works correctly
    def test_remove_track_correct(self):
        # creating fake sessionVar
        sessionVar = self.client.session
        sessionVar['input_tracks'] = [{'id' : 'abcdefg'}, {'id' : 'hijklmn'},{'id' : 'opqrstu'}]
        sessionVar.save()
        
        sessionVar = self.client.session
        
        # test if removing non existing track does not cause any error and remove anything 
        remove_non_existing_track_url = '/remove_from_inputs/abcdefghijklmnop' 
        
        response = self.client.post(remove_non_existing_track_url)
        sessionVar = self.client.session

        self.assertEqual(response.status_code, 302)     # check if no error
        self.assertEqual(len(sessionVar['input_tracks']), 3)        # check if length is still the same as created above (3)

        remove_track = 'hijklmn'
        remove_track_url = '/remove_from_inputs/' + remove_track
        
        response1 = self.client.post(remove_track_url)
        sessionVar = self.client.session

        self.assertEqual(response1.status_code, 302)        # check if no error
        self.assertEqual(len(sessionVar['input_tracks']), 2)        # check if one element is removed from the list
        self.assertNotIn(remove_track, [track['id'] for track in sessionVar['input_tracks']])      # check if the removed element is not in the list 

    # test if get_input_track_id_list returns a list of input track ids, given the track details list
    def test_get_input_track_id_list_returns_correct(self):
        list_of_dict = [{'id' : 'a', 'name' : 'name1'}, {'id' : 'b', 'name' : 'name2'}, {'id' : 'c', 'name' : 'name3'}]
        get_ids = get_input_track_id_list(list_of_dict)

        self.assertEqual(len(list_of_dict), len(get_ids))       # check if the lenght of input and output are the same
        self.assertEqual(['a','b','c'], get_ids)        # check if the expected ids are in the output

    # test if get_artist_list returns a list of artists of the input track
    def test_get_artist_list_returns_correct(self):
        artists = get_artists_list(self.trackCollab)

        self.assertEqual(len(artists), 2)   # check if the artists list has 2 elements.
        self.assertEqual(['Zendaya', 'Sofia Carson'], artists)      # check if artists in the list are correct.

    # test if the recommend function is working as expected
    def test_recommend_works(self):
        sessionVar = self.client.session

        sessionVar['input_tracks'] = [{'id': self.track1.track_id}, {'id': self.track4.track_id}]
        sessionVar['preferences'] = {'energy_weight' : 1.0, 'tempo_weight': 1.0}
        sessionVar.save()

        recommend_url = '/recommend/'

        response = self.client.get(recommend_url)
        sessionVar = self.client.session
        self.assertEqual(response.status_code, 302)     # url successful
        self.assertIn('recommended_track',sessionVar)       # recommended_track gets created in the function
        self.assertEqual(sessionVar['recommended_track']['trackId'], self.trackCollab.track_id)     #recommended_track has the expected value
