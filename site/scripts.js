import {getWeatherFromCoords, getWeatherFromCity} from "./weather_api.mjs"
import {getForecastedAstronomyData} from "./astronomy_api.mjs"

//prepare setup for modifying the dom
document.addEventListener("DOMContentLoaded", function()
{
    // actual executed code goes here
    let domHandler = new domLoader();

    let searchFourm = document.querySelector('form#citySearch');

    searchFourm.addEventListener('submit', function(e)
    {
        e.preventDefault();

        domHandler.setLocationCity(searchFourm['searchbar'].value)
    });
});

//create domLoader class for ease of use
class domLoader
{
    #timelineHandler;
    #dayHandler;

    #curLocationStr;
    #astroData;
    #weatherData;

    constructor()
    {
        //load dayHandler and timelineHandler
        this.#dayHandler = new domDayHandler();
        this.#timelineHandler = new domTimelineHandler();

        //load first data
        this.setLocationGPS();
    }

    setLocationCity(cityName)
    {
        //update weather and pull lat/long from update to input into getForecastedAstronomyData
        getWeatherFromCity(cityName).then((weatherData) => 
        {
            //update current weatherData
            this.#weatherData = weatherData;

            //update forecastAstroData using lat and long pulled from weatherData for convenience
            getForecastedAstronomyData(weatherData.location.lat, weatherData.location.lon, 0 /*No altitude data so setting to 0*/).then((astroData) =>
            {
                //update data from astroData
                this.#astroData = astroData;
                
                //update visuals
                this.update();
            });
        });
    }

    async setLocationGPS()
    {
        //get current location
        if (navigator.geolocation)
        {
            navigator.geolocation.getCurrentPosition((location) =>
            {
                //load weather data
                getWeatherFromCoords(location.coords.latitude, location.coords.longitude).then((e) =>
                {
                    this.#weatherData = e;
                    //load astro data
                    getForecastedAstronomyData(location.coords.latitude, location.coords.longitude, location.coords.altitude).then((e) =>
                    {
                        this.#astroData = e;

                        //update visuals
                        this.update();
                    });
                });

            });
        }
        else
        {
            console.warn("GPS request failed.  Remember to implement backup method (like IP?)")
        }
    }

    clear()
    {
        //clear all dayHandler and timelineHandler conteent
        this.#dayHandler.clear();
        this.#timelineHandler.clear();

        //add class on body to hide non-functioning content
        document.body.classList.add("no_content");
    }

    update()
    {
        //update titlebar to location
        document.querySelector('#location').innerText = this.#weatherData.location.name;

        this.clear();

        this.#dayHandler.update(this.#weatherData, this.#astroData);
        this.#timelineHandler.update(this.#weatherData, this.#astroData.data);

        document.body.classList.remove("no_content");
    }
}

const DAY_NODE_CONTAINER_QUERY = '#dayIdentifier'
const DAY_NODE_QUERY = '.dayInfo';
const DAY_NODE_DAY_NAME_QUERY = '.day';
const SIMPLE_DAY_NODE_QUERY = '.dayLabel';

class domDayHandler
{
    #daysContainer;
    #dayTemplate;
    #simpleDayTemplate;

    constructor()
    {
        this.#daysContainer = document.querySelector(DAY_NODE_CONTAINER_QUERY);
        this.#dayTemplate = this.#daysContainer.querySelector(DAY_NODE_QUERY);
        this.#simpleDayTemplate = this.#daysContainer.querySelector(SIMPLE_DAY_NODE_QUERY);

        this.#daysContainer.removeChild(this.#dayTemplate);
        this.#daysContainer.removeChild(this.#simpleDayTemplate);
    }

    //Clears all days from the daysContainer
    clear()
    {
        this.#daysContainer.innerHTML = '';
    }

