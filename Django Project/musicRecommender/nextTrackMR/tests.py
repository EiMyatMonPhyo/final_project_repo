import html

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.messages import get_messages
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
            energy= 0.4,        #Medium
            tempo = 140.555,        #high
            fixed_track_name = 'Keep It Undercover',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track5 = TrackFactory.create(
            track_id="4qEoqyPbLYnLOii6mKlIjI",
            track_name = "Determinate - From ""Lemonade Mouth""",
            energy= 0.8,        #high
            tempo = 96.555,        #low
            fixed_track_name = "Determinate",
            finalized_vector="[0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]"
        )
        self.track6 = TrackFactory.create(
            track_id="5lz0NiPw32Gq4kMIUJvuw2",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            energy= 0.2,        # low
            tempo= 123.55,      # medium
            fixed_track_name = "Take On the World",
            finalized_vector="[0.6841002328417786, 0.9981296726927211, 0.9354108025670682, 0.0013314044032724744, 0.4549565910412271, 0.0002909456740442656, 1.0051254112272907]"
        )
        self.track7 = TrackFactory.create(
            track_id="1rM0CnyUiiw6A9CHJRXjZA",
            track_name = "Chillin' Like a Villain",
            energy= 0.23,        # low
            tempo= 125.55,      # medium
            fixed_track_name = "Chillin' Like a Villain",
            finalized_vector="[0.756059430092028, 1.0849448653514364, 1.100407373668103, 0.041574344961911015, 0.44000287433286084, 0.0, 1.0003729857720596]"
        )

        # fake data (mostly for random model testing)
        self.track2 = TrackFactory.create(
            track_id='abcdefghijklmnopqrstuv',
            track_name='random song by Zendaya', 
            energy= 0.9,        #high
            tempo = 76.555,        #low
            fixed_track_name = 'random song 1 by Zendaya',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track3 = TrackFactory.create(
            track_id='klmnopqrstuvabcdefghij',
            track_name='random song 2 by Zendaya', 
            energy= 0.6,        #Medium
            tempo = 145.555,        #high
            fixed_track_name = 'random song 2 by Zendaya',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track4 = TrackFactory.create(
            track_id='pqrstuvabcklmnodefghij',
            track_name='random song 1 by Sofia Carson', 
            energy= 0.65,        #Medium
            tempo = 89.555,        #low
            fixed_track_name = 'random song 1 by Sofia Carson',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.trackCollab = TrackFactory.create(
            track_id='uvabcklmnopqrstdefghij',
            track_name='random song 1 by Sofia Carson & Zendaya', 
            energy= 0.1,        #low
            tempo = 120.555,        #medium
            fixed_track_name = 'random song 1 by Sofia Carson & Zendaya',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.trackNoLink = TrackFactory.create(
            track_id='uvabcklefghijmnopqrstd',
            track_name='this track has no link table, so no artist linked to this track', 
            energy = 0.9,   #high
            tempo = 12.09,       # low
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
        
    def tearDown(self):
        Track.objects.all().delete()
        Artist.objects.all().delete()
        TrackArtistLink.objects.all().delete()
        TrackFactory.reset_sequence(0)



    # test if getting track vectors from database works
    def test_get_track_vectors_returns_valid_vectors(self):
        vectors = get_track_vectors_from_database(["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"])
        
        self.assertEqual(len(vectors), 2)
        # self.assertIn(np.array([0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]),vectors)
        
    # test if getting track vectors from database raise error for invalid input
    def test_get_track_vectors_returns_invalid(self):
        with self.assertRaises(ValueError):
            get_track_vectors_from_database(["abcdefg11234567"])

    # test if weighting is applied correctly
    # def test_weight_vector_changes_energy_and_tempo(self):
    #     avg_vector = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

    #     normal = weight_vector(avg_vector.copy(), energy_weight=1.0, tempo_weight=1.0)
    #     high_energy = weight_vector(avg_vector.copy(), energy_weight=2.0, tempo_weight=1.0)
    #     low_tempo = weight_vector(avg_vector.copy(), energy_weight=1.0, tempo_weight=0.7)
        
    #     self.assertNotEqual(normal[1], high_energy[1]) 
    #     self.assertGreater(high_energy[1], normal[1])
    #     self.assertNotEqual(normal[4], low_tempo[4]) 
    #     self.assertLess(low_tempo[4], normal[4])

    # testing if euclidean equation gives correct answer
    def test_Euclidean_equation_is_correct(self):
        result = calculate_Euclidean(np.array([1,2]), np.array([1,1]))
        self.assertEqual(result, np.sqrt(1))

        result = calculate_Euclidean(np.array([1,2,3]), np.array([1,1,1]))
        self.assertEqual(result, np.sqrt(5))

    # test if minimum distance index is returned correctly
    def test_get_track_with_minimum_distance_returns_correct_index(self):
        distances = [0.1, 0.3, 0.0, 0.9]
        min_index = get_track_index_with_minimum_distance(distances)
        
        self.assertEqual(min_index,2)

    # # DELETED FUNCTION#
    # # test if the Euclidean recommender output is Track obj
    # def test_recommenderLogicReturnsTrack(self):
    #     input_tracks = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
    #     input_preferences = {
    #         "energy_weight" : 1.0,
    #         "tempo_weight" : 1.2
    #     }
    #     result = recommend_Euclidean(input_tracks, input_preferences)

    #     self.assertIsInstance(result, Track)

    # test if get_top_tracks returns correct data
    def test_get_top_tracks_return_correct(self):
        comparison_results = [(self.track1, 0.1),(self.track4, 0.4),(self.track7, 0.6),(self.track3, 0.3),
                              (self.track6, 0.5),(self.track2, 0.2),(self.track5, 0.4),(self.trackCollab, 0.7)]
        k = 5
        higher = True # (higher to lower => highest results returned)

        output = get_top_tracks(comparison_results, k, higher)
        output_ids = {t.track_id for t in output}

        expected_output = [self.trackCollab, self.track7, self.track6, self.track5, self.track4]
        expected_ids = {t.track_id for t in expected_output}

        self.assertEqual(len(output), k)     # no: of elements in output is k
        self.assertTrue(expected_ids.issubset(output_ids))        # expected_ids are in output ids
        self.assertIsInstance(output[0], Track)      # of Track instance
        self.assertTrue(type(output), list)         # output is list

    # test if normalize_Euclidean works correctly
    def test_normalize_euclidean_correct(self):
        dist_scores = [0, 1.2, 2.4, 2.5]    # normal input
        #min = 0, max = 2.5, => min-max = [0, 0.48, 0.96, 1] => 1 - [0, 0.48, 0.96, 1] is expected
        expected = [1, 0.52, 0.04, 0]

        normalized_E = normalize_Euclidean(dist_scores)
        self.assertEqual(len(normalized_E), len(dist_scores))       # lengths of input and output are same
        for i, j in zip(normalized_E, expected):        # output is expected
            self.assertAlmostEqual(i, j)

        same_dists = [2,2,2,2]
        expected_same_dists = [1,1,1,1]
        normalized_E_same_dists = normalize_Euclidean(same_dists)
        self.assertEqual(len(normalized_E_same_dists), len(same_dists))       # lengths of input and output are same  
        for i, j in zip(normalized_E_same_dists, expected_same_dists):        # output is expected
            self.assertAlmostEqual(i, j)

        # empty input raise error
        with self.assertRaises(ValueError):
            normalize_Euclidean([]) 

    # test if smaller Euclidean distances are bigger after normalized
    def test_smaller_Euclidean_are_normalized_to_be_bigger_score(self):
        dist_scores = [1, 5, 10]
        normalized_E = normalize_Euclidean(dist_scores)
        self.assertGreater(normalized_E[0], normalized_E[1])
        self.assertGreater(normalized_E[1], normalized_E[2])

    # test if reward_track_by_matching_artists returns correct score as expected
    def test_reward_track_by_matching_artists_return_correct(self):
        frequency = Counter({'a': 3, 'b': 2, 'c': 1}) 

        candidate = ['a', 'c', 'd']     #matching candidate
        # total = 6, matching : a and c => 4, so result is 4/6
        expected = 2/3        #expected result
        reward = reward_track_by_matching_artists(candidate, frequency)
        self.assertAlmostEqual(reward, expected)

        candidate_no_match = ['d','e']
        reward_no_match = reward_track_by_matching_artists(candidate_no_match, frequency)
        self.assertAlmostEqual(0, reward_no_match)

    # tested just in case for edge cases, rare and unlikely to happen
    def test_reward_track_by_matching_artists_handle_edge_case_correct(self):
        frequency = Counter({'a': 3, 'b': 2, 'c': 1}) 
        candidate = ['a', 'c', 'd']

        # in case there is no candidate artist (no artist linked with track)        
        reward_no_candidate_artist = reward_track_by_matching_artists([], frequency)        #no candidate artist
        self.assertEqual(reward_no_candidate_artist, 0)

        # in case there is no input tracks' artists and so no frequency 
        reward_no_freq = reward_track_by_matching_artists(candidate, {})        # no frequency 
        self.assertEqual(reward_no_candidate_artist, 0)
    
    # check if the returned filtered tracks are in corresponding range, and all eligible tracks in range are returnee
    def test_filtering_tracks_by_pref_works_correct(self):
        pref = {
            "energy_input" : "High",
            "tempo_input" : "Low"
        }
        high_E_low_T_tracks = [self.track5, self.track2]

        eligible_tracks = Track.objects.all().exclude(track_id= self.trackNoLink.track_id)

        eligible = filter_tracks_by_pref(pref, eligible_tracks)

        eligible_energy = [i.energy for i in list(eligible)]
        eligible_tempo = [i.tempo for i in list(eligible)]
    
        self.assertEqual(high_E_low_T_tracks, list(eligible))

        # check if the returned filtered track's energy and tempo are in respective range
        for e in eligible_energy:       # high energy (between 0.7 - 1)
            self.assertGreater(e, 0.7)
            self.assertLess(e, 1.0)
        for t in eligible_tempo:        # low tempo (between 0 and 100)
            self.assertGreater(t, 0)
            self.assertLess(t, 100)     



   
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


    ###################Euclidean ###################
    # test if recommend_euclidean_topk returns correct data
    def test_recommend_Euclidean_topk_returns_correct(self):
              
        input_track_ids = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_input" : "High",
            "tempo_input" : "Low"
        }
        k = 2

        recommended = recommend_Euclidean_topk(input_track_ids, input_preferences, k = k)       # k value is given
        recommended_ids = {t.track_id for t in recommended}
        recommended_energy = [t.energy for t in recommended]
        recommended_tempo = [t.tempo for t in recommended]
        self.assertIsInstance(recommended, list)        # the returned data is list
        self.assertEqual (len(recommended), k)  # len of returned list is k 
        self.assertEqual(len(set(recommended_ids)), len(recommended_ids)) # no duplicate
        self.assertTrue(all(isinstance(i, Track) for i in recommended))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.
        for e in recommended_energy:        # checking if filtering with pref setting works??
            self.assertGreater(e, 0.7)
            self.assertLess(e, 1.0)
        for t in recommended_tempo: 
            self.assertGreater(t, 0)
            self.assertLess(e, 100)
        
        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids)

        recommended1 = recommend_Euclidean_topk(input_track_ids, input_preferences)     # no k value given
        recommended_ids1 = {t.track_id for t in recommended1}
        recommended_energy1 = [t.energy for t in recommended]
        recommended_tempo1 = [t.tempo for t in recommended]
        self.assertIsInstance(recommended1, list)
        self.assertEqual(len(recommended1), 1)     
        self.assertEqual(len(set(recommended_ids1)), len(recommended_ids1)) # no duplicate
        self.assertTrue(all(isinstance(i, Track) for i in recommended1))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.
        for e in recommended_energy1:        # checking if filtering with pref setting works??
            self.assertGreater(e, 0.7)
            self.assertLess(e, 1.0)
        for t in recommended_tempo1: 
            self.assertGreater(t, 0)
            self.assertLess(e, 100)
        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids1)

        recommended_no_pref = recommend_Cosine_topk(input_track_ids)
        recommended_ids_no_pref = {t.track_id for t in recommended_no_pref}
        self.assertIsInstance(recommended_no_pref, list)
        self.assertEqual(len(recommended_no_pref), 1)     
        self.assertEqual(len(set(recommended_ids_no_pref)), len(recommended_ids_no_pref)) # no duplicate
        self.assertTrue(all(isinstance(i, Track) for i in recommended_no_pref))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.
        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids_no_pref) 
       

    ###################Cosine ######################
    # test if recommend_cosine_topk returns correct data
    def test_recommend_Cosine_topk_returns_correct(self):
              
        input_track_ids = ["4qEoqyPbLYnLOii6mKlIjI","5lz0NiPw32Gq4kMIUJvuw2"]
        input_preferences = {
            "energy_input" : "Low",
            "tempo_input" : "Medium"
        }
        k = 2

        recommended = recommend_Cosine_topk(input_track_ids, input_preferences, k = k)       # k value is given
        recommended_ids = {t.track_id for t in recommended}
        recommended_energy1 = [t.energy for t in recommended]
        recommended_tempo1 = [t.tempo for t in recommended]
        self.assertIsInstance(recommended, list)        # the returned data is list
        self.assertEqual (len(recommended), k)  # len of returned list is k 
        self.assertEqual(len(set(recommended_ids)), len(recommended_ids)) # no duplicate
        self.assertTrue(all(isinstance(i, Track) for i in recommended))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.
        for e in recommended_energy1:        # checking if filtering with pref setting works??
            self.assertGreater(e, 0)
            self.assertLess(e, 0.3)
        for t in recommended_tempo1: 
            self.assertGreater(t, 100)
            self.assertLess(e, 130)
        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids)

        recommended1 = recommend_Cosine_topk(input_track_ids, input_preferences)     # no k value given
        recommended_ids1 = {t.track_id for t in recommended1}
        recommended_energy1 = [t.energy for t in recommended]
        recommended_tempo1 = [t.tempo for t in recommended]
        self.assertIsInstance(recommended1, list)
        self.assertEqual(len(recommended1), 1)     
        self.assertEqual(len(set(recommended_ids1)), len(recommended_ids1)) # no duplicate
        self.assertTrue(all(isinstance(i, Track) for i in recommended1))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.
        for e in recommended_energy1:        # checking if filtering with pref setting works??
            self.assertGreater(e, 0)
            self.assertLess(e, 0.3)
        for t in recommended_tempo1: 
            self.assertGreater(t, 100)
            self.assertLess(e, 130)
        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids1)

        recommended_no_pref = recommend_Cosine_topk(input_track_ids)
        recommended_ids_no_pref = {t.track_id for t in recommended_no_pref}
        self.assertIsInstance(recommended_no_pref, list)
        self.assertEqual(len(recommended_no_pref), 1)     
        self.assertEqual(len(set(recommended_ids_no_pref)), len(recommended_ids_no_pref)) # no duplicate
        self.assertTrue(all(isinstance(i, Track) for i in recommended_no_pref))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.
        # no input tracks  
        for id in input_track_ids:
            self.assertNotIn(id, recommended_ids_no_pref) 


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

    # test if recommend_random_topk works correctly
    def test_recommend_random_topk(self):
        input_track_ids = [self.track1.track_id, self.track2.track_id, self.track3.track_id, self.track4.track_id, self.track5.track_id]
        
        recommended = recommend_random_topk(input_track_ids)        # k = 1
        self.assertEqual(len(recommended), 1)       # k = 1
        self.assertTrue(all(isinstance(i, Track) for i in recommended))      # all elements in the returned list are Track obj     

        # no duplicate
        self.assertEqual(len(set(recommended)), len(recommended)) # no duplicate

        # k test
        k = 2
        recommended_topk = recommend_random_topk(input_track_ids, k)      
        self.assertEqual(len(recommended_topk), k)       # k = 10 (10 track objects in returned list)

        # no input included in the result 
        for id in input_track_ids:
            self.assertNotIn(id, recommended_topk)
       

