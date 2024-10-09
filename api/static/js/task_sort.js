function sortTasks() {
  var sortBy = document.getElementById('sort-by').value;
  var url = window.location.pathname + '?sort_by=' + sortBy;  // Build the URL using the current path
  window.location.href = url;
}