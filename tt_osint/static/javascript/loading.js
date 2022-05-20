const btn = document.getElementById("start-btn");
const container = document.getElementById("loading-info");
const input_box = document.getElementById("input-text");

btn.addEventListener("click", function (e) {
  container.style.display = "inherit";
  btn.value = "Scraping";
  btn.classList.add("Disabled"); // ! Not working
});
