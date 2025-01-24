

// Sample turf data
const turfs = [
    {
      name: "Green Valley",
      location: "Downtown",
      price: "$50/hour",
      image: "https://via.placeholder.com/300x200.png?text=Green+Valley",
    },
    {
      name: "Sunset Fields",
      location: "Westside",
      price: "$45/hour",
      image: "https://via.placeholder.com/300x200.png?text=Sunset+Fields",
    },
    {
      name: "Riverside Pitch",
      location: "Eastside",
      price: "$55/hour",
      image: "https://via.placeholder.com/300x200.png?text=Riverside+Pitch",
    },
    {
      name: "Central Park",
      location: "Midtown",
      price: "$60/hour",
      image: "https://via.placeholder.com/300x200.png?text=Central+Park",
    },
  ]
  
  // Function to create turf cards
  function createTurfCard(turf) {
    const card = document.createElement("div")
    card.className = "turf-card"
    card.innerHTML = `
          <img src="${turf.image}" alt="${turf.name}" class="turf-image">
          <div class="turf-info">
              <h2 class="turf-name">${turf.name}</h2>
              <p class="turf-location">${turf.location}</p>
              <p class="turf-price">${turf.price}</p>
              <a href="#" class="book-btn">Book Now</a>
          </div>
      `
    return card
  }
  
  // Populate turf grid
  const turfGrid = document.getElementById("turfGrid")
  turfs.forEach((turf) => {
    turfGrid.appendChild(createTurfCard(turf))
  })
  
  // Login/Logout functionality
  const loginBtn = document.getElementById("loginBtn")
  const logoutBtn = document.getElementById("logoutBtn")
  const profileIcon = document.querySelector(".profile-icon")
  
  let isLoggedIn = false
  
  function updateAuthState() {
    if (isLoggedIn) {
      loginBtn.style.display = "none"
      logoutBtn.style.display = "inline-block"
      profileIcon.style.display = "inline-block"
    } else {
      loginBtn.style.display = "inline-block"
      logoutBtn.style.display = "none"
      profileIcon.style.display = "none"
    }
  }
  
  loginBtn.addEventListener("click", () => {
    isLoggedIn = true
    updateAuthState()
  })
  
  logoutBtn.addEventListener("click", () => {
    isLoggedIn = false
    updateAuthState()
  })
  
  // Initial auth state
  updateAuthState()
  
  