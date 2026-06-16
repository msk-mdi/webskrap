// Copy-to-clipboard for the hero install chip.
document.addEventListener("click", function (event) {
  var btn = event.target.closest("[data-ws-copy]");
  if (!btn) return;
  var text = btn.getAttribute("data-ws-copy");
  var done = function () {
    btn.classList.add("is-copied");
    setTimeout(function () {
      btn.classList.remove("is-copied");
    }, 1600);
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(done);
  } else {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
    done();
  }
});
