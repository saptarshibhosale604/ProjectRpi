
let songQueue = [];
let currentIndex = 0;
let audioPlayer = document.getElementById("audio-player");
let audioSource = document.getElementById("audio-source");
let songTitle = document.getElementById("song-title");
let songInfo = document.getElementById("song-info");
let previousSongsList = document.getElementById("previous-songs");
let nextSongsList = document.getElementById("next-songs");

async function loadSongs() {
	const response = await fetch('/songs');
	songQueue = await response.json();
	
	console.log("songqueue01:",songQueue);
	// Sort by language, then genre, then singer, then filename
	//~ songQueue.sort((a, b) => {
		//~ return a.language.localeCompare(b.language) ||
		//~ a.genre.localeCompare(b.genre) ||
		//~ a.singer.localeCompare(b.singer) ||
		//~ a.filename.localeCompare(b.filename);
	//~ });
	//~ console.log("songqueue02:",songQueue);
	if (songQueue.length > 0) {
		loadSong(0);
	}
}

// Function to shuffle the song queue
function shuffleQueue() {
	console.log("song shuffling");
    for (let i = songQueue.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [songQueue[i], songQueue[j]] = [songQueue[j], songQueue[i]]; // Swap elements
    }
	console.log("songqueue03:",songQueue);
    if (songQueue.length > 0) {
        loadSong(0); // Start playing the first song in the shuffled queue
    }
}


// Function to shuffle within each language group
function shuffleQueueByLanguage() {
    // Group songs by language
    let languageGroups = {};
    songQueue.forEach(song => {
        if (!languageGroups[song.language]) {
            languageGroups[song.language] = [];
        }
        languageGroups[song.language].push(song);
    });

    // Shuffle songs within each language group
    let shuffledQueue = [];
    Object.keys(languageGroups).sort().forEach(language => {
        let songs = languageGroups[language];

        // Fisher-Yates shuffle for the group
        for (let i = songs.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [songs[i], songs[j]] = [songs[j], songs[i]];
        }

        shuffledQueue = shuffledQueue.concat(songs);
    });

    songQueue = shuffledQueue;
	console.log("songqueue04:",songQueue);
    if (songQueue.length > 0) {
        loadSong(0); // Start playing the first song in the shuffled queue
    }
}

function loadSong(index) {
	currentIndex = index;
	let song = songQueue[currentIndex];
	audioSource.src = "/play/" + song.filename;
	audioPlayer.load();
	songTitle.innerText = song.title;
	songInfo.innerText = `${song.singer} - ${song.genre} - ${song.language}`;
	audioPlayer.play();
	updateSongList();
}

function updateSongList() {
previousSongsList.innerHTML = "";
nextSongsList.innerHTML = "";

for (let i = Math.max(0, currentIndex - 2); i < currentIndex; i++) {
let li = document.createElement("li");
li.innerText = songQueue[i].title;
previousSongsList.appendChild(li);
}

for (let i = currentIndex + 1; i <= Math.min(songQueue.length - 1, currentIndex + 2); i++) {
let li = document.createElement("li");
li.innerText = songQueue[i].title;
nextSongsList.appendChild(li);
}
}

function togglePlayPause() {
	if (audioPlayer.paused) {
	audioPlayer.play();
	} else {
	audioPlayer.pause();
	}
}

function nextSong() {
if (currentIndex < songQueue.length - 1) {
loadSong(currentIndex + 1);
}
}

function previousSong() {
if (currentIndex > 0) {
loadSong(currentIndex - 1);
}
}

// Auto-play next song when the current song ends
audioPlayer.addEventListener("ended", () => {
if (currentIndex < songQueue.length - 1) {
nextSong();
}
});

window.onload = loadSongs;


function fetchMode() {
    fetch('/get_mode')
        .then(response => response.json())
        .then(data => {
                document.getElementById("mode").innerText = data.mode;
                if (data.mode === "pause") {
                    	togglePlayPause();
			//update_mode_file();
			console.log("mode detected: pause");
                }
                else if (data.mode === "play") {
                    	togglePlayPause();
			console.log("mode detected: play");
                }
		else if (data.mode === "next") {
                    	nextSong();
			console.log("mode detected: next");
                }
		else if (data.mode === "previous") {
			previousSong()
			console.log("mode detected: previous");
                }
		
        })
        .catch(error => console.error("Error fetching mode:", error));
}

// Check for mode updates every 2 seconds
setInterval(fetchMode, 5000);
