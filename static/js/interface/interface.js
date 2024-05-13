
window.addEventListener("load", async e => {
    // Define global variables to hold server time and interval ID
    let serverTime;
    let intervalId;
    let hourly_event;

    // Define a function to fetch game time from the server
    async function fetchGameTime() {
        console.log("calling the server again");
        try {
            const response = await fetch('/game-time');
            const data = await response.json();
            serverTime = new Date(data.time);
        } catch (error) {
            console.error('Error fetching game time:', error);
            document.getElementById('game_time').innerHTML = 'Error fetching game time';
        }
    }


    // Define a function to update the game time displayed on the webpage
    function updateGameTime() {
        // Add one second to the current displayed time
        serverTime.setSeconds(serverTime.getSeconds() + 1);

        // Extract hours, minutes, and seconds from the serverTime Date object
        const hours = serverTime.getHours().toString().padStart(2, '0');
        const minutes = serverTime.getMinutes().toString().padStart(2, '0');
        const seconds = serverTime.getSeconds().toString().padStart(2, '0');

        // Format the time in military format (24-hour format)
        const militaryTime = `${hours}:${minutes}:${seconds}`;

        document.getElementById('game_time').innerHTML = `
            <span class="font-weight-bold text-danger d-block d-sm-inline">GAME TIME :<span class="font-weight-bold text-info">${militaryTime}</span></span>
            <hr/>
            
        `;

    }

    // Fetch game time from the server initially
    await fetchGameTime();

    // Call updateGameTime every second
    intervalId = setInterval(() => {
        updateGameTime();

        // Check if 5 minutes have elapsed
        const elapsedTime = new Date() - serverTime;
        if (elapsedTime >= 5 * 60 * 100000) { // 5 minutes in milliseconds
            // clearInterval(intervalId); // Stop the current interval
            fetchGameTime(); // Fetch game time from the server again
        }
    }, 1000); // 1000 milliseconds = 1 second





async function fetch_hourly_event() {
    try {
        const response = await fetch('/game-hourly');
        const data = await response.json();
        hourly_event = data.event;
        console.log("Hourly event fetched successfully at", new Date());
        console.log('Hourly Event ', hourly_event);
        document.getElementById('hourly_event').innerHTML = `
        <span class="font-weight-bold text-danger d-block d-sm-inline"> HOURLY EVENT</span> : <span class="text-info"> ${hourly_event} </span>`
    } catch (error) {
        console.log("Error fetching hourly event", error);
    }
}

await fetch_hourly_event();

async function scheduleHourlyEvent() {
    try {
        const timeResponse = await fetch('/game-time');
        const timeData = await timeResponse.json();
        const currentTime = new Date(timeData.time);
        const millisecondsUntilNextHour = (60 - currentTime.getMinutes() - 1) * 60 * 1000 + (60 - currentTime.getSeconds()) * 1000;

        setTimeout(async function() {
            await fetch_hourly_event(); // Call the function to fetch the hourly event
            // Schedule the function to be called every hour afterwards
            setInterval(fetch_hourly_event, 60 * 60 * 1000);
        }, millisecondsUntilNextHour);
    } catch (error) {
        console.log("Error fetching game time", error);
    }
}

// Start scheduling the hourly event
await scheduleHourlyEvent();

});
