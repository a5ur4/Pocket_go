from fastapi import status
from unittest.mock import patch

# Need to create a test archive for each group of endpoints in the API

class TestAPIEndpoints:
    """Test all API endpoints with mocked services"""

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Welcome to the Pocket GO API!"}

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    @patch('services.users_service.getAllUsers')
    def test_get_users(self, mock_get_all_users, client):
        """Test get all users endpoint"""
        mock_get_all_users.return_value = []
        response = client.get("/users/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @patch('services.users_service.getUserById')
    def test_get_user_by_id_not_found(self, mock_get_user, client):
        """Test get user by ID when user doesn't exist"""
        mock_get_user.return_value = None
        response = client.get("/users/test-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('services.hotels_service.getAllHotels')
    def test_get_hotels(self, mock_get_all_hotels, client):
        """Test get all hotels endpoint"""
        mock_get_all_hotels.return_value = []
        response = client.get("/hotels/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @patch('services.hotels_service.getHotelById')
    def test_get_hotel_by_id_not_found(self, mock_get_hotel, client):
        """Test get hotel by ID when hotel doesn't exist"""
        mock_get_hotel.return_value = None
        response = client.get("/hotels/test-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('services.hotels_service.getClosestHotels')
    def test_get_closest_hotels(self, mock_get_closest_hotels, client):
        """Test get closest hotels endpoint"""
        mock_get_closest_hotels.return_value = []
        response = client.get("/hotels/nearby/?latitude=0&longitude=0")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @patch('services.cities_service.getAllCities')
    def test_get_cities(self, mock_get_all_cities, client):
        """Test get all cities endpoint"""
        mock_get_all_cities.return_value = []
        response = client.get("/cities/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @patch('services.evaluations_service.getAllEvaluations')
    def test_get_evaluations(self, mock_get_all_evaluations, client):
        """Test get all evaluations endpoint"""
        mock_get_all_evaluations.return_value = []
        response = client.get("/evaluations/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @patch('services.logs_service.getAllLogs')
    def test_get_logs(self, mock_get_all_logs, client):
        """Test get all logs endpoint"""
        mock_get_all_logs.return_value = []
        response = client.get("/logs/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []