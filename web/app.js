const areas = ["work", "study", "physical", "energy"];
let activeArea = "general";
let logs = createDemoLogs();

const grid = document.getElementById("contributionGrid");
const monthLabels = document.getElementById("monthLabels");
const activeDays = document.getElementById("activeDays");
const currentStreak = document.getElementById("currentStreak");

function startOfGraph(year) {
  const first = new Date(year, 0, 1);
  const day = (first.getDay() + 6) % 7;
  const start = new Date(first);
  start.setDate(first.getDate() - day);
  return start;
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function scoreForDay(day, area) {
  if (!day) return null;
  if (area !== "general") return day[area] ?? null;
  const values = areas.map((key) => day[key]).filter((value) => Number.isFinite(value));
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function levelForScore(score) {
  if (score === null || score <= 0) return 0;
  if (score <= 1) return 1;
  if (score <= 2) return 2;
  if (score <= 3) return 3;
  return 4;
}

function renderMonths(year) {
  monthLabels.innerHTML = "";
  const spacer = document.createElement("span");
  monthLabels.appendChild(spacer);
  const start = startOfGraph(year);
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  let lastMonth = -1;

  for (let week = 0; week < 53; week++) {
    const date = new Date(start);
    date.setDate(start.getDate() + week * 7);
    const label = document.createElement("span");
    if (date.getFullYear() === year && date.getMonth() !== lastMonth) {
      label.textContent = monthNames[date.getMonth()];
      lastMonth = date.getMonth();
    }
    monthLabels.appendChild(label);
  }
}

function renderGraph() {
  const year = new Date().getFullYear();
  const start = startOfGraph(year);
  renderMonths(year);
  grid.innerHTML = "";

  let active = 0;
  let streak = 0;

  for (let index = 0; index < 53 * 7; index++) {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    const key = isoDate(date);
    const score = date.getFullYear() === year ? scoreForDay(logs[key], activeArea) : null;
    const level = levelForScore(score);
    const cell = document.createElement("span");
    cell.className = `day-cell level-${level}`;
    cell.title = `${key}: ${score === null ? "No data" : Math.round((score / 4) * 100) + "%"}`;
    grid.appendChild(cell);
    if (score && score > 0) active++;
  }

  for (let day = new Date(); ; day.setDate(day.getDate() - 1)) {
    const score = scoreForDay(logs[isoDate(day)], activeArea);
    if (!score || score <= 0) break;
    streak++;
  }

  activeDays.textContent = active;
  currentStreak.textContent = streak;
}

function createDemoLogs() {
  const data = {};
  const today = new Date();
  for (let i = 0; i < 120; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const chance = Math.random();
    if (chance < 0.24) continue;
    data[isoDate(date)] = {
      work: Math.floor(Math.random() * 5),
      study: Math.floor(Math.random() * 5),
      physical: Math.floor(Math.random() * 5),
      energy: Math.floor(Math.random() * 5),
    };
  }
  return data;
}

document.querySelectorAll("input[type='range']").forEach((input) => {
  input.addEventListener("input", () => {
    input.nextElementSibling.value = input.value;
  });
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    activeArea = tab.dataset.area;
    renderGraph();
  });
});

document.getElementById("habitForm").addEventListener("submit", (event) => {
  event.preventDefault();
  logs[isoDate(new Date())] = {
    work: Number(document.getElementById("work").value),
    study: Number(document.getElementById("study").value),
    physical: Number(document.getElementById("physical").value),
    energy: Number(document.getElementById("energy").value),
  };
  renderGraph();
});

renderGraph();
