"""
Helper functions for BRTS Portal
"""
import numpy as np
from .constants import STATIONS, STATION_COORDS, ROUTES


def calculate_distance(coord1, coord2):
    """Calculate distance between two coordinates using Haversine formula (in km)"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    distance = R * c
    return distance


def find_nearby_stations(station_id, max_distance_km=5.0):
    """Find stations within max_distance_km from the given station"""
    if station_id not in STATION_COORDS:
        return []
    
    station_coord = STATION_COORDS[station_id]
    nearby = []
    
    for sid, coord in STATION_COORDS.items():
        if sid != station_id:
            distance = calculate_distance(station_coord, coord)
            if distance <= max_distance_km:
                nearby.append({
                    'station_id': sid,
                    'station_name': STATIONS[sid],
                    'distance_km': round(distance, 2)
                })
    
    # Sort by distance
    nearby.sort(key=lambda x: x['distance_km'])
    return nearby


def find_routes(start_id, end_id):
    """Find direct routes between two stations"""
    possible = []
    for rid, info in ROUTES.items():
        arr = info["stations"]
        if start_id in arr and end_id in arr and arr.index(start_id) < arr.index(end_id):
            possible.append(rid)
    return possible


def find_routes_with_transfer(start_id, end_id):
    """Find routes that require one transfer (bus change)"""
    transfer_routes = []
    
    # Get all stations where start_id has routes
    for route1_id, route1_info in ROUTES.items():
        if start_id not in route1_info["stations"]:
            continue
        
        start_idx = route1_info["stations"].index(start_id)
        
        # Check all intermediate stations in this route after start
        for transfer_idx in range(start_idx + 1, len(route1_info["stations"])):
            transfer_station = route1_info["stations"][transfer_idx]
            
            # Now check if there's a route from transfer_station to end_id
            for route2_id, route2_info in ROUTES.items():
                if route1_id == route2_id:  # Skip same route
                    continue
                
                if transfer_station in route2_info["stations"] and end_id in route2_info["stations"]:
                    transfer_idx_in_route2 = route2_info["stations"].index(transfer_station)
                    end_idx_in_route2 = route2_info["stations"].index(end_id)
                    
                    if transfer_idx_in_route2 < end_idx_in_route2:
                        # Calculate distances for both legs
                        leg1_stations = route1_info["stations"][start_idx:transfer_idx+1]
                        leg1_distance = sum(route1_info["distances"].get((leg1_stations[i], leg1_stations[i+1]), 0) 
                                          for i in range(len(leg1_stations)-1))
                        
                        leg2_stations = route2_info["stations"][transfer_idx_in_route2:end_idx_in_route2+1]
                        leg2_distance = sum(route2_info["distances"].get((leg2_stations[i], leg2_stations[i+1]), 0) 
                                          for i in range(len(leg2_stations)-1))
                        
                        transfer_routes.append({
                            'route1_id': route1_id,
                            'route1_name': route1_info['route_name'],
                            'bus1_name': route1_info['bus_name'],
                            'leg1_stations': leg1_stations,
                            'leg1_distance': leg1_distance,
                            'transfer_station': transfer_station,
                            'route2_id': route2_id,
                            'route2_name': route2_info['route_name'],
                            'bus2_name': route2_info['bus_name'],
                            'leg2_stations': leg2_stations,
                            'leg2_distance': leg2_distance,
                            'total_distance': leg1_distance + leg2_distance
                        })
    
    # Sort by total distance (shortest first)
    transfer_routes.sort(key=lambda x: x['total_distance'])
    return transfer_routes


def find_routes_from_nearby(station_id, destination_id, max_distance_km=5.0):
    """Find routes from nearby stations to destination"""
    nearby_stations = find_nearby_stations(station_id, max_distance_km)
    alternative_routes = []
    
    for nearby in nearby_stations:
        nearby_sid = nearby['station_id']
        routes = find_routes(nearby_sid, destination_id)
        
        if routes:
            for route_id in routes:
                route_info = ROUTES[route_id]
                alternative_routes.append({
                    'nearby_station': nearby,
                    'route_id': route_id,
                    'route_name': route_info['route_name'],
                    'bus_name': route_info['bus_name']
                })
    
    return alternative_routes


def calculate_fare(route_id, start_id, end_id, qty):
    """Calculate fare for a journey"""
    from config.settings import FARE_PER_KM
    
    route = ROUTES[route_id]
    stations = route["stations"]
    distances = route["distances"]
    
    start_idx = stations.index(start_id)
    end_idx = stations.index(end_id)
    
    total_km = sum(distances.get((stations[i], stations[i+1]), 0) 
                   for i in range(start_idx, end_idx))
    
    fare_per_ticket = total_km * FARE_PER_KM
    total_fare = fare_per_ticket * qty
    
    return total_km, fare_per_ticket, total_fare