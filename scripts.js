const apiKey = "6c5642e7e476b31a7d5d77ef8c5357d3";

const searchBtn = document.getElementById("SearchBtn");
const cityInput = document.getElementById("city_input");
const locationBtn = document.getElementById("locationBtn");

function showError(message) {
    alert(message);
}

function handleSearch() {
    const city = cityInput.value.trim();
    if (!city) {
        showError("Please enter a city name.");
        return;
    }
    getWeather(city);
}

searchBtn.addEventListener("click", handleSearch);

cityInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") {
        handleSearch();
    }
});

locationBtn.addEventListener("click", () => {
    if (!navigator.geolocation) {
        showError("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            getWeatherByCoordinates(pos.coords.latitude, pos.coords.longitude);
        },
        (err) => {
            console.error(err);
            showError("Unable to get your location. Please allow location access.");
        }
    );
});

async function getWeather(city) {
    const url =
        `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(
            city
        )}&units=metric&appid=${apiKey}`;

    try {
        const res = await fetch(url);

        if (!res.ok) {
            if (res.status === 404) {
                showError("City not found! Please check the spelling.");
            } else if (res.status === 401) {
                showError("API key issue. Please check your OpenWeather API key.");
            } else {
                showError("Failed to fetch weather data.");
            }
            return;
        }

        const data = await res.json();
        updateCurrentWeatherUI(data);
        getFiveDayForecast(data.name);
    } catch (error) {
        console.error(error);
        showError("Network error. Please check your internet connection.");
    }
}

async function getWeatherByCoordinates(lat, lon) {
    const url =
        `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`;

    try {
        const res = await fetch(url);

        if (!res.ok) {
            showError("Failed to fetch weather for your location.");
            return;
        }

        const data = await res.json();
        updateCurrentWeatherUI(data);
        getFiveDayForecast(data.name);
    } catch (error) {
        console.error(error);
        showError("Network error while fetching location weather.");
    }
}

function updateCurrentWeatherUI(data) {
    document.getElementById("temp").innerText =
        `${Math.round(data.main.temp)}°C`;
    document.getElementById("weatherDesc").innerText =
        data.weather[0].description;
    document.getElementById("weatherIcon").src =
        `https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`;
    document.getElementById("location").innerText =
        `${data.name}, ${data.sys.country}`;
    document.getElementById("date").innerText =
        new Date().toDateString();

    const feelsLikeEl = document.getElementById("feelsLike");
    const humidityEl = document.getElementById("humidity");
    const windEl = document.getElementById("wind");

    if (feelsLikeEl) {
        feelsLikeEl.innerText = `${Math.round(data.main.feels_like)}°C`;
    }
    if (humidityEl) {
        humidityEl.innerText = `${data.main.humidity}%`;
    }
    if (windEl) {
        windEl.innerText = `${data.wind.speed} m/s`;
    }
}

async function getFiveDayForecast(city) {
    const url =
        `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(
            city
        )}&units=metric&appid=${apiKey}`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        if (data.cod !== "200" || !Array.isArray(data.list)) {
            console.warn("Forecast error:", data);
            return;
        }

        const container = document.getElementById("forecastContainer");
        if (!container) return;

        container.innerHTML = "";

        const dayMap = {};

        data.list.forEach(item => {
            const date = item.dt_txt.split(" ")[0];
            if (!dayMap[date]) dayMap[date] = item;
        });

        Object.values(dayMap)
            .slice(0, 5)
            .forEach(item => {
                const dateLabel = new Date(item.dt_txt)
                    .toLocaleDateString("en-US", { weekday: "short" });

                const icon = item.weather[0].icon;
                const temp = Math.round(item.main.temp);
                const desc = item.weather[0].description;

                const rowHTML = `
                    <div class="forecast-row">
                        <div class="forecast-left">
                            <p class="forecast-date">${dateLabel}</p>
                            <img src="https://openweathermap.org/img/wn/${icon}.png" alt="${desc}">
                        </div>
                        <p class="forecast-temp">${temp}°C</p>
                        <p class="forecast-desc">${desc}</p>
                    </div>
                `;

                container.innerHTML += rowHTML;
            });
    } catch (error) {
        console.error(error);
    }
}

// Default city on load
window.addEventListener("DOMContentLoaded", () => {
    getWeather("Mumbai");
});
