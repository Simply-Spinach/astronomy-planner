//BELOW CODE DOES NOT WORK (Should be server side?)
import {ASTRONOMY_API_APP_ID, ASTRONOMY_API_SECRET} from './API_KEYS.mjs'

//enable to prevent API calls and instead use test data
const DEBUG_MODE = true;

const API_FORECAST_URL = "https://api.astronomyapi.com/api/v2/bodies/positions"

//const AUTH_SECRET = 

export async function getForecastedAstronomyData(latitude, longitude, altitude)
{
    //asign consts and vars
    const AUTH_STRING = btoa(`${ASTRONOMY_API_APP_ID}:${ASTRONOMY_API_SECRET}`);
    const URL_OPTIONS = 
    {
        method:'GET',
        headers:
        {
            'Authorization': 'Basic ' + AUTH_STRING,
            'Content-Type': 'application/json'
        }
    }   

    //fix altitude to 0 if identified as null (not able to determine)
    if (altitude === null)
    {
        altitude = 0;
    }
    
    //prep dates
    let curDate = new Date();
    let futureDate = new Date(curDate);
    futureDate.setDate(futureDate.getDate() + 14);

    //turn to things we can input into get function
    let curMonth = curDate.getMonth() + 1;

    //cook current date
    if (curMonth < 10)
    {
        curMonth = '0' + String(curMonth);
    }
    let curDay = curDate.getDate();
    if (curDay < 10)
    {
        curDay = '0' + String(curDay);
    }

    //cook future date
    let futureMonth = futureDate.getMonth() + 1;
    if (futureMonth < 10)
    {
        futureMonth = '0' + String(futureMonth);
    }
    let futureDay = futureDate.getDate();
    if (futureDay < 10)
    {
        futureDay = '0' + String(futureDay);
    }

    //set our from and to dates
    let fromDate = `${curDate.getFullYear()}-${curMonth}-${curDay}`;
    let toDate = `${futureDate.getFullYear()}-${futureMonth}-${futureDay}`;
    
    //current time used to be computed here but I realized I should probably just check every midnight instead as that's when you're actually looking at the stars
    
    //prep url

    //NOTE FOR SELF: ONLY CHECKS TIMES ALMOST AT MIDNIGHT EVERY NIGHT.  UPDATE LATER TO COMBINE DATA FROM MULTIPLE TIMES, ONCE I DISCOVER THE RATE LIMITS
    let url = `${API_FORECAST_URL}/?latitude=${latitude}&longitude=${longitude}&elevation=${altitude}&from_date=${fromDate}&to_date=${toDate}&time=23%3A59%3A59`;

    try
    {
        console.log("Attempting via URL: " + url);
        const response = await fetch(url, URL_OPTIONS)
        console.log("Response get!")
        if (response.ok)
        {
            return response.json();
        }
        else
        {
            console.error("Response was not ok")
            console.error("Response code: " + response.statusText)
            console.error(await response.text())
            return null;
        }
    }
    catch (error)
    {
        //error processing here
        console.error()
        return null;
    }
}
