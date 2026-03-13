import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import requests
from datetime import datetime, timedelta
import math
import threading
from typing import Optional
import json
from tkinter import messagebox

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WeatherAPI:
    """
    Handle weather data fetching using WeatherAPI.com
    Provides real-time autocomplete search and weather data
    """
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1"
        # Flag to use demo data if API key is "demo"
        self.use_demo = (api_key == "demo")

    def search_locations(self, query: str) -> list:
        """
        Search for locations using WeatherAPI.com search endpoint.
        Returns list of matching locations with proper formatting.
        Requires minimum 2 characters for search.
        Falls back to demo search if API key is invalid.
        """
        # Require at least 2 characters for search
        if not query or len(query.strip()) < 2:
            return []
        
        query_lower = query.lower().strip()
        
        # If using demo mode, use fallback search from common cities
        if self.use_demo:
            return self._demo_search_locations(query_lower)
        
        try:
            response = requests.get(
                f"{self.base_url}/search.json",
                params={"key": self.api_key, "q": query},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                locations = []
                
                # Parse API response and format locations
                for location in data:
                    formatted_location = {
                        "id": location.get("id"),
                        "name": location.get("name", "Unknown"),
                        "region": location.get("region", ""),
                        "country": location.get("country", "Unknown"),
                        "lat": location.get("lat"),
                        "lon": location.get("lon"),
                        "url": location.get("url", "")
                    }
                    locations.append(formatted_location)
                
                return locations
            else:
                # If API fails, fall back to demo search
                print(f"API Error {response.status_code}: Using demo search")
                return self._demo_search_locations(query_lower)
        except Exception as e:
            print(f"Search API error: {e}. Using demo search")
            return self._demo_search_locations(query_lower)
    
    def _demo_search_locations(self, query: str) -> list:
        """
        Fallback search with demo cities database.
        Provides realistic location data for common cities.
        """
        # Comprehensive demo cities database with real regions and countries
        demo_cities = [
            {"name": "Mumbai", "region": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777, "url": "mumbai-maharashtra-india"},
            {"name": "Delhi", "region": "Delhi", "country": "India", "lat": 28.7041, "lon": 77.1025, "url": "delhi-delhi-india"},
            {"name": "Bangalore", "region": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946, "url": "bangalore-karnataka-india"},
            {"name": "Chennai", "region": "Tamil Nadu", "country": "India", "lat": 13.0827, "lon": 80.2707, "url": "chennai-tamil-nadu-india"},
            {"name": "London", "region": "England", "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278, "url": "london-england-united-kingdom"},
            {"name": "New York", "region": "New York", "country": "United States", "lat": 40.7128, "lon": -74.0060, "url": "new-york-new-york-united-states"},
            {"name": "Los Angeles", "region": "California", "country": "United States", "lat": 34.0522, "lon": -118.2437, "url": "los-angeles-california-united-states"},
            {"name": "Tokyo", "region": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "url": "tokyo-tokyo-japan"},
            {"name": "Sydney", "region": "New South Wales", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "url": "sydney-new-south-wales-australia"},
            {"name": "Paris", "region": "Île-de-France", "country": "France", "lat": 48.8566, "lon": 2.3522, "url": "paris-ile-de-france-france"},
            {"name": "Amsterdam", "region": "North Holland", "country": "Netherlands", "lat": 52.3676, "lon": 4.9041, "url": "amsterdam-north-holland-netherlands"},
            {"name": "Berlin", "region": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050, "url": "berlin-berlin-germany"},
            {"name": "Dubai", "region": "Dubai", "country": "United Arab Emirates", "lat": 25.2048, "lon": 55.2708, "url": "dubai-dubai-united-arab-emirates"},
            {"name": "Singapore", "region": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "url": "singapore-singapore-singapore"},
            {"name": "Toronto", "region": "Ontario", "country": "Canada", "lat": 43.6532, "lon": -79.3832, "url": "toronto-ontario-canada"},
            {"name": "Mexico City", "region": "Mexico City", "country": "Mexico", "lat": 19.4326, "lon": -99.1332, "url": "mexico-city-mexico-city-mexico"},
            {"name": "São Paulo", "region": "São Paulo", "country": "Brazil", "lat": -23.5505, "lon": -46.6333, "url": "sao-paulo-sao-paulo-brazil"},
            {"name": "Bangkok", "region": "Bangkok", "country": "Thailand", "lat": 13.7563, "lon": 100.5018, "url": "bangkok-bangkok-thailand"},
            {"name": "Istanbul", "region": "Istanbul", "country": "Turkey", "lat": 41.0082, "lon": 28.9784, "url": "istanbul-istanbul-turkey"},
            {"name": "Moscow", "region": "Moscow", "country": "Russia", "lat": 55.7558, "lon": 37.6173, "url": "moscow-moscow-russia"},
        ]
        
        # Filter cities matching the query
        matching_cities = []
        for city in demo_cities:
            city_name = city["name"].lower()
            region = city["region"].lower()
            country = city["country"].lower()
            
            # Match if query is in city name, region, or country
            if (query in city_name or 
                city_name.startswith(query) or
                query in region or
                query in country):
                matching_cities.append(city)
        
        return matching_cities[:10]  # Return top 10 matches

    def get_current_weather(self, location: str) -> dict:
        """
        Fetch current weather for a given location.
        Uses location name or coordinates from search results.
        Returns weather data with proper error handling.
        """
        # If using demo mode, return realistic demo data based on location
        if self.use_demo:
            return self._get_realistic_demo_weather(location)
        
        try:
            response = requests.get(
                f"{self.base_url}/current.json",
                params={"key": self.api_key, "q": location, "aqi": "yes"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Format API response
                return {
                    "name": data["location"].get("name", "Unknown"),
                    "region": data["location"].get("region", ""),
                    "country": data["location"].get("country", "Unknown"),
                    "lat": data["location"].get("lat"),
                    "lon": data["location"].get("lon"),
                    "temp_c": data["current"].get("temp_c", 0),
                    "feels_like": data["current"].get("feelslike_c", 0),
                    "humidity": data["current"].get("humidity", 0),
                    "condition": data["current"].get("condition", {}).get("text", "Unknown"),
                    "condition_icon": data["current"].get("condition", {}).get("code", 1000),
                    "wind_kph": data["current"].get("wind_kph", 0),
                    "wind_dir": data["current"].get("wind_dir", "N"),
                    "pressure_mb": data["current"].get("pressure_mb", 0),
                    "visibility_km": data["current"].get("vis_km", 0),
                    "cloud": data["current"].get("cloud", 0),
                    "uv": data["current"].get("uv", 0),
                    "aqi": data["current"].get("air_quality", {}).get("us-epa-index", 0) if data["current"].get("air_quality") else 0,
                }
            else:
                # API failed, use realistic demo
                return self._get_realistic_demo_weather(location)
        except Exception as e:
            print(f"Weather API error: {e}. Using demo weather")
            return self._get_realistic_demo_weather(location)

    def get_forecast(self, location: str, days: int = 5) -> dict:
        """
        Fetch forecast data for a location.
        Falls back to demo forecast if API fails.
        """
        # If using demo mode, return demo forecast
        if self.use_demo:
            return self._get_demo_forecast(location)
        
        try:
            response = requests.get(
                f"{self.base_url}/forecast.json",
                params={"key": self.api_key, "q": location, "days": days, "aqi": "no"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                for day in data["forecast"]["forecastday"]:
                    forecasts.append({
                        "date": day["date"],
                        "max_temp": day["day"]["maxtemp_c"],
                        "min_temp": day["day"]["mintemp_c"],
                        "condition": day["day"]["condition"]["text"],
                        "condition_code": day["day"]["condition"]["code"],
                        "humidity": day["day"]["avg_humidity"],
                        "wind_kph": day["day"]["maxwind_kph"],
                        "chance_rain": day["day"]["daily_chance_of_rain"],
                        "avg_temp": day["day"]["avgtemp_c"],
                        "hourly": day["hour"]
                    })
                
                return {"forecast": forecasts, "location": data["location"]}
            else:
                return self._get_demo_forecast(location)
        except Exception as e:
            print(f"Forecast API error: {e}")
            return self._get_demo_forecast(location)
    
    def _get_realistic_demo_weather(self, location: str) -> dict:
        """
        Generate realistic demo weather data with proper location info.
        Uses hardcoded data for common cities.
        """
        import random
        
        # Realistic demo data for common cities
        location_data = {
            "mumbai": {"city": "Mumbai", "region": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777},
            "delhi": {"city": "Delhi", "region": "Delhi", "country": "India", "lat": 28.7041, "lon": 77.1025},
            "bangalore": {"city": "Bangalore", "region": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946},
            "chennai": {"city": "Chennai", "region": "Tamil Nadu", "country": "India", "lat": 13.0827, "lon": 80.2707},
            "london": {"city": "London", "region": "England", "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278},
            "new york": {"city": "New York", "region": "New York", "country": "United States", "lat": 40.7128, "lon": -74.0060},
            "los angeles": {"city": "Los Angeles", "region": "California", "country": "United States", "lat": 34.0522, "lon": -118.2437},
            "tokyo": {"city": "Tokyo", "region": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
            "sydney": {"city": "Sydney", "region": "New South Wales", "country": "Australia", "lat": -33.8688, "lon": 151.2093},
            "paris": {"city": "Paris", "region": "Île-de-France", "country": "France", "lat": 48.8566, "lon": 2.3522},
        }
        
        # Try to match location with demo data
        location_lower = location.lower().strip()
        loc_info = location_data.get(location_lower)
        
        if not loc_info:
            # If not found, use generic location info
            loc_info = {
                "city": location.split(",")[0].strip().title(),
                "region": "Unknown",
                "country": "Unknown",
                "lat": 0,
                "lon": 0
            }
        
        # Generate realistic weather based on latitude
        hour = datetime.now().hour
        base_temp = 25 if abs(loc_info["lat"]) < 30 else 15  # Hotter near equator
        if hour < 6 or hour > 18:
            base_temp -= 8
        
        conditions = ["Sunny", "Partly cloudy", "Cloudy", "Rainy"]
        condition = random.choice(conditions[:3])
        
        return {
            "name": loc_info["city"],
            "region": loc_info["region"],
            "country": loc_info["country"],
            "lat": loc_info["lat"],
            "lon": loc_info["lon"],
            "temp_c": round(base_temp + random.uniform(-3, 3), 1),
            "feels_like": round(base_temp + random.uniform(-5, -1), 1),
            "humidity": random.randint(40, 85),
            "condition": condition,
            "condition_icon": 1000,
            "wind_kph": round(random.uniform(5, 20), 1),
            "wind_dir": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "pressure_mb": random.randint(1000, 1050),
            "visibility_km": random.randint(8, 15),
            "cloud": random.randint(10, 80),
            "uv": random.randint(1, 8),
            "aqi": random.randint(1, 5),
        }
    
    def _get_demo_weather(self, location: str) -> dict:
        """Legacy demo weather method - redirects to realistic demo"""
        return self._get_realistic_demo_weather(location)
    
    def _get_demo_forecast(self, location: str) -> dict:
        """Generate realistic demo forecast data with hourly breakdown"""
        import random
        
        forecastdays = []
        base_time = datetime.now()
        conditions = ["Sunny", "Partly cloudy", "Cloudy", "Rainy", "Thunderstorm"]
        
        for i in range(5):
            date = base_time + timedelta(days=i)
            base_temp = 22 + 5 * math.sin((i - 2) * math.pi / 5)
            
            # Generate hourly data (24 hours)
            hourly = []
            for hour_num in range(24):
                hour_time = date.replace(hour=hour_num)
                hour_temp = base_temp - 6 if hour_num < 6 else base_temp
                if hour_num > 18:
                    hour_temp = base_temp - 8
                
                hourly.append({
                    "time": hour_time.strftime("%Y-%m-%d %H:%M"),
                    "temp_c": round(hour_temp + random.uniform(-2, 2), 1),
                    "condition": {"text": random.choice(conditions), "code": 1000},
                    "chance_of_rain": random.randint(0, 60)
                })
            
            forecastdays.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": {
                    "maxtemp_c": round(base_temp + random.uniform(3, 7), 1),
                    "mintemp_c": round(base_temp - random.uniform(5, 9), 1),
                    "avgtemp_c": round(base_temp, 1),
                    "condition": {"text": random.choice(conditions), "code": 1000},
                    "avg_humidity": 50 + random.randint(-10, 30),
                    "maxwind_kph": round(5 + random.uniform(0, 15), 1),
                    "daily_chance_of_rain": random.randint(10, 70) if i % 2 == 0 else random.randint(0, 30),
                },
                "hour": hourly
            })
        
        return {
            "forecast": {"forecastday": forecastdays},
            "location": {"name": location}
        }


class CitySearchDropdown(ctk.CTkToplevel):
    """Autocomplete dropdown for city search using real API"""
    def __init__(self, parent, search_entry, api, callback, x, y):
        super().__init__(parent)
        self.withdraw()
        self.attributes("-topmost", True)
        self.search_entry = search_entry
        self.api = api
        self.callback = callback
        self.bg_color = "#1a1a2e"
        self.fg_color = "#2d2d44"
        
        # Window properties
        self.geometry("300x0")
        self.resizable(False, True)
        self.overrideredirect(True)
        
        # Create frame for city list
        self.list_frame = ctk.CTkFrame(self, fg_color=self.fg_color, corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollable frame for cities
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.list_frame,
            fg_color="transparent",
            scrollbar_button_color="#3d3d54",
            scrollbar_button_hover_color="#4d4d64"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.city_buttons = []
        self.selected_index = -1
        self.suggestions = []
        self.parent_window = parent
        
    def show_suggestions(self, query: str, x: int, y: int):
        """
        Show location suggestions based on WeatherAPI.com search results
        Requires minimum 2 characters for search
        """
        # Clear previous suggestions
        for btn in self.city_buttons:
            btn.destroy()
        self.city_buttons = []
        
        # Don't search if less than 2 characters
        if not query or len(query.strip()) < 2:
            self.withdraw()
            return
        
        # Fetch real suggestions from WeatherAPI.com search endpoint
        try:
            self.suggestions = self.api.search_locations(query)
        except Exception as e:
            print(f"Search error: {e}")
            self.suggestions = []
        
        # If no results found
        if not self.suggestions:
            self.withdraw()
            return
        
        # Limit to 10 suggestions
        display_suggestions = self.suggestions[:10]
        
        # Create buttons for each suggestion
        for idx, location in enumerate(display_suggestions):
            # Format display: "City, Region, Country"
            display_text = self._format_location_text(location)
            
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=display_text,
                anchor="w",
                fg_color="transparent",
                hover_color="#3d3d54",
                text_color="white",
                height=40,
                font=ctk.CTkFont(size=12),
                command=lambda loc=location: self._select_location(loc)
            )
            btn.pack(fill="x", padx=0, pady=2)
            self.city_buttons.append(btn)
            btn.bind("<Enter>", lambda e, idx=idx: self._hover_location(idx))
            btn.bind("<Leave>", lambda e: self._unhover_location())
        
        # Position and show dropdown
        height = min(len(display_suggestions) * 42 + 10, 450)
        self.geometry(f"400x{height}")
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.selected_index = -1
    
    def _format_location_text(self, location: dict) -> str:
        """
        Format location data into readable text: "City, Region, Country"
        Handles cases where region or country might be missing
        """
        name = location.get("name", "Unknown")
        region = location.get("region", "").strip()
        country = location.get("country", "Unknown").strip()
        
        # Build format: City, Region, Country
        parts = [name]
        
        if region and region != "":
            parts.append(region)
        
        if country and country != "":
            parts.append(country)
        
        return ", ".join(parts)
        
    def _hover_location(self, idx: int):
        """Handle location button hover"""
        self.selected_index = idx
        if idx < len(self.city_buttons):
            self.city_buttons[idx].configure(fg_color="#3d3d54")
        
    def _unhover_location(self):
        """Handle location button unhover"""
        if self.selected_index >= 0 and self.selected_index < len(self.city_buttons):
            self.city_buttons[self.selected_index].configure(fg_color="transparent")
        
    def _select_location(self, location: dict):
        """Select a location and close dropdown"""
        display_name = self._format_location_text(location)
        
        # Update search entry with formatted location
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, display_name)
        
        # Hide dropdown and trigger callback
        self.withdraw()
        self.callback(location)
        
    def handle_arrow_keys(self, event):
        """Handle arrow key navigation in dropdown"""
        if not self.suggestions or not self.winfo_viewable():
            return
        
        if event.keysym == "Down":
            self.selected_index = (self.selected_index + 1) % len(self.suggestions)
            self._update_selection()
        elif event.keysym == "Up":
            self.selected_index = (self.selected_index - 1) % len(self.suggestions)
            self._update_selection()
        elif event.keysym == "Return":
            if self.selected_index >= 0 and self.selected_index < len(self.suggestions):
                location = self.suggestions[self.selected_index]
                self._select_location(location)
    
    def _update_selection(self):
        """Update visual selection highlight"""
        for idx, btn in enumerate(self.city_buttons):
            if idx == self.selected_index:
                btn.configure(fg_color="#3d3d54")
            else:
                btn.configure(fg_color="transparent")
    
    def hide(self):
        """Hide the dropdown"""
        self.withdraw()


class GlassFrame(ctk.CTkFrame):
    """Glassmorphism-style frame"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=("rgba(255,255,255,0.1)", "#1a1a2e"),
            corner_radius=20,
            border_width=1,
            border_color=("rgba(255,255,255,0.2)", "#2d2d44"),
            **kwargs
        )


class AnimatedBackground(ctk.CTkCanvas):
    """Animated weather background"""
    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.particles = []
        self.weather_type = "clear"
        self.gradient_colors = []
        self.animation_running = True
        self.bind("<Configure>", self._on_resize)
        
    def _on_resize(self, event):
        self._draw_gradient()
        
    def set_weather(self, weather_type: str):
        """Update background based on weather"""
        self.weather_type = weather_type.lower()
        
        gradients = {
            "clear": [("#1a1a2e", "#16213e", "#0f3460", "#533483")],
            "clouds": [("#2c3e50", "#3498db", "#85929e", "#5d6d7e")],
            "rain": [("#1a1a2e", "#2c3e50", "#34495e", "#1c2833")],
            "thunderstorm": [("#0d0d0d", "#1a1a2e", "#2c2c54", "#474787")],
            "snow": [("#ecf0f1", "#bdc3c7", "#95a5a6", "#7f8c8d")],
            "mist": [("#636e72", "#b2bec3", "#dfe6e9", "#95a5a6")]
        }
        
        self.gradient_colors = gradients.get(self.weather_type, gradients["clear"])[0]
        self._draw_gradient()
        self._init_particles()
        
    def _draw_gradient(self):
        """Draw gradient background"""
        width = self.winfo_width() or 800
        height = self.winfo_height() or 600
        
        self.delete("gradient")
        
        colors = self.gradient_colors if self.gradient_colors else ("#1a1a2e", "#16213e", "#0f3460", "#533483")
        
        steps = 100
        for i in range(steps):
            ratio = i / steps
            y1 = int(height * ratio)
            y2 = int(height * (ratio + 1/steps)) + 1
            
            # Interpolate between colors
            idx = min(int(ratio * (len(colors) - 1)), len(colors) - 2)
            local_ratio = (ratio * (len(colors) - 1)) - idx
            
            c1 = self._hex_to_rgb(colors[idx])
            c2 = self._hex_to_rgb(colors[idx + 1])
            
            r = int(c1[0] + (c2[0] - c1[0]) * local_ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * local_ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * local_ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_rectangle(0, y1, width, y2, fill=color, outline=color, tags="gradient")
        
        self.tag_lower("gradient")
        
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _init_particles(self):
        """Initialize weather particles"""
        self.particles = []
        width = self.winfo_width() or 800
        height = self.winfo_height() or 600
        
        import random
        
        if self.weather_type == "rain":
            for _ in range(100):
                self.particles.append({
                    "x": random.randint(0, width),
                    "y": random.randint(-height, 0),
                    "speed": random.uniform(15, 25),
                    "length": random.randint(10, 20)
                })
        elif self.weather_type == "snow":
            for _ in range(50):
                self.particles.append({
                    "x": random.randint(0, width),
                    "y": random.randint(-height, 0),
                    "speed": random.uniform(2, 5),
                    "size": random.randint(2, 5),
                    "drift": random.uniform(-1, 1)
                })
    
    def animate(self):
        """Animate weather particles"""
        if not self.animation_running:
            return
            
        self.delete("particle")
        width = self.winfo_width() or 800
        height = self.winfo_height() or 600
        
        import random
        
        if self.weather_type == "rain":
            for p in self.particles:
                p["y"] += p["speed"]
                p["x"] += 2
                
                if p["y"] > height:
                    p["y"] = random.randint(-50, 0)
                    p["x"] = random.randint(0, width)
                
                self.create_line(
                    p["x"], p["y"],
                    p["x"] - 2, p["y"] - p["length"],
                    fill="#87CEEB", width=1, tags="particle"
                )
                
        elif self.weather_type == "snow":
            for p in self.particles:
                p["y"] += p["speed"]
                p["x"] += p["drift"]
                
                if p["y"] > height:
                    p["y"] = random.randint(-20, 0)
                    p["x"] = random.randint(0, width)
                
                self.create_oval(
                    p["x"] - p["size"], p["y"] - p["size"],
                    p["x"] + p["size"], p["y"] + p["size"],
                    fill="white", outline="white", tags="particle"
                )
        
        self.after(50, self.animate)
    
    def stop_animation(self):
        self.animation_running = False


class WeatherIcon(ctk.CTkLabel):
    """Animated weather icon display"""
    
    WEATHER_EMOJIS = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️"
    }
    
    def __init__(self, master, icon_code: str = "01d", size: int = 80, **kwargs):
        emoji = self.WEATHER_EMOJIS.get(icon_code, "☀️")
        super().__init__(
            master,
            text=emoji,
            font=ctk.CTkFont(size=size),
            **kwargs
        )
        self.icon_code = icon_code
        
    def update_icon(self, icon_code: str):
        self.icon_code = icon_code
        emoji = self.WEATHER_EMOJIS.get(icon_code, "☀️")
        self.configure(text=emoji)


class CircularGauge(ctk.CTkCanvas):
    """Circular progress gauge for metrics"""
    def __init__(self, master, value: float = 0, max_value: float = 100, 
                 label: str = "", unit: str = "", size: int = 120, **kwargs):
        super().__init__(master, width=size, height=size, 
                        bg="#1a1a2e", highlightthickness=0, **kwargs)
        self.size = size
        self.value = value
        self.max_value = max_value
        self.label = label
        self.unit = unit
        self._draw()
        
    def _draw(self):
        self.delete("all")
        
        padding = 10
        center = self.size // 2
        radius = (self.size - padding * 2) // 2
        
        # Background arc
        self.create_arc(
            padding, padding,
            self.size - padding, self.size - padding,
            start=135, extent=270,
            style="arc", width=8,
            outline="#2d2d44"
        )
        
        # Value arc
        percentage = min(self.value / self.max_value, 1.0)
        extent = 270 * percentage
        
        # Color gradient based on value
        if percentage < 0.3:
            color = "#00d4aa"
        elif percentage < 0.6:
            color = "#ffd93d"
        elif percentage < 0.8:
            color = "#ff8c00"
        else:
            color = "#ff4757"
            
        self.create_arc(
            padding, padding,
            self.size - padding, self.size - padding,
            start=135, extent=-extent,
            style="arc", width=8,
            outline=color
        )
        
        # Center text
        self.create_text(
            center, center - 8,
            text=f"{int(self.value)}{self.unit}",
            fill="white",
            font=("Helvetica", 14, "bold")
        )
        self.create_text(
            center, center + 12,
            text=self.label,
            fill="#888888",
            font=("Helvetica", 9)
        )
        
    def set_value(self, value: float):
        self.value = value
        self._draw()


class HourlyForecastCard(GlassFrame):
    """Hourly forecast display card"""
    def __init__(self, master, time: str, temp: float, icon: str, pop: float = 0, **kwargs):
        super().__init__(master, width=80, height=130, **kwargs)
        
        self.grid_propagate(False)
        
        # Time
        ctk.CTkLabel(
            self, text=time,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(10, 5))
        
        # Weather icon
        WeatherIcon(self, icon, size=30).pack()
        
        # Temperature
        ctk.CTkLabel(
            self, text=f"{int(temp)}°",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=5)
        
        # Precipitation probability
        if pop > 0:
            ctk.CTkLabel(
                self, text=f"💧{int(pop*100)}%",
                font=ctk.CTkFont(size=10),
                text_color="#87CEEB"
            ).pack()


class DailyForecastCard(GlassFrame):
    """Daily forecast display card"""
    def __init__(self, master, day: str, high: float, low: float, 
                 icon: str, description: str, **kwargs):
        super().__init__(master, height=60, **kwargs)
        
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=10)
        
        # Day
        ctk.CTkLabel(
            container, text=day,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80, anchor="w"
        ).pack(side="left")
        
        # Icon
        WeatherIcon(container, icon, size=24).pack(side="left", padx=10)
        
        # Description
        ctk.CTkLabel(
            container, text=description.title(),
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            width=100, anchor="w"
        ).pack(side="left", padx=10)
        
        # Temperatures
        temp_frame = ctk.CTkFrame(container, fg_color="transparent")
        temp_frame.pack(side="right")
        
        ctk.CTkLabel(
            temp_frame, text=f"{int(high)}°",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=40
        ).pack(side="left")
        
        ctk.CTkLabel(
            temp_frame, text=f"{int(low)}°",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
            width=40
        ).pack(side="left")


class LifestyleWidget(GlassFrame):
    """Lifestyle insights widget"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.insights = []
        self._build_ui()
        
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header, text="🎯 Lifestyle Insights",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        self.insights_container = ctk.CTkFrame(self, fg_color="transparent")
        self.insights_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
    def update_insights(self, weather_data: dict):
        """Generate lifestyle insights based on weather (WeatherAPI.com format)"""
        for widget in self.insights_container.winfo_children():
            widget.destroy()
        
        try:
            # Extract data with WeatherAPI.com format
            temp = weather_data.get("temp_c", 20)
            humidity = weather_data.get("humidity", 50)
            wind = weather_data.get("wind_kph", 0)
            condition = weather_data.get("condition", "Clear").lower()
            
            insights = []
            
            # Exercise recommendation
            if "clear" in condition or "sunny" in condition or ("cloud" in condition and "rain" not in condition):
                if 15 <= temp <= 28 and wind < 15:
                    insights.append(("🏃", "Great conditions for outdoor exercise", "#00d4aa"))
                else:
                    insights.append(("🏃", "Outdoor activity possible", "#ffd93d"))
            elif "rain" in condition or "drizzle" in condition:
                insights.append(("🏋️", "Indoor workout recommended today", "#ffd93d"))
            else:
                insights.append(("⚠️", "Check conditions before outdoor activities", "#ff8c00"))
                
            # Laundry
            if ("clear" in condition or "sunny" in condition) and humidity < 70:
                insights.append(("👕", "Perfect day to dry clothes outside", "#00d4aa"))
            else:
                insights.append(("👕", "Consider indoor drying today", "#ffd93d"))
                
            # Driving
            if "rain" in condition or "thunder" in condition or "mist" in condition or "fog" in condition:
                insights.append(("🚗", "Drive carefully - reduced visibility", "#ff4757"))
            elif wind > 20:
                insights.append(("🚗", "High winds - secure loose items", "#ffd93d"))
            else:
                insights.append(("🚗", "Good driving conditions", "#00d4aa"))
                
            # Skin protection
            uv = weather_data.get("uv", 3)
            if ("clear" in condition or "sunny" in condition) and 10 <= datetime.now().hour <= 16:
                if uv > 5:
                    insights.append(("🧴", "High UV index - apply sunscreen", "#ff8c00"))
                else:
                    insights.append(("🧴", "Moderate UV - light sunscreen recommended", "#ffd93d"))
            
            # Display insights
            for emoji, text, color in insights[:4]:
                row = ctk.CTkFrame(self.insights_container, fg_color="transparent")
                row.pack(fill="x", pady=3)
                
                ctk.CTkLabel(
                    row, text=emoji,
                    font=ctk.CTkFont(size=16)
                ).pack(side="left")
                
                ctk.CTkLabel(
                    row, text=text,
                    font=ctk.CTkFont(size=12),
                    text_color=color
                ).pack(side="left", padx=10)
        except Exception as e:
            print(f"Error updating lifestyle insights: {e}")


class AirQualityWidget(GlassFrame):
    """Air quality display widget"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build_ui()
        
    def _build_ui(self):
        # Header
        ctk.CTkLabel(
            self, text="🌬️ Air Quality",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # AQI display
        self.aqi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.aqi_frame.pack(fill="x", padx=15, pady=5)
        
        self.aqi_label = ctk.CTkLabel(
            self.aqi_frame, text="42",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#00d4aa"
        )
        self.aqi_label.pack(side="left")
        
        self.aqi_status = ctk.CTkLabel(
            self.aqi_frame, text="Good",
            font=ctk.CTkFont(size=14),
            text_color="#00d4aa"
        )
        self.aqi_status.pack(side="left", padx=15)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=200, height=8)
        self.progress.pack(padx=15, pady=10)
        self.progress.set(0.42)
        
        # Pollutants
        pollutants_frame = ctk.CTkFrame(self, fg_color="transparent")
        pollutants_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        pollutants = [("PM2.5", "12"), ("PM10", "28"), ("O₃", "45")]
        for name, value in pollutants:
            col = ctk.CTkFrame(pollutants_frame, fg_color="transparent")
            col.pack(side="left", expand=True)
            
            ctk.CTkLabel(
                col, text=value,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack()
            ctk.CTkLabel(
                col, text=name,
                font=ctk.CTkFont(size=10),
                text_color="#888888"
            ).pack()


class SunMoonWidget(GlassFrame):
    """Sunrise/Sunset and moon phase widget"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build_ui()
        
    def _build_ui(self):
        # Header
        ctk.CTkLabel(
            self, text="🌅 Sun & Moon",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Sun times
        sun_frame = ctk.CTkFrame(self, fg_color="transparent")
        sun_frame.pack(fill="x", padx=15, pady=5)
        
        # Sunrise
        sunrise_col = ctk.CTkFrame(sun_frame, fg_color="transparent")
        sunrise_col.pack(side="left", expand=True)
        ctk.CTkLabel(sunrise_col, text="🌅", font=ctk.CTkFont(size=24)).pack()
        ctk.CTkLabel(sunrise_col, text="6:12 AM", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkLabel(sunrise_col, text="Sunrise", font=ctk.CTkFont(size=10), text_color="#888888").pack()
        
        # Sunset
        sunset_col = ctk.CTkFrame(sun_frame, fg_color="transparent")
        sunset_col.pack(side="left", expand=True)
        ctk.CTkLabel(sunset_col, text="🌇", font=ctk.CTkFont(size=24)).pack()
        ctk.CTkLabel(sunset_col, text="6:48 PM", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkLabel(sunset_col, text="Sunset", font=ctk.CTkFont(size=10), text_color="#888888").pack()
        
        # Golden hour
        ctk.CTkLabel(
            self, text="✨ Golden Hour: 5:58 PM - 6:48 PM",
            font=ctk.CTkFont(size=11),
            text_color="#ffd93d"
        ).pack(pady=(10, 5))
        
        # Moon phase
        moon_frame = ctk.CTkFrame(self, fg_color="transparent")
        moon_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(moon_frame, text="🌓", font=ctk.CTkFont(size=28)).pack(side="left")
        
        moon_info = ctk.CTkFrame(moon_frame, fg_color="transparent")
        moon_info.pack(side="left", padx=10)
        ctk.CTkLabel(moon_info, text="First Quarter", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(moon_info, text="52% illuminated", font=ctk.CTkFont(size=10), text_color="#888888").pack(anchor="w")


class WeatherApp(ctk.CTk):
    """Main Weather Application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Premium Weather")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Initialize API with WeatherAPI.com API key
        # Replace with your actual WeatherAPI.com key from https://www.weatherapi.com/
        self.api = WeatherAPI("demo")  # Use "demo" for testing without key
        self.current_city = "Mumbai"
        self.current_location = None  # Store the selected location object from search results
        self.weather_data = None
        self.forecast_data = None
        self.search_dropdown = None
        
        self._build_ui()
        self._load_weather()
        
    def _build_ui(self):
        # Animated background
        self.background = AnimatedBackground(self)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.background.set_weather("clear")
        self.background.animate()
        
        # Main container with scrolling
        self.main_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#2d2d44",
            scrollbar_button_hover_color="#3d3d54"
        )
        self.main_container.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self._build_header()
        self._build_current_weather()
        self._build_hourly_forecast()
        self._build_details_section()
        self._build_daily_forecast()
        self._build_widgets_section()
        
    def _build_header(self):
        """Build header with search and location"""
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        # Search frame
        search_frame = GlassFrame(header)
        search_frame.pack(side="left", fill="x", expand=True)
        
        search_inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_inner.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            search_inner, text="📍",
            font=ctk.CTkFont(size=20)
        ).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Search city worldwide...",
            font=ctk.CTkFont(size=14),
            border_width=0,
            fg_color="transparent",
            width=300
        )
        self.search_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.search_entry.insert(0, self.current_city)
        self.search_entry.bind("<Return>", self._on_search)
        self.search_entry.bind("<KeyRelease>", self._on_search_input)
        self.search_entry.bind("<Down>", self._on_arrow_down)
        self.search_entry.bind("<Up>", self._on_arrow_up)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            search_inner,
            text="🔄",
            width=40,
            height=40,
            fg_color="#2d2d44",
            hover_color="#3d3d54",
            command=self._load_weather
        )
        refresh_btn.pack(side="right", padx=(10, 0))
        
        # Current time
        self.time_label = ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%A, %B %d • %I:%M %p"),
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.time_label.pack(side="right", padx=20)
        self._update_time()
        
    def _build_current_weather(self):
        """Build main current weather display"""
        current_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        current_frame.pack(fill="x", padx=30, pady=20)
        
        # Left side - Temperature and condition
        left_panel = GlassFrame(current_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        temp_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        temp_container.pack(fill="x", padx=30, pady=30)
        
        # City name
        self.city_label = ctk.CTkLabel(
            temp_container,
            text="Mumbai",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.city_label.pack(anchor="w")
        
        # Temperature row
        temp_row = ctk.CTkFrame(temp_container, fg_color="transparent")
        temp_row.pack(fill="x", pady=10)
        
        self.weather_icon = WeatherIcon(temp_row, "01d", size=80)
        self.weather_icon.pack(side="left")
        
        self.temp_label = ctk.CTkLabel(
            temp_row,
            text="28°",
            font=ctk.CTkFont(size=72, weight="bold")
        )
        self.temp_label.pack(side="left", padx=20)
        
        # Condition and feels like
        details_col = ctk.CTkFrame(temp_row, fg_color="transparent")
        details_col.pack(side="left", fill="y")
        
        self.condition_label = ctk.CTkLabel(
            details_col,
            text="Partly Cloudy",
            font=ctk.CTkFont(size=18)
        )
        self.condition_label.pack(anchor="w", pady=(15, 5))
        
        self.feels_like_label = ctk.CTkLabel(
            details_col,
            text="Feels like 30°",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        self.feels_like_label.pack(anchor="w")
        
        # High/Low
        self.highlow_label = ctk.CTkLabel(
            details_col,
            text="H: 32° • L: 24°",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        self.highlow_label.pack(anchor="w")
        
        # Right side - Quick stats
        right_panel = GlassFrame(current_frame, width=300)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        stats_title = ctk.CTkLabel(
            right_panel,
            text="Weather Details",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_title.pack(pady=(20, 15))
        
        self.stats_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.stats_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Stats will be populated when data loads
        self.stat_labels = {}
        stats = [
            ("💨 Wind", "wind"),
            ("💧 Humidity", "humidity"),
            ("👁️ Visibility", "visibility"),
            ("📊 Pressure", "pressure"),
            ("☁️ Clouds", "clouds"),
            ("🌡️ Dew Point", "dew_point")
        ]
        
        for i, (icon_label, key) in enumerate(stats):
            row = ctk.CTkFrame(self.stats_container, fg_color="transparent")
            row.pack(fill="x", pady=8)
            
            ctk.CTkLabel(
                row, text=icon_label,
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            ).pack(side="left")
            
            self.stat_labels[key] = ctk.CTkLabel(
                row, text="--",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            self.stat_labels[key].pack(side="right")
            
    def _build_hourly_forecast(self):
        """Build hourly forecast scrollable section"""
        section_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        section_frame.pack(fill="x", padx=30, pady=10)
        
        # Header
        header = ctk.CTkFrame(section_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header,
            text="⏰ Hourly Forecast",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Next 24 hours",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(side="right")
        
        # Scrollable hourly cards
        self.hourly_scroll = ctk.CTkScrollableFrame(
            section_frame,
            height=170,
            width=1000,
            fg_color="transparent",
            orientation="horizontal",
            scrollbar_button_color="#2d2d44",
            scrollbar_button_hover_color="#3d3d54"
        )
        self.hourly_scroll.pack(fill="both", expand=True, padx=0, pady=(10, 0))
        
    def _build_details_section(self):
        """Build gauges and detailed metrics"""
        section_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        section_frame.pack(fill="x", padx=30, pady=10)
        
        # Gauges row
        gauges_frame = GlassFrame(section_frame)
        gauges_frame.pack(fill="x", pady=10)
        
        gauges_inner = ctk.CTkFrame(gauges_frame, fg_color="transparent")
        gauges_inner.pack(fill="x", padx=30, pady=20)
        
        # Create gauges
        self.gauges = {}
        
        gauge_configs = [
            ("humidity", "Humidity", "%", 100),
            ("uv", "UV Index", "", 11),
            ("wind", "Wind", "km/h", 50),
            ("visibility", "Visibility", "km", 20)
        ]
        
        for key, label, unit, max_val in gauge_configs:
            col = ctk.CTkFrame(gauges_inner, fg_color="transparent")
            col.pack(side="left", expand=True, padx=10)
            
            gauge = CircularGauge(col, value=0, max_value=max_val, 
                                 label=label, unit=unit, size=100)
            gauge.pack()
            self.gauges[key] = gauge
            
    def _build_daily_forecast(self):
        """Build 7-day forecast section"""
        section_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        section_frame.pack(fill="x", padx=30, pady=10)
        
        # Header
        header = ctk.CTkFrame(section_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header,
            text="📅 7-Day Forecast",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Daily cards container
        self.daily_container = GlassFrame(section_frame)
        self.daily_container.pack(fill="x")
        
    def _build_widgets_section(self):
        """Build additional widgets section"""
        section_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        section_frame.pack(fill="x", padx=30, pady=(10, 30))
        
        # Header
        ctk.CTkLabel(
            section_frame,
            text="🎯 Insights & More",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Widgets grid
        widgets_grid = ctk.CTkFrame(section_frame, fg_color="transparent")
        widgets_grid.pack(fill="x")
        
        # Configure grid
        widgets_grid.columnconfigure(0, weight=1)
        widgets_grid.columnconfigure(1, weight=1)
        widgets_grid.columnconfigure(2, weight=1)
        
        # Lifestyle insights
        self.lifestyle_widget = LifestyleWidget(widgets_grid)
        self.lifestyle_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Air quality
        self.air_quality_widget = AirQualityWidget(widgets_grid)
        self.air_quality_widget.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Sun & Moon
        self.sun_moon_widget = SunMoonWidget(widgets_grid)
        self.sun_moon_widget.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
    def _update_time(self):
        """Update time display"""
        self.time_label.configure(
            text=datetime.now().strftime("%A, %B %d • %I:%M %p")
        )
        self.after(60000, self._update_time)
    
    def _on_search_input(self, event=None):
        """Handle search input to show suggestions from API"""
        query = self.search_entry.get()
        
        # Create dropdown if it doesn't exist
        if self.search_dropdown is None:
            # Get position of search entry
            x = self.search_entry.winfo_rootx()
            y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
            self.search_dropdown = CitySearchDropdown(self, self.search_entry, self.api, self._on_location_selected, x, y)
        
        # Show suggestions from API
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
        self.search_dropdown.show_suggestions(query, x, y)
    
    def _on_arrow_down(self, event):
        """Handle down arrow in search"""
        if self.search_dropdown and self.search_dropdown.winfo_viewable():
            self.search_dropdown.handle_arrow_keys(event)
            return "break"
    
    def _on_arrow_up(self, event):
        """Handle up arrow in search"""
        if self.search_dropdown and self.search_dropdown.winfo_viewable():
            self.search_dropdown.handle_arrow_keys(event)
            return "break"
    
    def _on_location_selected(self, location: dict):
        """Handle location selection from dropdown with coordinates"""
        self.current_location = location
        # Build display name
        name = location.get("name", "Unknown")
        state = location.get("state", "")
        country = location.get("country", "")
        self.current_city = name
        
        if self.search_dropdown:
            self.search_dropdown.hide()
        self._load_weather()
        
    def _on_search(self, event=None):
        """Handle search key press (Enter key)"""
        city = self.search_entry.get().strip()
        if city:
            self.current_city = city
            if self.search_dropdown:
                self.search_dropdown.hide()
            
            # If no location selected from dropdown, search for it
            if not self.current_location:
                threading.Thread(
                    target=self._search_and_load,
                    args=(city,),
                    daemon=True
                ).start()
            else:
                self._load_weather()
    
    def _search_and_load(self, query):
        """Search for location and load weather if found"""
        results = self.api.search_locations(query)
        if results:
            self.current_location = results[0]
            self._load_weather()
        else:
            self.root.after(0, lambda: messagebox.showwarning(
                "Location Not Found",
                f"Could not find weather data for '{query}'"
            ))
        
    def _load_weather(self):
        """Load weather data in background thread using WeatherAPI.com"""
        def fetch():
            try:
                # Determine location string for API request
                location_str = self.current_city
                
                # If we have a location object from search, use the URL for precision
                if self.current_location:
                    location_str = self.current_location.get("url", self.current_city)
                
                # Fetch weather using WeatherAPI.com
                self.weather_data = self.api.get_current_weather(location_str)
                
                # Fetch forecast using WeatherAPI.com
                self.forecast_data = self.api.get_forecast(location_str)
                
                # Ensure we have valid data
                if not self.weather_data:
                    print("Error: No weather data received")
                    self.weather_data = self.api._get_realistic_demo_weather(location_str)
                
                if not self.forecast_data:
                    print("Error: No forecast data received")
                    self.forecast_data = self.api._get_demo_forecast(location_str)
                
                self.after(0, self._update_display)
            except Exception as e:
                print(f"Error loading weather: {e}")
                # Fallback to demo data
                self.weather_data = self.api._get_realistic_demo_weather(self.current_city)
                self.forecast_data = self.api._get_demo_forecast(self.current_city)
                self.after(0, self._update_display)
        
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
        
    def _update_display(self):
        """Update all display elements with new WeatherAPI.com data"""
        try:
            if not self.weather_data:
                print("Warning: No weather data to display")
                return
                
            data = self.weather_data
            
            # Map condition text to background weather type
            condition_text = data.get("condition", "unknown").lower()
            if "rain" in condition_text or "drizzle" in condition_text:
                weather_type = "rain"
            elif "thunder" in condition_text or "storm" in condition_text:
                weather_type = "thunderstorm"
            elif "snow" in condition_text:
                weather_type = "snow"
            elif "cloud" in condition_text or "overcast" in condition_text:
                weather_type = "clouds"
            elif "fog" in condition_text or "mist" in condition_text:
                weather_type = "mist"
            else:
                weather_type = "clear"
            
            # Update background based on weather
            self.background.set_weather(weather_type)
            
            # Update main display with proper WeatherAPI.com fields
            location_text = f"{data.get('name', 'Unknown')}"
            if data.get('region'):
                location_text += f", {data['region']}"
            location_text += f", {data.get('country', 'Unknown')}"
            self.city_label.configure(text=location_text)
            
            self.temp_label.configure(text=f"{int(data.get('temp_c', 0))}°")
            self.condition_label.configure(text=data.get("condition", "Unknown").title())
            self.feels_like_label.configure(text=f"Feels like {int(data.get('feels_like', 0))}°")
            
            # WeatherAPI doesn't provide min/max in current endpoint, show dashes
            self.highlow_label.configure(text="H: -- • L: --")
            
            # Update stats with WeatherAPI.com fields
            wind_dir = data.get("wind_dir", "N")
            self.stat_labels["wind"].configure(text=f"{data.get('wind_kph', 0)} km/h {wind_dir}")
            self.stat_labels["humidity"].configure(text=f"{data.get('humidity', 0)}%")
            self.stat_labels["visibility"].configure(text=f"{data.get('visibility_km', 0):.0f} km")
            self.stat_labels["pressure"].configure(text=f"{data.get('pressure_mb', 0):.0f} hPa")
            self.stat_labels["clouds"].configure(text=f"{data.get('cloud', 0)}%")
            
            # Calculate dew point (approximate formula)
            temp = data.get('temp_c', 0)
            humidity = data.get('humidity', 0)
            dew_point = temp - ((100 - humidity) / 5)
            self.stat_labels["dew_point"].configure(text=f"{int(dew_point)}°")
            
            # Update gauges with WeatherAPI.com data
            self.gauges["humidity"].set_value(data.get("humidity", 0))
            self.gauges["uv"].set_value(data.get("uv", 0))
            self.gauges["wind"].set_value(data.get("wind_kph", 0))
            self.gauges["visibility"].set_value(data.get("visibility_km", 0))
            
            # Update lifestyle widget with WeatherAPI.com format
            self.lifestyle_widget.update_insights(data)
            
            # Update hourly forecast
            self._update_hourly_forecast()
            
            # Update daily forecast
            self._update_daily_forecast()
        except Exception as e:
            print(f"Error updating display: {e}")
        
    def _update_hourly_forecast(self):
        """Update hourly forecast cards with WeatherAPI.com data"""
        for widget in self.hourly_scroll.winfo_children():
            widget.destroy()
            
        if not self.forecast_data:
            print("No forecast data available")
            return
        
        # Extract hourly data from first day of forecast
        try:
            # Handle both forecast structures
            if "forecast" in self.forecast_data:
                forecastdays = self.forecast_data.get("forecast", {}).get("forecastday", [])
            else:
                forecastdays = []
            
            if not forecastdays:
                print(f"No forecastdays found. Data keys: {self.forecast_data.keys()}")
                return
            
            # Get hourly data from today
            hours = forecastdays[0].get("hour", [])
            
            if not hours:
                print(f"No hourly data. Day keys: {forecastdays[0].keys()}")
                return
            
            # Show only next 8 hours
            created_cards = 0
            for i, hour_data in enumerate(hours[:8]):
                try:
                    # Parse time
                    time_str = hour_data.get("time", "")
                    if " " in time_str:
                        hour_part = time_str.split(" ")[1]  # "14:30"
                        hour_num = int(hour_part.split(":")[0])
                        time_display = "Now" if i == 0 else f"{hour_num % 12 or 12} {'AM' if hour_num < 12 else 'PM'}"
                    else:
                        time_display = f"Hour {i}"
                    
                    temp = hour_data.get("temp_c", 0)
                    condition = hour_data.get("condition", {}).get("text", "Unknown")
                    chance_rain = hour_data.get("chance_of_rain", 0)
                    
                    # Map condition to icon code (simplified)
                    icon_map = {
                        "sunny": "01d", "clear": "01d", "cloudy": "04d", "overcast": "04d",
                        "rain": "09d", "drizzle": "09d", "thunderstorm": "11d", "snow": "13d"
                    }
                    icon = icon_map.get(condition.lower(), "02d")
                    
                    card = HourlyForecastCard(
                        self.hourly_scroll,
                        time=time_display,
                        temp=int(temp),
                        icon=icon,
                        pop=chance_rain / 100
                    )
                    card.pack(side="left", padx=5, pady=5, fill="both")
                    created_cards += 1
                except Exception as card_err:
                    print(f"  Error creating hour card {i}: {card_err}")
                
            print(f"✓ Hourly forecast loaded: {created_cards} cards created and packed")
        except Exception as e:
            print(f"Error updating hourly forecast: {e}")
            
    def _update_daily_forecast(self):
        """Update daily forecast cards with WeatherAPI.com data"""
        for widget in self.daily_container.winfo_children():
            widget.destroy()
            
        if not self.forecast_data:
            print("No forecast data available for daily")
            return
        
        try:
            # Handle both forecast structures
            if "forecast" in self.forecast_data:
                forecastdays = self.forecast_data.get("forecast", {}).get("forecastday", [])
            else:
                forecastdays = []
            
            if not forecastdays:
                print(f"No forecastdays found for daily. Data keys: {self.forecast_data.keys()}")
                return
            
            # Create cards for next 5-7 days
            created_cards = 0
            for i, day_data in enumerate(forecastdays[:7]):
                try:
                    date_str = day_data.get("date", "")
                    day_info = day_data.get("day", {})
                    
                    # Format day name
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        day_name = "Today" if i == 0 else date_obj.strftime("%A")
                    else:
                        day_name = f"Day {i+1}"
                    
                    high_temp = day_info.get("maxtemp_c", 0)
                    low_temp = day_info.get("mintemp_c", 0)
                    condition = day_info.get("condition", {}).get("text", "Unknown")
                    
                    # Map condition to icon code
                    icon_map = {
                        "sunny": "01d", "clear": "01d", "cloudy": "04d", "overcast": "04d",
                        "rain": "09d", "drizzle": "09d", "thunderstorm": "11d", "snow": "13d"
                    }
                    icon = icon_map.get(condition.lower(), "02d")
                    
                    card = DailyForecastCard(
                        self.daily_container,
                        day=day_name,
                        high=int(high_temp),
                        low=int(low_temp),
                        icon=icon,
                        description=condition
                    )
                    card.pack(fill="x", pady=2, padx=10, expand=False)
                    created_cards += 1
                except Exception as card_err:
                    print(f"  Error creating day card {i}: {card_err}")
            
            print(f"✓ Daily forecast loaded: {created_cards} cards created and packed")
        except Exception as e:
            print(f"Error updating daily forecast: {e}")
            
    def destroy(self):
        """Clean up on close"""
        self.background.stop_animation()
        super().destroy()


def main():
    app = WeatherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
