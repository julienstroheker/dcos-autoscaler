from unittest.mock import Mock, patch

from nose.tools import assert_is_instance, assert_is_not_none, assert_true, assert_equals

import requests
import json

class TestCluster():

    @patch('autoscaler.Cluster')
    def test_get_health_not_null(self, MockCluster):
        # Mock
        cluster = MockCluster()
        payload = {}
        with open('./test/mockupDown.json') as json_data:
            payload = json.load(json_data)
        response = cluster.get_health()
        # Act
        cluster.get_health.return_value = payload
        # Assert
        assert_is_not_none(response)

    @patch('autoscaler.Cluster')
    def test_get_health_is_dict(self, MockCluster):
        # Mock
        cluster = MockCluster()
        payload = {}
        with open('./test/mockupDown.json') as json_data:
            payload = json.load(json_data)
        cluster.get_health.return_value = payload
        # Act
        response = cluster.get_health()
        # Assert
        assert_is_instance(response, dict)

    @patch('autoscaler.Cluster')
    def test_filter_get_health_to_get_only_stateless_nodes(self, MockCluster):
        # Mock
        cluster = MockCluster()
        payload = {}
        metrics = {"totalCPU": 0, "totalMEM": 0,
                   "usedCPU": 0, "usedMEM": 0,
                   "ratioCPU": 0, "ratioMEM": 0,
                   "nbNodes": 0}
        with open('./test/mockupDown.json') as json_data:
            payload = json.load(json_data)
        cluster.get_health.return_value = payload
        # Act
        response = cluster.filter_stateless(metrics, cluster.get_health())
        # Assert
        assert_equals(len(response['nbNodes']), 4)
