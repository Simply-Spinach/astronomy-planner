//import { WEATHER_API_KEY } from "./API_KEYS.mjs";

const WEATHER_API_KEY = 'e743aae5077a47e79e1231340260704'
const WEATHER_API_URL = `https://api.weatherapi.com/v1/forecast.json?key=${WEATHER_API_KEY}`;
const IP_API_URL = 'https://api.ipify.org/?format=json';

const WEATHER_API_URL_OPTIONS = {
	method: 'GET'
};

const WEATHER_API_DAY_COUNT = 3;

/* Public exported functions */


//Returns weatherAPI weather forecast output for desired latitude and longitude
export async function getWeatherFromCoords(latitude, longitude)
{
    let location = `${latitude},${longitude}`;
    const output = await getWeatherData(location)
    return output;
}

//Returns weatherAPI weather forecast output for desired city
export async function getWeatherFromCity(city)
{
    //cook city name
    city = city.trim();
    city = city.replace(/[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]/g, '');
    city = city.replaceAll(' ', '-');

    const output = await getWeatherData(city);
    return output;
}

/* Prepared private functions */

//Gets weatherData from saved city
async function getWeatherData(locationRaw)
{
    //prep local url
    let url = WEATHER_API_URL;
    url += `&q=${locationRaw}&days=${WEATHER_API_DAY_COUNT}`;

    //get response
    try {
        const response = await fetch(url, WEATHER_API_URL_OPTIONS);
        if (response.ok) {
            const result = await response.json();
            return result;
        } else {
            throw(response.status);
        }
    } catch (error) {

    }
}
