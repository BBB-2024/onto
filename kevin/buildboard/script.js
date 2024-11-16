// Function to fetch tasks from the API
async function fetchTasks(teamCode) {
  try {
    const response = await fetch("http://bitkozpont.mik.uni-pannon.hu/2024/gettasks.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: "all", teamcode: teamCode }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch tasks");
    }

    const data = await response.json();
    if (data.status === "success") {
      return data.data.task_list;
    } else {
      alert(data.message || "Unknown error occurred.");
      return [];
    }
  } catch (error) {
    console.error("Error fetching tasks:", error);
    alert("Failed to load tasks. Please try again.");
    return [];
  }
}

// Function to render tasks in their respective categories
function renderTasks(tasks) {
  const openTasks = document.getElementById("openTasks");
  const completedTasks = document.getElementById("completedTasks");
  const lockedTasks = document.getElementById("lockedTasks");

  // Clear existing tasks
  openTasks.innerHTML = "";
  completedTasks.innerHTML = "";
  lockedTasks.innerHTML = "";

  tasks.forEach((task) => {
    const listItem = document.createElement("li");
    listItem.className = "list-group-item";
    listItem.textContent = `Task ID: ${task.ID} - Points: ${task.points}`;

    switch (task.state) {
      case "OPEN":
        openTasks.appendChild(listItem);
        break;
      case "COMPLETED":
        completedTasks.appendChild(listItem);
        break;
      case "LOCKED":
        lockedTasks.appendChild(listItem);
        break;
    }
  });
}

async function getter(){
  const teamCode = document.getElementById("teamcode").value.trim();

  if (!teamCode) {
    alert("Please enter a valid team code.");
    return;
  }
  console.log("Getting tasks, teamcode:",teamCode);
  const tasks = await fetchTasks(teamCode);
  renderTasks(tasks);
  setTimeout(getter,1000);
}

// Event listener for the Load Tasks button
document.getElementById("loadTasks").addEventListener("click", async () => {
  getter();
});
  