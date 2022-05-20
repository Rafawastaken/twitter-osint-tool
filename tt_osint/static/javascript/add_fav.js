function add_fav(id) {
  fetch("/add-favorite", {
    method: "POST",
    body: JSON.stringify({ id: id }),
  }).then((_res) => {
    window.location.reload();
  });
}
