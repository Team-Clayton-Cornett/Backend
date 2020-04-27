from django.test import TestCase
from route_visualization.get_routes import *
from unittest.mock import MagicMock

import datetime as datetime
import unittest.mock as mock
import builtins

class GetRoutesTestCase(TestCase):
    def test_style_function_good_color(self):
        color = style_function('#000000')
        
        assert color is not None

    def test_style_function_bad_color(self):
        color = style_function(None)

        assert color is not None

    def test_read_coords_from_3_group_json_good_params(self):
        res = read_coords_from_3_group_json()
        
        assert len(res) is 3
        assert res is not None
    
    def test_read_coords_from_3_group_json_bad_params(self):
        res = read_coords_from_3_group_json(filename='bad/path')
        
        assert res is None

    def test_load_markers_bad_params(self):
        m = folium.Map(location=(12, 12), zoom_start=14)
        res = load_markers(m, filename='bad/file')

        assert res is not None
        self.assertEqual(res.location, [12.0,12.0])
        self.assertEqual(res.options['zoom'], 14.0)
        self.assertEqual(len(res._children), 1) 
    
    def test_load_markers_good_params(self):
        m = folium.Map(location=(12, 12), zoom_start=14)
        res = load_markers(m)

        assert res is not None
        self.assertEqual(res.location, [12.0,12.0])
        self.assertEqual(res.options['zoom'], 14.0)
        self.assertEqual(len(res._children), 78)

    @mock.patch('route_visualization.get_routes.openrouteservice.Client.distance_matrix')
    def test_load_markers_bad_client_call(self, mock_client):
        mock_client.return_value = None  

        groupNum = 0
        clnt = openrouteservice.Client(key=123)
        coords = [(12,12)]

        res = get_matrices(groupNum, clnt, coords)

        assert res is None
    
    @mock.patch('route_visualization.get_routes.openrouteservice.Client.distance_matrix')
    def test_load_markers_good_client_call(self, mock_client):
        mock_client.return_value = True  

        groupNum = 0
        clnt = openrouteservice.Client(key=123)
        coords = [(12,12)]

        res = get_matrices(groupNum, clnt, coords)

        assert res is not None

    @mock.patch('route_visualization.get_routes.garage_matrix_g1',  {'durations': [[10 for i in range(5)] for j in range(5)] })
    def test_get_distance_gn_good_params(self):
        res = get_distance_g1(2, 2)

        assert res is not None
        self.assertEqual(10, res)

    @mock.patch('route_visualization.get_routes.garage_matrix_g1',  None)
    def test_get_distance_gn_bad_matrix(self):
        res = get_distance_g1(2, 2)

        assert res is not None
        self.assertEqual(0, res)

    @mock.patch('route_visualization.get_routes.garage_matrix_g1',  {'durations': [[10 for i in range(5)] for j in range(5)] })
    def test_get_distance_gn_bad_params(self):
        res = get_distance_g1(-1, -1)

        assert res is not None
        self.assertEqual(0, res)

    
    def test_save_routes_bad_params(self):
        res = save_routes(-1, None)

        assert res is False
    
    # this is a bad test...
    # def test_save_routes_good_params(self):
    #     optimal_coords = [(0,0), (1,1)]
    #     res = save_routes(1, optimal_coords, filepath='test_save_route_')

    #     os.remove('test_save_route_1.json')

    #     assert res is True

    def test_save_routes_bad_file_write(self):
        with mock.patch('route_visualization.get_routes.open', mock.mock_open()) as mocked_file:
            mocked_file.side_effect = Exception("test exception")

            optimal_coords = [(0,0), (1,1)]
            res = save_routes(1, optimal_coords, filepath='test_save_route_')

            assert res is False

    @mock.patch('route_visualization.get_routes.openrouteservice.Client.directions')
    @mock.patch('route_visualization.get_routes.folium.features.GeoJson')
    def test_get_path_mapped_bad_file_write(self, mock_client, mock_folium):
        mock_client.return_value = True
        mock_folium.return_value = True
        with mock.patch('route_visualization.get_routes.open', mock.mock_open()) as mocked_file:
            m = folium.Map(location=(12, 12), zoom_start=14)
            optimal_coords = [(0,0), (1,1)]
            clnt = openrouteservice.Client(key=123)

            mocked_file.side_effect = Exception("test exception")

            res = get_path_mapped(optimal_coords, m, clnt, 1)

            assert res is False
    
    def test_get_path_mapped_bad_params(self):
        with mock.patch('route_visualization.get_routes.open', mock.mock_open()) as mocked_file:
            m = None
            optimal_coords = None
            clnt = None

            res = get_path_mapped(optimal_coords, m, clnt, -1)

            assert res is False
    
    @mock.patch('route_visualization.get_routes.openrouteservice.Client.directions')
    @mock.patch('route_visualization.get_routes.folium.features.GeoJson')
    @mock.patch('route_visualization.get_routes.folium.features.GeoJson.add_to')
    def test_get_path_mapped_good_params(self, mock_client, mock_folium, mock_add):
        mock_client.return_value = True
        mock_folium.return_value = folium.features.GeoJson()
        mock_add.return_value = True
        with mock.patch('route_visualization.get_routes.open', mock.mock_open()) as mocked_file:
            m = folium.Map(location=(12, 12), zoom_start=14)
            optimal_coords = [(0,0), (1,1)]
            clnt = openrouteservice.Client(key=123)

            res = get_path_mapped(optimal_coords, m, clnt, 1)

            assert res is True

    def test_get_path_bad_params(self):
        garage_matrix = None
        coords = None
        matrixNum = -1

        res = get_path(garage_matrix, coords, matrixNum)

        assert res is False

    def test_get_path_good_params(self):
        garage_matrix = {'durations': [[10 for i in range(3)] for j in range(3)] }
        coords = [(0,0), (1,1), (2,2)]
        matrixNum = 1

        res = get_path(garage_matrix, coords, matrixNum)

        assert res is not None
        self.assertEqual(res, [(2,2), (1,1), (0,0)])





    