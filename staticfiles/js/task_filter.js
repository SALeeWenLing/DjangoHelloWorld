function filterTasks() {
    var checkboxes = document.querySelectorAll('.filter-checkbox:checked');
    var selectedTags = Array.from(checkboxes).map(cb => cb.value);
    var url = window.location.pathname + '?filter_by=' + selectedTags.join(',');
    window.location.href = url;
}