# serializer test
class recommendTrackIdSerializerTest(APITestCase):

    def setUp(self):

        # full input is allowed 
        self.input_data1 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy": 'High',
                "tempo": 'Low'
            }
        }

        # full input is allowed 
        self.input_data2 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy": 'Medium',
                "tempo": 'Medium'
            }
        }

        # optional preference input is allowed 
        self.input_data3 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"]
        }

        # only one pref
        self.input_data4 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "tempo": 'Medium'
            }
        }

        # only one pref
        self.input_data5 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy": 'High'
            }
        }

        self.input_data6 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {}
        }
        

        self.good_inputs = [self.input_data1, self.input_data2, self.input_data3, self.input_data4, self.input_data5, self.input_data6]


        # invalid track input is not allowed (id empty str)
        self.invalid_input_data1 = {
            "track_ids": ["", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy": "Medium",
                "tempo": "Low"
            }
        }

        # no track input is not allowed (no tracks input)
        self.invalid_input_data2 = {
            "preferences": {
                "energy": 'Medium',
                "tempo": 'Medium'
            }
        }

        # track input (not a list) is not allowed
        self.invalid_input_data3 = {
            "track_ids": "4qEoqyPbLYnLOii6mKlIjI",
            "preferences": {
                "energy": 'Low',
                "tempo": 'High'
            }
        }

        # pref values of string are not allowed (one pref is wrong input)
        self.invalid_input_data4 = {
            "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
            "preferences": {
                "energy": 'High',
                "tempo": 0.5
            }
        }

        # invalid track input is not allowed  (one pref is wrong input)
        self.invalid_input_data5 = {
            "track_ids": ["abcdefg"],
            "preferences": {
                "energy": 'random text',
                "tempo": 'Medium'
            }
        }

        self.bad_inputs = [self.invalid_input_data1, self.invalid_input_data2, self.invalid_input_data3, self.invalid_input_data4, self.invalid_input_data5]

        self.track = TrackFactory.create( 
            track_id='744ZuzjXQmoJmOdk2I1ym9',
            track_name='"Keep It Undercover - Theme Song From ""K.C. Undercover"""', 
            fixed_track_name = 'Keep It Undercover',
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )


    # valid data testing
    def test_recommenderInputSerializerValidData(self):
        for i in self.good_inputs:
            serializer = RecommenderInputSerializer(data = i)
            self.assertTrue(serializer.is_valid())


    # invalid data testing
    def test_recommenderInputSerializerInvalidData(self):
        for i in self.bad_inputs:
            serializer = RecommenderInputSerializer(data = i)
            self.assertFalse(serializer.is_valid())


    # output serializer testing 
    def test_TrackIdRecommendationSerializer(self):
        output_serializer = TrackIdRecommendationSerializer(self.track)
        self.assertEqual(output_serializer.data['track_id'],self.track.track_id)        # returned track id is correct

