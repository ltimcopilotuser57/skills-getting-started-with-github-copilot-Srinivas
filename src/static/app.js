document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and dropdown
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const spotsLeft = details.max_participants - details.participants.length;

        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        let participantsHtml = "";
        if (details.participants && details.participants.length) {
          participantsHtml = details.participants.map(email => `
            <li style="list-style-type:none; display:flex; align-items:center;">
              <span>${email}</span>
              <button class="delete-participant" data-activity="${name}" data-email="${email}" title="Remove" style="margin-left:8px; background:none; border:none; cursor:pointer; color:#c00; font-size:1.2em;">&#128465;</button>
            </li>
          `).join("");
        } else {
          participantsHtml = `<li style="list-style-type:none;"><em>No participants yet</em></li>`;
        }
        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Participants</h5>
            <ul class="participants-list" style="padding-left:0;">
              ${participantsHtml}
            </ul>
          </div>
        `;
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities list to show updated participants
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Delegate click event for delete buttons
  document.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-participant")) {
      const activity = event.target.getAttribute("data-activity");
      const email = event.target.getAttribute("data-email");
      try {
        const response = await fetch(`/activities/${encodeURIComponent(activity)}/unregister`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email })
        });
        if (response.ok) {
          // Refresh activities list
          await fetchActivities();
        } else {
          alert("Failed to remove participant.");
        }
      } catch (error) {
        alert("Failed to remove participant.");
        console.error("Error removing participant:", error);
      }
    }
  });

  // Initial load
  fetchActivities();
});
