function getTimeFromServer() {
    try {
        const response = fetch('/get-time');
        const data = response.json();
        return new Date(data.time);
    } catch (error) {
        console.error('Error fetching time from server:', error);
        return null;
    }
}

function time_format(timestamp) {

        // Use serverTime instead of new Date() for current time
        let currentDt = getTimeFromServer();

        // Convert the timestamp string to a Date object in UTC
        let timestampDt = new Date(timestamp);

        // Calculate the difference between the timestamps in milliseconds
        let timeDifference = currentDt - timestampDt;
        let formattedTime = "";
        if (timeDifference <= 60000) {
            formattedTime =  "just now";
        } else if (timeDifference < 360000) {
            let minutes = Math.floor(timeDifference / 60000);
            formattedTime = minutes + " minute" + (minutes > 1 ? "s" : "") + " ago";
        } else if (timeDifference < 8640000) {
            let hours = Math.floor(timeDifference / 3600000);
            formattedTime =  hours + " hour" + (hours > 1 ? "s" : "") + " ago";
        } else if (currentDt.getDate() === timestampDt.getDate()) {
            formattedTime =  "today";
        } else if (currentDt.getDate() - timestampDt.getDate() === 1) {
            formattedTime =  "yesterday";
        } else if (timeDifference < 604800000) {
            let days = Math.floor(timeDifference / 86400000);
            formattedTime = days + " day" + (days > 1 ? "s" : "") + " ago";
        } else if (timeDifference < 2592000000) { // 30 days
            let weeks = Math.floor(timeDifference / 604800000);
            formattedTime = weeks + " week" + (weeks > 1 ? "s" : "") + " ago";
        } else {
            // Return the full timestamp if older than 30 days
            formattedTime = timestampDt.getFullYear() + "-" + (timestampDt.getMonth() + 1) + "-" + timestampDt.getDate();
        }
    return formattedTime
}


    let protocol = "wss"
    if (location.hostname === "localhost"){
        protocol = "ws"
    }
    console.log(location.hostname);
    console.log(protocol);
    let socket = io.connect(protocol + '://' + document.domain + ':' + location.port);

    // Function to create a formatted chat message
    function add_new_message(message) {
        let messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message');
        messageDiv.style.color = message.user_colour;


        let userIconDiv = document.createElement('div');
        userIconDiv.classList.add('user-icon');
        let userIconImg = document.createElement('img');

        userIconImg.src = "/static/images/avatar.png"; // You can replace this with the actual user icon URL
        userIconDiv.appendChild(userIconImg);

        let messageContentDiv = document.createElement('div');
        messageContentDiv.classList.add('chat-message-content');

        let messageTextDiv = document.createElement('div');
        messageTextDiv.classList.add('chat-message-text');
        messageTextDiv.textContent = message.text;

        let timestampDiv = document.createElement('div');
        timestampDiv.classList.add('chat-message-timestamp');
        timestampDiv.textContent = time_format(message.timestamp)


        messageContentDiv.appendChild(messageTextDiv);
        messageContentDiv.appendChild(timestampDiv);

        messageDiv.appendChild(userIconDiv);
        messageDiv.appendChild(messageContentDiv);

        return messageDiv;
    }

    // Event listener for receiving messages
    socket.on('message', function(data) {
        let chatContainer = document.getElementById('chat-container');
        let messageElement = add_new_message(data);
        chatContainer.appendChild(messageElement);
    });

    // Event listener for sending messages
    document.getElementById('message-form').onsubmit = function(e) {
        e.preventDefault();
        let messageInput = document.getElementById('message-input');
        socket.emit('message', { text: messageInput.value });
        messageInput.value = '';
    };