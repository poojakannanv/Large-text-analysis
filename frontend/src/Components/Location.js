import React, { useEffect, useState } from "react";
import axios from "axios";
import { useLocation } from "react-router-dom";
import { Spinner } from "react-bootstrap";

const Location = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true); // State for loading spinner
  const location = useLocation();
  const { selectedCards } = location.state;

  useEffect(() => {
    // Function to load Google Maps API script
    const loadMapScript = () => {
      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyDxfIQxxkklHytjLs9-hNyv0I4yNPvB_rk&callback=initMap`;
      script.async = true;
      document.body.appendChild(script);
      script.onload = () => {
        fetchLocations();
      };
    };

    // Axios call to retrieve latitudes and longitudes
    const fetchLocations = async () => {
      try {
        const response = await axios.post("http://localhost:5000/location", {
          candidates: selectedCards,
        });
        setLocations(response.data);
        setLoading(false); // Set loading to false when data is fetched
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false); // Set loading to false even in case of error
      }
    };

    // Load the map script
    loadMapScript();
  }, [selectedCards]);

  // Render the Google Map with location pins
  const renderMap = () => {
    // Initialize the map
    const mapOptions = {
      zoom: 2.3,
      center: { lat: 0, lng: 0 }, // Center of the map
    };

    const map = new window.google.maps.Map(
      document.getElementById("map"),
      mapOptions
    );

    // Add markers for each location
    locations.forEach((location) => {
      // Check if lat_long is an array or a string indicating error
      if (Array.isArray(location.lat_long)) {
        const marker = new window.google.maps.Marker({
          position: { lat: location.lat_long[0], lng: location.lat_long[1] },
          map: map,
          title: location.title,
        });
      } else {
        console.error(
          `Geocoding API error for location "${location.title}": ${location.lat_long}`
        );
      }
    });
  };

  useEffect(() => {
    if (locations.length > 0) {
      renderMap();
    }
  }, [locations]);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
      }}
    >
      {loading ? ( // Conditional rendering of spinner
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="sr-only"></span>
          </Spinner>
        </div>
      ) : (
        <div id="map" style={{ height: "600px", width: "100%" }}></div>
      )}
    </div>
  );
};

export default Location;