# api test
class recommendTrackIDTest(APITestCase):

    def setUp(self):
        self.good_url_euclidean = reverse('recommend_track_api')
        self.good_url_cosine = reverse('recommend_track_cosine_api')
        self.good_url_random_artist = reverse('recommend_track_random_api')
        self.good_url_random = reverse('recommend_track_random1_api')

        # good valid input
        self.good_input1 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
                            "preferences": {
                                "energy": "High",
                                "tempo": "Medium"
                            }}
        
        # no pref input
        self.good_input2 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
                            "preferences": {}}
        
        # one pref input
        self.good_input3 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
                            "preferences": {
                                "energy": "High"
                            }}
        
        # no preferences
        self.good_input4 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"]}
        
        # only one track input
        self.good_input5 =  {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI"]}

        # invalid track id (string)
        self.bad_input1 = {"track_ids" : "a",
                          "preferences": {
                                "energy": "High",
                                "tempo": "Low"
                            }}
        
        # invalid track_ids
        self.bad_input2 = {"track_ids" : ["abcdefg"],
                          "preferences": {
                                "energy": "High",
                                "tempo": "Medium"
                            }}
        
        # no track_ids
        self.bad_input3 = {"preferences": {
                                "energy": "High",
                                "tempo": "High"
                            }}
        
        # no track (empty list)
        self.bad_input4 = {"track_ids" : [],
                          "preferences": {
                                "energy": "Low",
                                "tempo": "High"
                            }}
        
        # wrong pref input
        self.bad_input5 = {"track_ids" : ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
                           "preferences" : {
                               "energy": "High",
                                "tempo": 1.2
                           }}
        
        # value error will raise, because there is no other track in database like this input pref
        self.error_input = {"track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
                            "preferences": {
                                "energy": "Low",
                                "tempo": "High"
                            }}
        
        self.track1 = TrackFactory.create(
            track_id="4qEoqyPbLYnLOii6mKlIjI",
            track_name = "Determinate - From ""Lemonade Mouth""",
            fixed_track_name = "Determinate",
            danceability = 0.562,
            energy = 0.768,     # high 
            valence = 0.218,
            acousticness = 0.00361,
            tempo = 139.968,        # high
            instrumentalness = 0.0,
            loudness = -5.006,
            normalized_vector = "[0.5376427541856083, 0.7679593928937565, 0.22312408520046265, 0.003619762009199307, 0.5703852259290954, 0.0, 0.8683863126794208]",
            finalized_vector="[0.5914070296041691, 1.075143150051259, 0.29006131076060143, 0.004705690611959099, 0.6274237485220049, 0.0, 1.042063575215305]"
        )

        self.track2 = TrackFactory.create(
            track_id="5lz0NiPw32Gq4kMIUJvuw2",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            danceability = 0.638,
            energy = 0.713,     #high
            valence = 0.703,
            acousticness = 0.00103,
            tempo = 115.967,        # medium
            instrumentalness = 0.000241,
            loudness = -6.475,
            normalized_vector = "[0.621909302583435, 0.7129497662090866, 0.7195467712054371, 0.0010241572332865187, 0.41359690094657003, 0.0002424547283702213, 0.8376045093560757]",
            finalized_vector="[0.6841002328417786, 0.9981296726927211, 0.9354108025670682, 0.0013314044032724744, 0.4549565910412271, 0.0002909456740442656, 1.0051254112272907]"
        )

        self.track3 = TrackFactory.create(
            track_id="1rM0CnyUiiw6A9CHJRXjZA",
            track_name = "Take On the World - Theme Song From ""Girl Meets World""",
            fixed_track_name = "Take On the World",
            danceability = 0.638,
            energy = 0.713,     # high
            valence = 0.703,
            acousticness = 0.00103,
            tempo = 115.967,        # medium
            instrumentalness = 0.000241,
            loudness = -6.475,
            normalized_vector = "[0.621909302583435, 0.7129497662090866, 0.7195467712054371, 0.0010241572332865187, 0.41359690094657003, 0.0002424547283702213, 0.8376045093560757]",
            finalized_vector="[0.756059430092028, 1.0849448653514364, 1.100407373668103, 0.041574344961911015, 0.44000287433286084, 0.0, 1.0003729857720596]"
        )

        # good and bad inputs
        self.good_inputs = [self.good_input1, self.good_input2, self.good_input3, self.good_input4, self.good_input5]
        self.bad_inputs = [self.bad_input1, self.bad_input2, self.bad_input3, self.bad_input4, self.bad_input5]
        self.good_urls = [self.good_url_euclidean, self.good_url_cosine, self.good_url_random_artist, self.good_url_random]

    def tearDown(self):
        Track.objects.all().delete()
        Artist.objects.all().delete()
        TrackArtistLink.objects.all().delete()
        TrackFactory.reset_sequence(0)

    # testing if api returns correct with good inputs
    def test_recommendTrackIdModelsReturnsSuccess(self):
        for good_url in self.good_urls:
            for good_input in self.good_inputs:

                response = self.client.post(good_url, 
                                            good_input,
                                            format= 'json')
                self.assertEqual(response.status_code,200) 

            response = self.client.post(good_url + '?k=2',
                                        self.good_input5,
                                        format= 'json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 2)

    # testing if api returns error with bad inputs
    def test_recommendTrackIdModelsReturnsError(self):
        for good_url in self.good_urls:
            for bad_input in self.bad_inputs:

                response = self.client.post(good_url,
                                            bad_input,
                                            format = 'json')
                self.assertEqual(response.status_code, 400)
            
            # test if k=abc is invalid
            response = self.client.post(good_url + '?k=abc',
                                        self.good_input3,
                                        format= 'json')
            self.assertEqual(response.status_code, 400)

            # test if k= less than 0 is invalid
            response = self.client.post(good_url + '?k=0',
                                        self.good_input3,
                                        format= 'json')
            self.assertEqual(response.status_code, 400)
        

        # cases where no eligible tracks are there for recommendation (for Euclidean and Cosine only, cuz other models dont use pref)
        response = self.client.post(self.good_url_euclidean,
                                    self.error_input,
                                    format= 'json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.good_url_cosine,
                                    self.error_input,
                                    format= 'json')
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
            energy = 0.713,     #high
            tempo = 115.967,        # medium
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.track4 = TrackFactory.create(
            track_id='pqrstuvabcklmnodefghij',
            track_name='random song 1 by Sofia Carson', 
            fixed_track_name = 'random song 1 by Sofia Carson',
            energy = 0.5,     #medium
            tempo = 85.967,        # low
            finalized_vector = "[0.7450826033928375, 1.083544620308554, 1.0684725534549997, 0.4721228022873516, 0.41189189895413475, 0.0, 1.0561951260398548]"
        )
        self.trackCollab = TrackFactory.create(
            track_id='uvabcklmnopqrstdefghij',
            track_name='random song 1 by Sofia Carson and Zendaya', 
            fixed_track_name = 'random song 1 by Sofia Carson and Zendaya',
            energy = 0.2,     #low
            tempo = 140.6,        # high
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


    def tearDown(self):
        Track.objects.all().delete()
        Artist.objects.all().delete()
        TrackArtistLink.objects.all().delete()
        TrackFactory.reset_sequence(0)

    # testing if get_input_tracks_in_order works, order correctly
    def test_get_input_tracks_in_order_correct(self):
        input_track_ids = [self.track4.track_id, self.track1.track_id]

        ordered_tracks = get_input_tracks_in_order(input_track_ids)
        self.assertEqual(ordered_tracks, [self.track4, self.track1])        # ordered tracks are in added order
        self.assertEqual(type(ordered_tracks), list)        # return type is list
        self.assertTrue(all(isinstance(i, Track) for i in ordered_tracks))      # all elements in the returned list are Track obj      # check if list's elements are Track objects.

        # for no input track case.
        no_tracks = get_input_tracks_in_order([])
        self.assertEqual(len(no_tracks), 0)
        self.assertEqual(type(no_tracks), list)

    

    # test if getAllTracks work correctly
    def test_getAllTracks_correct(self):
        input_track_ids = [self.track4.track_id]

        all_tracks = getAllTracks(input_track_ids)

        self.assertNotIn(self.track4, all_tracks)       # track in input list is not included
        self.assertEqual(all_tracks, [self.track1, self.trackCollab])
        self.assertEqual(type(all_tracks), list)        # return type is list
        self.assertTrue(all(isinstance(i, Track) for i in all_tracks))      # all elements in the returned list are Track obj     


    # test if update_all_tracks_html returns correct html with correct all_tracks
    def test_update_all_tracks_html(self):
        class FakeRequest:
            session = {"input_tracks": [self.track1.track_id]}
        request = FakeRequest()

        # no serach keyword test
        all_tracks_html = update_all_tracks_html(request)

        self.assertIsInstance(all_tracks_html, str)     # string returned
        self.assertIn(self.trackCollab.track_id, all_tracks_html)       # trackCollab is not in input , so should be in all tracks
        self.assertIn(self.track4.track_id, all_tracks_html)             # track4 is not in input , track4 is not by Zendaya(keyword), so should not be in all tracks
        self.assertNotIn(self.track1.track_id, all_tracks_html)          # track1 is in input , so should not be in all tracks

        # with search keyword test
        all_tracks_html_with_keyword = update_all_tracks_html(request, 'Zendaya')
        
        self.assertIsInstance(all_tracks_html_with_keyword, str)     # string returned
        self.assertIn(self.trackCollab.track_id, all_tracks_html_with_keyword)       # trackCollab is not in input , so should be in all tracks
        self.assertNotIn(self.track4.track_id, all_tracks_html_with_keyword)             # track4 is not in input , so should be in all tracks
        self.assertNotIn(self.track1.track_id, all_tracks_html_with_keyword)          # track1 is in input , so should not be in all tracks
    
    # test if update_input_tracks_html returns correct html with correct input tracks
    def test_update_input_tracks_html(self):
        class FakeRequest:
            session = {"input_tracks": [self.track1.track_id]}      #track 1 is in input tracks
        request = FakeRequest()

        input_tracks_html = update_input_tracks_html(request)

        self.assertIsInstance(input_tracks_html, str)       # return str
        self.assertNotIn(self.track4.track_id, input_tracks_html)       # track4 should not be in input_track
        self.assertNotIn(self.trackCollab.track_id, input_tracks_html)      # trackCollab should not be in input_track
        self.assertIn (self.track1.track_id, input_tracks_html)     # track1 should be in input track.
    
    # index function testing
    # test if index function loads okay, use the right template
    def test_index_loads_correctly(self):
        response = self.client.get(reverse('index'))
        
        self.assertEqual(response.status_code, 200)     # check if the url is successful
        self.assertTemplateUsed(response, 'nextTrackMR/home.html')     # check if the correct template is rendered

    # test if session variables are true and passed to the html file correctly from the index function
    def test_session_vars_are_correct(self):
        sessionVar = self.client.session
        sessionVar['input_tracks'] = [self.track1.track_id]
        sessionVar['recommended_track'] = {'trackId' : 'abcd', 'trackName' : 'Photograph', 'arists' : ['Ed Shreen']}
        sessionVar['preferences'] = {'energy_input': "Medium", 'tempo_input': "Medium"}

        sessionVar.save()

        response = self.client.get(reverse('index'))

        # test if the session variables and variables passed to HTML are the same (checking for all three sessioin variables)
        expected_all_tracks = response.context['all_tracks']
        self.assertEqual(expected_all_tracks, [self.track4, self.trackCollab])
        self.assertNotIn(self.track1.track_id, expected_all_tracks)
        self.assertEqual(list(response.context['input_tracks']), [self.track1])        
        self.assertEqual(response.context['recommended_track'], sessionVar['recommended_track'])
        self.assertEqual(response.context['preferences'], sessionVar['preferences'])

    # test if searchTracks work correct.
    def test_search_tracks_correct(self):
        session = self.client.session
        session['input_tracks'] = [self.track1.track_id]
        session.save()

        # track title search
        response = self.client.get(reverse('search_tracks'), {'q': 'random'})
         
        self.assertEqual(response.status_code, 200)         # successful search 
        self.assertContains(response, 'random')               # correct search result (track title name)
        self.assertNotContains(response, self.track1.track_name)        # already in input tracks should not be in search results  

        # artist keyword search
        response_artist = self.client.get(reverse('search_tracks'), {'q':'Zendaya'})
        self.assertEqual(response.status_code, 200)         # successful search 
        self.assertContains(response_artist, 'Zendaya')

        # nothing type and enter clicked case.
        response_blank = self.client.get(reverse('search_tracks'), {'q':''})
        self.assertEqual(response.status_code, 200)         # successful search 
        self.assertContains(response_blank, self.track4.track_name)
        self.assertContains(response_blank, html.escape(self.trackCollab.track_name))       # cuz of &
        self.assertNotContains(response, self.track1.track_name)        # already in input tracks should not be in search results  


    # addTrack funtion testing
    # testing if the add_to_inputs url does correctly, session variable is created and stores a correct input
    def test_add_track_correct(self):
        add_track_url = '/add_to_inputs/'
        valid_input_id = self.track1.track_id
        add_track_url_input_id = add_track_url + valid_input_id +'/'
        response = self.client.post(add_track_url_input_id)

        sessionVar = self.client.session
        self.assertEqual(response.status_code, 200)     # request successful
        self.assertIn('input_tracks',sessionVar)        #input_tracks session var is created
        self.assertEqual(len(sessionVar['input_tracks']), 1)        #input_tracks session var has one element in it
        self.assertEqual(sessionVar["input_tracks"][0], valid_input_id)       # the element in the input_tracks session var is track details related to the input id

    # test if adding non exisitng or already-in-input-lists track does not work.
    def test_adding_invalid_track_does_not_work(self):
        add_track_url = '/add_to_inputs/'
        sessionVar = self.client.session
        sessionVar['input_tracks'] = [self.track1.track_id, self.track4.track_id]
        sessionVar.save()
        
        self.assertEqual(len(sessionVar['input_tracks']), 2)  

        # adding tracks 
        invalid_track1 = self.track1.track_id       #exists in database, but already in input tracks list
        invalid_track2 = 'abcdefg'      # non-existing track in database
        
        # adding already-in-input-lists track -> so, not added
        response = self.client.post(add_track_url + invalid_track1 + '/')
        self.assertEqual(response.status_code, 200)     # request successful
        self.assertEqual(len(sessionVar['input_tracks']), 2)    # same length as defined earlier above
        self.assertEqual(sessionVar['input_tracks'].count(invalid_track1), 1)          # only one self.track1, the duplicate self.track1 track is not added      

        # adding non-existing track -> so, not added
        response = self.client.post(add_track_url + invalid_track2 + '/')
        self.assertEqual(response.status_code, 200)     # request successful
        self.assertEqual(len(sessionVar['input_tracks']), 2)    # same length as defined earlier above
        self.assertNotIn(invalid_track2, sessionVar['input_tracks'])    # invalid track 2 (non-existing track) is not added.

    # testing if updatePreference function is correct?
    def test_update_preference_correct(self):
        update_preference_url = '/update_preference/'
        valid_input_preference = {'energy_pref': 'High', 'tempo_pref' : 'Low'}

        response = self.client.post(update_preference_url, valid_input_preference)

        sessionVar = self.client.session
        self.assertEqual(response.status_code, 200)     #success json response
        self.assertIn('preferences',sessionVar)        #preferences session var is created
        self.assertEqual(sessionVar['preferences']['energy_input'], 'High')        # preferences session var has correct value 1.2 for High value
        self.assertEqual(sessionVar['preferences']['tempo_input'], 'Low')       # preferences session var has correct value 0.8 for Low value

    # testing if removeTrack function works correctly
    def test_remove_track_correct(self):
        # creating fake sessionVar
        sessionVar = self.client.session
        sessionVar['input_tracks'] = ['abcdefg', 'hijklmn', 'opqrstu']
        sessionVar.save()
        
        sessionVar = self.client.session
        
        # test if removing non existing track does not cause any error and remove anything 
        non_existing_track = 'abcdefghijklmnop'
        remove_non_existing_track_url = '/remove_from_inputs/' + non_existing_track + '/'
        
        response = self.client.post(remove_non_existing_track_url)
        sessionVar = self.client.session

        self.assertEqual(response.status_code, 200)     # request successful
        self.assertEqual(len(sessionVar['input_tracks']), 3)        # check if length is still the same as created above (3)

        # remove the existing track
        remove_track = 'hijklmn'
        remove_track_url = '/remove_from_inputs/' + remove_track +'/'
        
        response1 = self.client.post(remove_track_url)
        sessionVar = self.client.session

        self.assertEqual(response1.status_code, 200)       # request successful
        self.assertEqual(len(sessionVar['input_tracks']), 2)        # check if one element is removed from the list
        self.assertNotIn(remove_track, [track for track in sessionVar['input_tracks']])      # check if the removed element is not in the list 

    # test if get_artist_list returns a list of artists of the input track
    def test_get_artist_list_returns_correct(self):
        artists = get_artists_list(self.trackCollab)

        self.assertEqual(type(artists), list)       # return type is list
        self.assertEqual(len(artists), 2)   # check if the artists list has 2 elements.
        self.assertEqual(['Zendaya', 'Sofia Carson'], artists)      # check if artists in the list are correct.
        
    # test if the recommend function is working as expected
    def test_recommend_works(self):
        sessionVar = self.client.session

        sessionVar['input_tracks'] = [self.track1.track_id, self.track4.track_id]
        sessionVar['preferences'] = {'energy_input' : 'Low', 'tempo_input': 'High'}
        sessionVar.save()

        recommend_url = '/recommend/'

        response = self.client.get(recommend_url)
        sessionVar = self.client.session
        self.assertEqual(response.status_code, 200)     # request successful
        self.assertIn('recommended_track',sessionVar)       # recommended_track gets created in the function
        self.assertEqual(sessionVar['recommended_track']['trackId'], self.trackCollab.track_id)     #recommended_track has the expected value

    # test if no recommendation leads to msg?
    def test_recommend_raise_errors_if_no_recommendation(self):
        sessionVar = self.client.session

        sessionVar['input_tracks'] = [self.track1.track_id, self.track4.track_id]
        sessionVar['preferences'] = {'energy_input' : 'Medium', 'tempo_input': 'Medium'}        # there is no track with pref in this test case, so, will lead to err and output no recommendation
        sessionVar.save()

        recommend_url = '/recommend/'

        response = self.client.get(recommend_url, follow=True)      # follow true is added for browser acting as client

        data = response.json()        
        errMsg_from_logic = "No tracks match the given preferences"
        sessionVar = self.client.session
        self.assertEqual(response.status_code, 400)     # browser receieves bad request
        self.assertNotIn('recommended_track',sessionVar)       # recommended_track does not get created in the function
        self.assertEqual(data["error"], errMsg_from_logic)        # no recommendation leads to err msg