    update(weatherData, astroData)
    {
        //for simplicity, clear all days from daysContainer
        this.clear();


        let weatherForecastAvailable = weatherData.forecast.forecastday.length;
        let astroForecastAvailable = astroData.data.table.header.length; /* I really can't figure out how to do the math here and I don't want to worry about it*/;

        for (let i = 0; i < astroForecastAvailable; ++i)
        {
            //create day to add to daysContainer
            let currentTime = new Date();

            let curAstro = astroData.data.table[i];
            let curDay; //set later

            //set default curDay template
            if (i < weatherForecastAvailable) //has forecast info
            {
                curDay = this.#dayTemplate.cloneNode(true);
            }
            else //no forecast info
            {
                curDay = this.#simpleDayTemplate.cloneNode(true);
            }
            
            //set day
            if (i == 0)
            {
                curDay.querySelector(DAY_NODE_DAY_NAME_QUERY).innerText = 'Tonight';
            }
            else if (i == 1)
            {
                curDay.querySelector(DAY_NODE_DAY_NAME_QUERY).innerText = "Tomorrow";
            }
            else if (i < 7) //same week
            {
                let daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                let selectWeekDay = (currentTime.getDay() + i - 1) % 6;
                
                curDay.querySelector(DAY_NODE_DAY_NAME_QUERY).innerText = daysOfWeek[selectWeekDay];
            }
            else //just throw out the date
            {
                let nodeTime = currentTime;
                nodeTime.setDate(currentTime.getDate() + i);
                
                curDay.querySelector(DAY_NODE_DAY_NAME_QUERY).innerText = `${nodeTime.getMonth() + 1}-${nodeTime.getDate()}-${nodeTime.getFullYear()}`
            }

            //set phase from moon info
            curDay.querySelector('.moonPhase').innerText = astroData.data.table.rows[1].cells[i].extraInfo.phase.string;

            //complex info for other stuff
            if (i < weatherForecastAvailable)
            {
                //get weather data            
                let curWeather = weatherData.forecast.forecastday[i].day;

                curDay.querySelector('.weatherIcon').src = curWeather.condition.icon;

                //update sunset and sunrise
                if (i < weatherForecastAvailable - 1)
                {
                    curDay.querySelector('.timeframe .sunset').innerText = weatherData.forecast.forecastday[i].astro.sunset;
                    curDay.querySelector('.timeframe .sunrise').innerText = weatherData.forecast.forecastday[i + 1].astro.sunrise;
                }
                else if (i == weatherForecastAvailable - 1)
                {
                    curDay.querySelector('.timeframe').innerHTML = `Sunset: <span class="sunset">${weatherData.forecast.forecastday[i].astro.sunset}</span>`;
                }
            }
            else //we don't have weather data and nothing gets set
            {

            }
            
            //Add to DOM
            this.#daysContainer.appendChild(curDay);
        }
    }
}

class domTimelineHandler
{
    #timelineTemplate;
    #lineSegmentTemplate;
    #lineSegmentBeginTemplate;
    #lineSegmentEndTemplate;
    //added to help with Chromium bug (developed on firefox and without thinking introduced bugs on 99% of the world's browsers)
    #lineSegmentBridgeTemplate;
    
    #planetsContainer;

    constructor()
    {
        this.#timelineTemplate = document.querySelector(".timeline").cloneNode(true);

        //prep line segments
        this.#lineSegmentTemplate = this.#timelineTemplate.querySelector(".line .lineSegment").cloneNode(/*true /* REMOVE COMMENT FOR DEBUGGING MODE*/);
        this.#lineSegmentBeginTemplate = this.#timelineTemplate.querySelector(".lineSegment .left-cap").cloneNode();
        this.#lineSegmentEndTemplate = this.#timelineTemplate.querySelector(".lineSegment .right-cap").cloneNode();

        this.#lineSegmentBridgeTemplate = this.#timelineTemplate.querySelector(".line .left-bridge").cloneNode();

        //remove children from timelineTemplate's line
        this.#timelineTemplate.querySelector('.line').innerHTML = '';

        //get containers by type
        this.#planetsContainer = document.querySelector(".timeline-holder > .sectionType#planets");
        this.clear()
    }

