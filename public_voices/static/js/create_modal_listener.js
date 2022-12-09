document.querySelector('.btn_create').addEventListener('click', function(e) {
    var modal_container = document.querySelector(
      ".create_modal .modal_container"
    );
    modal_container.style.display = "block";
    modal_container.style.width = "100%";
    modal_container.style.height = "100%";
});

document
  .querySelector(".modal_container")
  .addEventListener("click", function (e) {
    if (e.target.closest(".modal_bottom")) return;

    var modal_container = document.querySelector(
      ".create_modal .modal_container"
    );
    modal_container.style.display = "none";
    modal_container.style.width = "0";
    modal_container.style.height = "0";
  });

document.querySelector('.btn_submit').addEventListener('click', function(e) {
    var textareas = document.querySelectorAll(
      ".create_modal textarea"
    );

    for (var textarea of textareas) {
      if (textarea.value.trim() == "") {
          alert("Please fill out all fields.");
          e.preventDefault();
          return;
      }
    }
})