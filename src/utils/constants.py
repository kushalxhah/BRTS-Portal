"""
Constants for BRTS Portal - Fallback to static data when database is not available
"""

# Static data (used when database is not available)
STATIONS = {
    1: "RTO Circle", 2: "Central Bus Stand", 3: "City Gold", 4: "Nehrunagar",
    5: "Iskon", 6: "Satellite", 7: "Maninagar", 8: "Vastral",
    9: "Jivraj Park", 10: "Memnagar", 11: "Ranip", 12: "Gota",
    13: "Vaishnodevi", 14: "Sola", 15: "Ghuma Gam", 16: "Bhadaj",
    17: "Thaltej", 18: "CTM", 19: "Odhav", 20: "Hansol",
    21: "Tragad", 22: "Airport", 23: "Naroda Gam", 24: "Saijpur Bogha",
    25: "Narol"
}

STATION_COORDS = {
    1: (23.0225, 72.5714), 2: (23.0352, 72.5661), 3: (23.0395, 72.5758),
    4: (23.0458, 72.5892), 5: (23.0225, 72.5114), 6: (23.0265, 72.5060),
    7: (23.0103, 72.5992), 8: (23.0458, 72.6525), 9: (23.0103, 72.6158),
    10: (23.0525, 72.5392), 11: (23.0703, 72.5514), 12: (23.1125, 72.5758),
    13: (23.0847, 72.5647), 14: (23.0925, 72.5525), 15: (23.1103, 72.5192),
    16: (23.0758, 72.4892), 17: (23.0547, 72.5092), 18: (23.0225, 72.6058),
    19: (23.0558, 72.6625), 20: (23.0792, 72.6292), 21: (23.1025, 72.6158),
    22: (23.0725, 72.6358), 23: (23.0892, 72.6625), 24: (23.1225, 72.6858),
    25: (22.9758, 72.6525)
}

ROUTES = {
    1: {"route_name": "RTO to Iskon", "bus_name": "Bus 101", "stations": [1, 2, 3, 4, 5], 
        "distances": {(1, 2): 2, (2, 3): 3, (3, 4): 2, (4, 5): 4}, "color": "#28a745"},
    2: {"route_name": "Central to Vastral", "bus_name": "Bus 202", "stations": [2, 7, 8], 
        "distances": {(2, 7): 5, (7, 8): 4}, "color": "#dc3545"},
    3: {"route_name": "Iskcon to Memnagar", "bus_name": "Bus 303", "stations": [5, 6, 9, 10], 
        "distances": {(5, 6): 3, (6, 9): 4, (9, 10): 3}, "color": "#007bff"},
    4: {"route_name": "Maninagar to Ghuma Gam", "bus_name": "Bus 404", "stations": [11, 12, 13, 14, 15], 
        "distances": {(11, 12): 3, (12, 13): 4, (13, 14): 2, (14, 15): 5}, "color": "#fd7e14"},
    5: {"route_name": "Bhadaj to Odhav", "bus_name": "Bus 505", "stations": [16, 17, 2, 18, 19], 
        "distances": {(16, 17): 4, (17, 2): 3, (2, 18): 5, (18, 19): 2}, "color": "#6f42c1"},
    6: {"route_name": "RTO Circle to Airport", "bus_name": "Bus 606", "stations": [1, 20, 21, 22], 
        "distances": {(1, 20): 6, (20, 21): 4, (21, 22): 3}, "color": "#ffc107"},
    7: {"route_name": "Naroda Gam to Narol", "bus_name": "Bus 707", "stations": [23, 24, 25, 11], 
        "distances": {(23, 24): 3, (24, 25): 5, (25, 11): 4}, "color": "#6c757d"}
}

# Try to load from database, fallback to static data
try:
    import mysql.connector
    from config.settings import DB_CONFIG
    
    def load_from_database():
        """Try to load data from MySQL database"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Load stations
            cursor.execute("SELECT id, name FROM stations ORDER BY id")
            stations_data = cursor.fetchall()
            if stations_data:
                global STATIONS
                STATIONS = {station['id']: station['name'] for station in stations_data}
            
            # Load station coordinates
            cursor.execute("SELECT id, latitude, longitude FROM stations ORDER BY id")
            coords_data = cursor.fetchall()
            if coords_data:
                global STATION_COORDS
                STATION_COORDS = {station['id']: (float(station['latitude']), float(station['longitude'])) for station in coords_data}
            
            print("✅ Data loaded from MySQL database")
            
        except Exception as e:
            print(f"⚠️  Using fallback data (Database not available: {e})")
        finally:
            try:
                if connection and connection.is_connected():
                    cursor.close()
                    connection.close()
            except:
                pass
    
    # Try to load from database on import
    load_from_database()
    
except ImportError:
    print("⚠️  MySQL connector not available, using static data")
except Exception as e:
    print(f"⚠️  Database connection failed, using static data: {e}")