    clear()
    {
        //clear timelines from objects stored
        for (let child of this.#planetsContainer.querySelectorAll('.timeline'))
        {
            this.#planetsContainer.removeChild(child);
        }
    }

    update(weatherData, astroData)
    {
        //just reset us and rebuild the dom for simplicity of coding
        this.clear();

        for (let planetID = 2 /*First planet after sun and moon tracking*/; planetID < astroData.table.rows.length; ++planetID)
        {
            let planetData = astroData.table.rows[planetID];

            if (planetData.entry.name == "Earth")
            {
                continue;
            }

            let curTimeline = this.#timelineTemplate.cloneNode(true);
            
            //prepare names to be visible
            curTimeline.querySelector(".objectLabel").innerText = planetData.entry.name;
            
            //mark days when viewable
            let lastEmptyDay = -1;
            let visibleDays = this.getDaysViewable(planetData, weatherData);
            let lastSegmentVisible = null; //defined after first loop
            
            //Debugging to find planet ids
            console.log(`${planetID}, ${planetData.entry.name}`);

            for (let i = 0; i < visibleDays.length; ++i)
            {
                //for some reason, we have earth as a planet you can view in our data, so we're forcing it out

                let isVisibleToday = visibleDays[i];
                let curLineSegment;
                           
                if (isVisibleToday)
                {
                    //setup line segment
                    
                    curLineSegment = this.#lineSegmentTemplate.cloneNode(true);
                                        
                    if (i > 0 && !lastSegmentVisible) //general case to add start point
                    {
                        //insert beginning point
                        curLineSegment.appendChild(this.#lineSegmentBeginTemplate.cloneNode(true));
                        
                    }
                    else if (i > 0 && lastSegmentVisible)
                    {
                        //patch for Chromium: add bridge to help cover gaps between lines
                        curLineSegment.appendChild(this.#lineSegmentBridgeTemplate.cloneNode(true));
                    }
                    else if (i == 0) //edge case where we do want a start here
                    {
                        curLineSegment.appendChild(this.#lineSegmentBeginTemplate.cloneNode(true));
                    }
                    /* if (i == 0 && isVisibleToday) //first node edge case.  Has segment behind it 
                    {
                        curLineSegment.appendChild(this.#lineSegmentBeginTemplate.cloneNode());
                    } */
                    
                }
                else //isVisibleToday == false
                {
                    if (i > 0 && lastSegmentVisible == true) //needs cap on last segment when called
                    {
                        curTimeline.querySelector('.line').lastElementChild.appendChild(this.#lineSegmentEndTemplate.cloneNode(true));
                    }

                    //enter empty div into dom
                    curLineSegment = document.createElement("div");                    
                    
                }
                
                //add timeline to dom
                this.#planetsContainer.appendChild(curTimeline);
                lastSegmentVisible = isVisibleToday;

                //add to timeline
                curTimeline.querySelector('.line').appendChild(curLineSegment);
            }
        }
            
    }

    ifPlanetViewable(planet, day, weatherInfo)
    {
        /*
        Honestly, I hate this API because I had to figure out what in the 
        world this number means and even then, I'm missing so much here that
        I should be checking.  For example, just because it's in the sky doesn't mean it's
        visible because of light pollution.
        I'm leaving it like this for now, but next time, REVISE THIS, AND/OR USE A NEW API
        BECAUSE THIS ISN'T GOOD.  ALTITUDE ONLY MATTERS AT WHATEVER RANDOM TIME IT DECIDES TO
        USE AND I'M PRETTY SURE IT ISN'T ALWAYS ACCURATE.

        Not to mention that it just is a headache to navigate.  Thankfully, I found some
        useful data, but not that much I could easily use.
        */

        if (planet.cells[day].position.horizontal.altitude.degrees > 10)
        {
            return true;
        }
        else //less than 10 degrees above the horizon, basically below the horizon and unviewable
        {
            return false;
        }
    }

    getDaysViewable(planet, weatherInfo)
    {
        let cells = planet.cells;
        let output = Array(cells.length);

        for (let i = 0; i < cells.length; ++i)
        {
            output[i] = this.ifPlanetViewable(planet, i, weatherInfo);
        }

        return output;
    }
}