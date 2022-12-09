document.querySelector('.btn_create').addEventListener('click', function(e) {
    var modal_container = document.querySelector(
      ".create_modal .modal_container"
    );
    modal_container.style.display = "block";
    modal_container.style.width = "100%";
    modal_container.style.height = "100%";
});