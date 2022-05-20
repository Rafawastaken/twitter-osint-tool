function delete_entry(entry_id) {
  fetch("/delete-entry", {
    method: "POST",
    body: JSON.stringify({ entry_id: entry_id }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
